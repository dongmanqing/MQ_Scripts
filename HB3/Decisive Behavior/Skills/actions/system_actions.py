"""System level actions."""
import asyncio


async def wait_for(seconds: float):
    """Let time pass for a specified amount of time
    #REQUIRES_SUBSEQUENT_FUNCTION_CALLS
    Args:
        seconds: number of seconds to wait for
    """
    await asyncio.sleep(seconds)
    return f"Waited for {seconds} seconds."


async def system_shut_down():
    """Shut down."""
    system.messaging.post("tts_say", ["System Shut Down", "EN"])


async def turn_volume_up():
    """Turn up your volume.
    #REQUIRES_SUBSEQUENT_FUNCTION_CALLS

    """
    system.messaging.post("change_speaker_volume", 0.1)
    return "increased speaker volume by 10%"


async def turn_volume_down():
    """Turn down your volume.
    #REQUIRES_SUBSEQUENT_FUNCTION_CALLS

    """
    system.messaging.post("change_speaker_volume", -0.1)
    return "reduced speaker volume by 10%"


async def change_head_colour(colour: list[float]):
    """Change the colour of your head.

    You can only change to a single rgb value at a time. If you want to change it to another colour after you will get a chance to call this function again.

    #REQUIRES_SUBSEQUENT_FUNCTION_CALLS

    Args:
        colour: the colour to change your head to. This MUST be in the format (r, g, b) where r, g, b represent the colour intensities for red, green, blue. Each value MUST be between 0 and 1, with 0 indicating 0 intensity and 1 indicating full intensity of that colour.
    """
    system.messaging.post("set_led", tuple(colour))
    return f"Set LED Colors to {colour}"


async def sleep_mode():
    """Go into sleep mode.

    Stop talking, be quiet, stop listening, go to sleep.
    """
    system.messaging.post("mode_change", "sleep")


async def normal_mode():
    """Go into talking / normal mode.

    Leave sleep mode, leave diagnostics mode, start talking, start listening.
    """
    system.messaging.post("mode_change", "normal")


async def stop_talking():
    """Stop talking when the robot has been interrupted."""
    system.messaging.post("tts_stop", None)


async def diagnostics_mode():
    """Go into diagnostics mode."""
    system.messaging.post("mode_change", "diagnostics")


async def drawing_mode():
    """Go into drawing mode."""
    system.messaging.post("mode_change", "drawing")