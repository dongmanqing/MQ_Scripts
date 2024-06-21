from collections import namedtuple

# ------- Do not touch this code --------#
get_layered_config = system.import_library("./utils.py").get_layered_config


# ----- Load in personalities ------#
# If you want to add another personality, you must add it in below as with the other personalities
AMECA_DEFAULT_MODULE = system.import_library(
    "./Default/Chat Personalities/Ameca_Default.py"
)
SAM_MODULE = system.import_library("./Default/Chat Personalities/SAM.py")
AMECA_ALT1_MODULE = system.import_library("./Default/Chat Personalities/Ameca_Alt1.py")
AMECA_ALT1_DESKTOP_MODULE = system.import_library(
    "./Default/Chat Personalities/Ameca_Alt1_Desktop.py"
)

ROBOT_AMECA_DEFAULT_MODULE = system.try_import_library(
    "./Robot/Chat Personalities/Ameca_Default.py"
)
ROBOT_SAM_MODULE = system.try_import_library("./Robot/Chat Personalities/SAM.py")
ROBOT_AMECA_ALT1_MODULE = system.try_import_library(
    "./Robot/Chat Personalities/Ameca_Alt1.py"
)
ROBOT_AMECA_ALT1_DESKTOP_MODULE = system.try_import_library(
    "./Robot/Chat Personalities/Ameca_Alt1_Desktop.py"
)

PERSONALITIES = {
    "Ameca_Default": get_layered_config(
        AMECA_DEFAULT_MODULE, ROBOT_AMECA_DEFAULT_MODULE
    ),
    "SAM": get_layered_config(SAM_MODULE, ROBOT_SAM_MODULE),
    "Ameca_Alt1": get_layered_config(AMECA_ALT1_MODULE, ROBOT_AMECA_ALT1_MODULE),
    "Ameca_Alt1_Desktop": get_layered_config(
        AMECA_ALT1_DESKTOP_MODULE, ROBOT_AMECA_ALT1_DESKTOP_MODULE
    ),
}


# ------- Do not touch this code --------#

CONFIG_MODULE = system.import_library("./Default/Chat.py")
ROBOT_CONFIG_MODULE = system.try_import_library("./Robot/Chat.py")

CONFIG = get_layered_config(CONFIG_MODULE, ROBOT_CONFIG_MODULE)

Profile = namedtuple("Profile", "prompt,robot_name,openai_params")
"""The default CHAT config.

To overwrite any values in here, create a file at "/Config/Robot/Chat.py", and put the appropriate values in.

e.g. saving the following to "/Config/Robot/Chat.py" will overwrite the value for ROBOT_NAME

```
ROBOT_NAME = "NOT AMECA"
```
"""


def make_profile(profile_script):
    return Profile(
        prompt=profile_script["PROMPT"],
        robot_name=profile_script["ROBOT_NAME"],
        openai_params={
            "frequency_penalty": profile_script.get("FREQUENCY_PENALTY", 1),
            "max_tokens": profile_script.get("MAX_TOKENS", 500),
            "n": profile_script.get("N", 1),
            "presence_penalty": profile_script.get("PRESENCE_PENALTY", 0.2),
            "stop": profile_script.get("STOP", []),
            "temperature": profile_script.get("TEMPERATURE", 0.8),
            "top_p": profile_script.get("TOP_P", 1),
        },
    )


LOADED_PERSONALITY_PROFILES: dict[str, Profile] = {
    personality_id: make_profile(personality_config)
    for personality_id, personality_config in PERSONALITIES.items()
}

CONFIG["LOADED_PROFILE"]: Profile = LOADED_PERSONALITY_PROFILES[
    CONFIG["CHAT_PROFILE_NAME"]
]
CONFIG["PERSONALITY"]: str = CONFIG["LOADED_PROFILE"].prompt
CONFIG["ROBOT_NAME"]: str = CONFIG["LOADED_PROFILE"].robot_name