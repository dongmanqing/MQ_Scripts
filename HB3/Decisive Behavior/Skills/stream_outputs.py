import re
from typing import Any, List, Callable, Optional, Awaitable

CONFIG = system.import_library("../../../Config/Chat.py").CONFIG
SPEAKER_MAP = CONFIG["SPEAKER_MAP"]
ROBOT_NAME = CONFIG["ROBOT_NAME"]

LANG_CODE = system.import_library("./determine_tts_lang_code.py")
StreamOutput = Callable[[str, dict[str, Any]], Awaitable[Any]]


def remove_patterns(text: str, patterns: List[str]):
    for pattern in patterns:
        regexp = re.compile(pattern)
        text = re.sub(regexp, "", text)
    return text


def generate_string_cases(text: str) -> List[str]:
    cases = [text.capitalize(), text.lower(), text.upper()]
    return cases


# This does not handle number like "3.14" well
def separate_sentences(
    text: str, separators: List[str] = [r"\.", "!", r"\?"]
) -> List[str]:
    separators_pattern = "[^" + "".join(separators) + "]*[" + "".join(separators) + "]*"
    sentences = re.findall(separators_pattern, text)
    return [sentence.strip() for sentence in sentences if sentence.strip()]


async def dummyStream(msg: str, kwargs: dict[str, Any] = {}):
    pass


async def streamToDefaultTTS(msg: str, kwargs: dict[str, Any] = {}):
    robot_name_colon = [n + ":" for n in generate_string_cases(ROBOT_NAME)]
    filtered_msg: str = remove_patterns(msg, robot_name_colon)
    sentences: List[str] = separate_sentences(filtered_msg)
    print("SAYING: ", sentences)
    for s in sentences:
        system.messaging.post("tts_say", [s, "EN"])


async def streamToMultiLangTTS(msg: str, kwargs: dict[str, Any] = {}):
    robot_name_colon = [n + ":" for n in generate_string_cases(ROBOT_NAME)]
    filtered_msg: str = remove_patterns(msg, robot_name_colon)
    interaction = kwargs.get("interaction", None)
    lang_detected: Optional[str] = await LANG_CODE.determineLangCode(
        filtered_msg, interaction
    )
    if lang_detected not in SPEAKER_MAP:
        lang_detected = "EN"
    sentences: List[str] = separate_sentences(filtered_msg)
    print(f"lang_detected: {lang_detected}")
    print("SAYING: ", sentences)
    for s in sentences:
        system.messaging.post("tts_say", [s, lang_detected])