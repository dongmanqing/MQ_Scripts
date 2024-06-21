"""The default HB3 config.

To overwrite any values in here, create a file at "/Config/Robot/HB3.py", and put the appropriate values in.

e.g. saving the following to "/Config/Robot/FACE_REC_SERVER_ADDRESS.py" will overwrite the value for FACE_REC_SERVER_ADDRESS

```
FACE_REC_SERVER_ADDRESS = "0.0.0.0:0000"
```
"""

from enum import Enum
from typing import Optional


class ROBOT_HEAD_TYPES:
    GEN1 = 1
    GEN2 = 2


class ROBOT_TYPES:
    AMECA = 1
    AMECA_DESKTOP = 2


class LED_TYPES(Enum):
    ADDRESSABLE_LEDs = 1
    NON_ADDRESSABLE_LEDs = 2


ROBOT_HEAD_TYPE = ROBOT_HEAD_TYPES.GEN2
ROBOT_TYPE = ROBOT_TYPES.AMECA
LED_TYPE: LED_TYPES = LED_TYPES.ADDRESSABLE_LEDs

NEUTRAL_BODY_POSE: str = "HB3_Body_Neutral"
NEUTRAL_FACE_POSE: str = "EXP_neutral"

# Face recognition address. Set to None to disable face rec
FACE_REC_SERVER_ADDRESS: Optional[str] = None
PROFILES_SERVER_ADDRESS: Optional[str] = None

VQA_SERVER_ADDRESS: Optional[str] = None

FLAPPY_SILENCE_THRESHOLD = 0.1  # peak level < than this value will disable flappy

FLAPPY_GAIN: float = 30
ARM_MOVE_GAIN: float = FLAPPY_GAIN / 3
