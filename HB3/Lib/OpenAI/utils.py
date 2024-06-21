import json
import functools

import openai
from tritium import log

client = system.import_library("./setup.py").CLIENT


def try_n_times(func):
    @functools.wraps(func)
    async def _wrapper(max_tries=2, *args, **kwargs):
        if client is None:
            raise Exception(
                "Attempt to use a GPT function but the OpenAI key has not been set."
            )
        for i in range(max_tries):
            if i > 0:
                log.warning("Retrying the OpenAI call...")
            try:
                return await func(*args, **kwargs)
            except (openai.APITimeoutError, openai.APIError) as e:
                log.warning(f"OpenAI Error: {e}")
            except Exception as e:
                log.warning(f"Unhandled error when running openai model: {e}")
                return None
        log.error("Max retry reached.")
        return None

    return _wrapper


def parse_tools_response(tool_calls):
    ret = []
    for tool in tool_calls:
        if not tool["type"] == "function":
            raise NotImplementedError("Only expect function tools")
        ret.append(
            {
                "name": tool["function"]["name"],
                "arguments": parse_function_call(tool["function"]["arguments"]),
            }
        )

    return


def parse_function_call(function_call: dict[str, str]):
    try:
        return {
            "name": function_call["name"],
            "arguments": json.loads(function_call["arguments"]),
        }
    except json.JSONDecodeError:
        log.warning(
            f"JSON Decode failed for function call arguments:\n {function_call['arguments']}. Trying with empty args instead."
        )
        return {"name": function_call["name"], "arguments": {}}