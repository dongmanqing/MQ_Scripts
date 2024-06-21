import json
from enum import Enum
from typing import Dict, List, Optional
from collections import namedtuple

Profile = namedtuple("Profile", "prompt,robot_name,openai_params")
"""The default CHAT config.

To overwrite any values in here, create a file at "/Config/Robot/Chat.py", and put the appropriate values in.

e.g. saving the following to "/Config/Robot/Chat.py" will overwrite the value for ROBOT_NAME

```
ROBOT_NAME = "NOT AMECA"
```
"""

AMECA_DEFAULT_MODULE = system.import_library(
    "./Chat Personalities/Ameca_Core_Template.py"
)
AMECA_INTERVIEW_MODULE = system.import_library(
    "./Chat Personalities/Ameca_Interview_Template.py"
)
AMECA_ALT1_MODULE = system.import_library("./Chat Personalities/Ameca_Alt1.py")
AMECA_ALT1_DESKTOP_MODULE = system.import_library(
    "./Chat Personalities/Ameca_Alt1_Desktop.py"
)

PERSONALITIES = {
    "Ameca_Core_Template": AMECA_DEFAULT_MODULE,
    "Ameca_Interview_Template": AMECA_INTERVIEW_MODULE,
    "Ameca_Alt1": AMECA_ALT1_MODULE,
    "Ameca_Alt1_Desktop": AMECA_ALT1_DESKTOP_MODULE,
}

NORMAL_MODE_HISTORY_LIMIT = 30


def make_profile(profile_script):
    return Profile(
        prompt=profile_script.PROMPT,
        robot_name=profile_script.ROBOT_NAME,
        openai_params={
            "frequency_penalty": getattr(profile_script, "FREQUENCY_PENALTY", 1),
            "max_tokens": getattr(profile_script, "MAX_TOKENS", 500),
            "n": getattr(profile_script, "N", 1),
            "presence_penalty": getattr(profile_script, "PRESENCE_PENALTY", 0.2),
            "stop": getattr(profile_script, "STOP", []),
            "temperature": getattr(profile_script, "TEMPERATURE", 0.8),
            "top_p": getattr(profile_script, "TOP_P", 1),
        },
    )


class CHAT_SYSTEM_TYPE(Enum):
    RULES_BASED_CHATBOT = 0
    CHAT_FUNCTION_CALL = 1


CHAT_PROFILE_NAME: str = "Ameca_Alt1"

CHAT_SYSTEM: CHAT_SYSTEM_TYPE = CHAT_SYSTEM_TYPE.CHAT_FUNCTION_CALL

GPT_LOGGING: bool = (
    False  # Enable to log what is sent to and received from openai gpt models
)

RULES_BASED_CHATBOT_URL: Optional[str] = None

USE_MULTI_LANG: bool = True

LOADED_PERSONALITY_PROFILES: Dict[str, Profile] = {
    personality_id: make_profile(personality_config)
    for personality_id, personality_config in PERSONALITIES.items()
}


# NOTE: This doesn't work with layered configs but layered configs don't work right now anyways so can rijig later
LOADED_PROFILE: Profile = LOADED_PERSONALITY_PROFILES[CHAT_PROFILE_NAME]
PERSONALITY: str = LOADED_PROFILE.prompt
ROBOT_NAME: str = LOADED_PROFILE.robot_name

SPEAKER_MAP: dict[str, str] = {
    "EN": "Amy",
    "FR": "Gabrielle",
    "DE": "Vicki",
    "ZH": "Zhiyu",  # Is there a reason we need this, since it is duplicated by CMN-CN for mandarin
    "CY": "Gwyneth",
    "PL": "Ola",
    "ES": "Lupe",
    "RU": "Tatyana",
    "JA": "Mizuki",
    "KO": "Seoyeon",
    "RO": "Carmen",
    "NB": "Ida",
    "IT": "Bianca",
    "PT": "Inês",
    "BR": "Vitória",
    "ARB": "Zeina",
    "IT": "Bianca",
    "YUE-CN": "Hiujin",
    "CMN-CN": "Zhiyu",
}


DISABLE_ASR_WHILE_SPEAKING: bool = False

MODES: List[str] = ["sleep", "normal", "diagnostics"]
