import json


def parse_tools_response(tool_calls):
    ret = []
    for tool in tool_calls:
        if not tool["type"] == "function":
            raise NotImplementedError("Only expect function tools")
        ret.append(parse_function_call(tool["function"]))
    return ret


def parse_function_call(function_call):
    try:
        args = json.loads(function_call["arguments"])
        return {"name": function_call["name"], "arguments": args}
    except json.JSONDecodeError:
        log.warning(
            f"JSON Decode failed for function call arguments:\n {function_call['arguments']}. Trying with empty args instead."
        )
        return {"name": function_call["name"], "arguments": {}}
