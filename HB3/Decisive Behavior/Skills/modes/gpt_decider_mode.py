import re
import json
from abc import abstractmethod
from typing import Any, Dict, List, Callable, Optional
from inspect import signature

from tritium import log

gpt_model = system.import_library("../../../Lib/OpenAI/gpt_model.py")
OPENAI_UTILS_MOD = system.import_library("../../../Lib/OpenAI/utils.py")
parse_tools_response = OPENAI_UTILS_MOD.parse_tools_response
parse_function_call = OPENAI_UTILS_MOD.parse_function_call

CONFIG = system.import_library("../../../../Config/Chat.py").CONFIG

mode = system.import_library("./mode.py")
stream_module = system.import_library("../stream_outputs.py")


class GPTDeciderMode(mode.Mode):
    """A mode in which we use GPT to decide what to do."""

    ############## Required properties ###################

    @property
    @abstractmethod
    def DECISION_MODEL(self) -> gpt_model.GPTModel:
        """OpenAI model to use"""
        pass

    ############## Provided methods ###################
    async def on_message(self, channel: str, message: Any):
        """Called when a system message is recieved.

        Args:
            channel (str): the channel the message was sent on
            message (Any): the message content
        """
        if channel == "speech_recognized":
            system.messaging.post("thinking", True)
            await self.recursively_call_llm(message)
            system.messaging.post("thinking", False)
            print('config: ', CONFIG)

    async def try_call_function(
        self, function_call: dict[str, str]
    ) -> tuple[list[dict], bool]:
        """Try to call a function.

        Args:
            function_call: a dictionary with keys describing the function call.
              - "name" is the name of the function to be called
              - "arguments" is the set of kwargs to be passed to the function

        Returns:
            a list of new messages to add to future prompts
            true if more functions should be called after this one
        """
        print(function_call)
        function_name = function_call["name"]
        function_args = function_call["arguments"]
        if function_name in self.DECISION_MODEL.functions_map:
            function_info = self.DECISION_MODEL.functions_map[function_name]
            # Check the function call is valid
            function = function_info["function"]
            function_signature = signature(function)
            if any(
                [k not in function_signature.parameters for k in function_args.keys()]
            ) or any(
                [
                    k not in function_args
                    for k, v in function_signature.parameters.items()
                    if v.default is v.empty
                ]
            ):
                log.warning("INVALID ARGUMENTS for function call! Ignoring...")
                return {
                    "success": False,
                    "error": "INVALID ARGUMENTS for function call! Ignoring...",
                }, False

            try:
                result = await function(**function_args)
                result = {"success": True, "result": "" if not result else result}
            except Exception as e:
                log.warning(str(e))
                result = {"success": True, "error": str(e)}

            return result, function_info["requires_subsequent_function_calls"]
        else:
            log.warning("LLM returned unrecognized function! Ignoring...")
            return {
                "success": False,
                "error": "LLM returned unrecognized function! Ignoring...",
            }, False

    async def recursively_call_llm(
        self,
        message: str,
        past_call_messages: Optional[str] = None,
        output_stream: stream_module.StreamOutput = stream_module.streamToDefaultTTS,
    ):
        if past_call_messages:
            messages = past_call_messages
        else:
            messages = self.DECISION_MODEL.get_message_prompt()

        # print('recursive call llm!!! message: ', message)
        # print('decision model: ', self.DECISION_MODEL)
        # print('decision  model name: ', self.DECISION_MODEL.model)
        # print('mode name: ', self.MODE_NAME)

        if CONFIG["GPT_LOGGING"]:
            log.info("[GPT Call] - Messages:")
            for message in messages:
                log.info(message)

        # Wait for the decision model to run
        response_stream = await self.DECISION_MODEL(messages)
        print(f'response stream from decision model: {response_stream}\n ###')
        if response_stream is None:
            return

        async for response in response_stream:
            if CONFIG["GPT_LOGGING"]:
                log.info(f"[GPT Response] - {response}")

            if response.get("tool_calls", False):
                messages.append(response)
                should_call_again = False
                for function in parse_tools_response(response["tool_calls"]):
                    (
                        result,
                        function_should_call_again,
                    ) = await self.try_call_function(function)

                    messages.append(
                        {
                            "tool_call_id": function.id,
                            "role": "tool",
                            "name": function["name"],
                            "content": json.dumps(result),
                        }
                    )
                    should_call_again |= function_should_call_again
                if should_call_again:
                    await self.recursively_call_llm(None, messages, output_stream)
            elif response.get("function_call", False):
                # Need to pop the tool calls bit or openai with throw a wobbly
                response.pop("tool_calls")
                messages.append(response)

                (
                    result,
                    should_call_again,
                ) = await self.try_call_function(
                    parse_function_call(response["function_call"])
                )
                messages.append(
                    {
                        "role": "function",
                        "name": response["function_call"]["name"],
                        "content": json.dumps(result),
                    }
                )

                if should_call_again:
                    await self.recursively_call_llm(None, messages, output_stream)
            else:
                await output_stream(response["content"])
