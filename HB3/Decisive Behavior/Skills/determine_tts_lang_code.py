import re
from typing import List, Optional

CONFIG = system.import_library("../../../Config/Chat.py").CONFIG
SPEAKER_MAP = CONFIG["SPEAKER_MAP"]

gpt_functions = system.import_library("../../Lib/OpenAI/gpt_functions.py")
INTERACTION_HISTORY = system.import_library("../Knowledge/Interaction_History.py")


def find_matching_pattern(text: str, pattern_list: List[str]) -> Optional[str]:
    for pattern in pattern_list:
        match = re.search(r"\b" + pattern + r"\b", text)
        if match:
            return match.group()
    return None


async def determineLangCode(
    msg: str, interactions: Optional[INTERACTION_HISTORY.InteractionHistory] = None
) -> Optional[str]:
    system_msg: str = "You specialize in identifying languages."
    context: str = (
        f"""Context:
```
{interactions.to_text()}
```

"""
        if interactions
        else ""
    )

    user_prompt: str = f"""Based on the message and context provided, identify the language being spoken. Respond only with the appropriate language code from the following options: {list(SPEAKER_MAP.keys())}.

Message(Detect the language for this output message here):
\"{msg}\"

{context}"""

    chat_msg = [
        {
            "role": "system",
            "content": system_msg,
        },
        {"role": "user", "content": user_prompt},
    ]
    try:
        response = await gpt_functions.run_chat(
            model="gpt-4", messages=chat_msg, temperature=0.2
        )
        reply: str = response["content"]
        result = find_matching_pattern(reply, list(SPEAKER_MAP.keys()))
    except Exception as e:
        log.warning(f"determineLangCode Error: {e}\n")
        result = "EN"
    return result