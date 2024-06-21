"""
Actions which affect where the robot looks.
"""
from time import time as time_unix

from tritium.world import World
from tritium.world.geom import Vector2, Vector3

contributor = system.import_library("../../../Lib/contributor.py")

lookat_contributor = contributor.Contributor(
    "look",
    "user_request",
    reference_frame="Head",
)


async def look_up(say: str):
    """Look up.

    Args:
        say: the sentence to say after looking up.
    """
    system.messaging.post("tts_say", [say, "EN"])
    lookat_contributor.add(
        contributor.LookAtItem(
            identifier="user_request",
            position=Vector3([1, 0, 2]),
            sample_time=time_unix(),
        )
    )


async def look_down(say: str):
    """Look down.

    Args:
        say: the sentence to say after looking down.
    """
    system.messaging.post("tts_say", [say, "EN"])
    lookat_contributor.add(
        contributor.LookAtItem(
            identifier="user_request",
            position=Vector3([1, 0, -1]),
            sample_time=time_unix(),
        )
    )