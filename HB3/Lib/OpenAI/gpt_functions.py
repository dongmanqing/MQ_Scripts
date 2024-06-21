import asyncio
from typing import Callable, Optional, AsyncGenerator

client = system.import_library("./setup.py").CLIENT
gpt_functions = system.import_library("./utils.py")


@gpt_functions.try_n_times
async def run_chat(**kwargs) -> Optional[dict[str, any]]:
    """Run the chatcompletion mode, with no streaming."""
    resp = await client.chat.completions.create(**kwargs)
    return resp.choices[0].message.model_dump()


@gpt_functions.try_n_times
async def run_chat_streamed(
    eos_separators: list[str], **kwargs
) -> Optional[AsyncGenerator[dict[str, str], None]]:
    """Run the chatcompletion mode in streaming mode.

    Args:
        max_retries: Retry calling openai up to max_retries times. Defaults to 2.
        eos_separators: A list of strings which could be used to separate sentences. Defaults to [].

    Returns:
        A generator of chunks of the openai response, or None if there has been an error.
    """
    return await get_streamed_responses(eos_separators, **kwargs)


async def get_streamed_responses(
    eos_separators: list[str], **kwargs
) -> AsyncGenerator[dict[str, str], None]:
    """Get the responses from openai.

    Args:
        eos_separators: A list of strings which could be used to separate sentences. Defaults to [].
        **kwargs: kwargs to pass to the openai.chat.completions initialiser.

    Yields:
        Generator[dict[str, str], None, None]: the chunks of responses to the openai request.
    """
    stream = await client.chat.completions.create(stream=True, **kwargs)

    def apply_delta(
        buffer: dict,
        delta: any,
    ) -> dict:
        if delta.content:
            buffer["content"] += delta.content
        if delta.tool_calls:
            buffer["tool_calls"].extend(delta.tool_calls.model_dump())
        if delta.function_call:
            if buffer["function_call"]:
                if delta.function_call.arguments:
                    buffer["function_call"][
                        "arguments"
                    ] += delta.function_call.arguments
                if delta.function_call.name:
                    buffer["function_call"]["name"] = delta.function_call.name
            else:
                buffer["function_call"] = delta.function_call.model_dump()
        return buffer

    async def response_generator():
        buffer = {
            "content": "",
            "role": "assistant",
            "function_call": None,
            "tool_calls": [],
        }

        async for response_chunk in stream:
            choice = response_chunk.choices[0]

            if choice.delta:
                buffer = apply_delta(buffer, choice.delta)

            finish_reason = choice.finish_reason
            if finish_reason is not None:
                break
            # Check if we can start streaming tts. If we are doing a function call, ignore the streaming.
            elif buffer["content"] and not buffer["function_call"] and eos_separators:
                for eos_separator in eos_separators:
                    if (sep_index := buffer["content"].rfind(eos_separator)) != -1:
                        yield_content = buffer["content"][
                            : sep_index + len(eos_separator)
                        ].strip()
                        if yield_content:
                            yield {
                                "content": yield_content,
                                "role": "assistant",
                                "tool_calls": None,
                            }
                        buffer["content"] = buffer["content"][
                            sep_index + len(eos_separator) :
                        ]
        if buffer["content"] or buffer["tool_calls"] or buffer["function_call"]:
            yield buffer

    return response_generator()


@gpt_functions.try_n_times
async def run_completion(**kwargs) -> Optional[dict[str, any]]:
    """Run the completion mode, with no streaming."""
    resp = await client.completions.create(**kwargs)
    return resp.choices[0].model_dump()


gpt_tasks = set()


def run_background_gpt_task(
    use_completion=False,
    eos_separators: list[str] = None,
    full_cb: Optional[Callable[[str], any]] = None,
    partial_cb: Optional[Callable[[str], any]] = None,
    **kwargs,
):
    """Start a gpt model in the background to do a task.

    This function returns immediately, and runs the provided callbacks.

    Args:
        use_completion: If True, use completion mode instead of chat completion. Defaults to False.
        eos_separators: A list of strings which could be used to separate sentences. Defaults to None.
        full_cb: Called when the whole response has been received. Defaults to None.
        partial_cb: Called when a chunk of response has been received. Defaults to None.
        **kwargs: kwargs to pass to the openai.chat.completions initialiser.

    """

    async def run_task(
        eos_separators: Optional[list[str]] = None,
        full_cb: Optional[Callable[[str], any]] = None,
        partial_cb: Optional[Callable[[str], any]] = None,
        **kwargs,
    ):
        if partial_cb is None:
            # If we ony have a full callback - do not bother with streaming mode
            if use_completion:
                response = await run_completion(**kwargs)
                full_cb(response["text"])
            else:
                response = await run_chat(**kwargs)
                if response["tool_calls"]:
                    raise NotImplementedError(
                        "Have not yet implemented function calling through this function."
                    )
                else:
                    full_cb(response["content"])
        else:
            if use_completion:
                raise NotImplementedError(
                    "Have not implemented completion with streaming."
                )
            if eos_separators is None:
                raise ValueError(
                    "Cannot evaluate a stream without eos_separators being set. If a partial_cb is provided, eos_separators must not be None."
                )
            full_response = ""
            for response in run_chat_streamed(eos_separators, **kwargs):
                if response["tool_calls"]:
                    raise NotImplementedError(
                        "Have not yet implemented function calling through this function."
                    )
                else:
                    full_response += response["content"]
                    partial_cb(response["content"])
            if full_cb:
                full_cb(full_response)

    loop = asyncio.get_event_loop()

    # Update the face in the background
    coroutine = loop.create_task(
        run_task(
            eos_separators,
            full_cb,
            partial_cb,
            **kwargs,
        )
    )
    gpt_tasks.add(coroutine)
    coroutine.add_done_callback(lambda _: gpt_tasks.remove(coroutine))
