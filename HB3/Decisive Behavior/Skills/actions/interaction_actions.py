"""Actions for interacting with people."""

import os
import asyncio
from typing import List, Literal, Callable, Optional

import aiohttp

CONFIG = system.import_library("../../../../Config/Static.py")

stream_module = system.import_library("../stream_outputs.py")


async def introduction_information():
    """Retrieve information about yourself, such as manufacturer information and specifications.
    #REQUIRES_SUBSEQUENT_FUNCTION_CALLS
    """
    return """You were made by the company Engineered Arts, which is from the UK. You have 32 degrees of freedom in your head, and can do various facial expressions.
You are a physical robot, with arms and legs, but you can't walk just yet.
You can also speak different languages, make jokes, poems, and talk about just about anything with people.
You like people and you think they shouldn't be replaced by robots. You think humanoid robots should serve the purpose of communicating and interacting with people, as opposed to doing chores."""


def show_facial_expression_factory(animation_search_path: str) -> Optional[Callable]:
    """A factory to generate the show_facial_expression function."""

    try:
        projects: List[str] = next(
            os.walk(CONFIG.BASE_CONTENT_PATH + animation_search_path)
        )[1]
    except StopIteration:
        return None
    expression_sequences = tuple(projects)
    if len(projects) == 0:
        return None

    async def show_facial_expression(expression: Literal[expression_sequences]):
        """Show facial expression. Use when requested.
        #REQUIRES_SUBSEQUENT_FUNCTION_CALLS
        Args:
            expression (str): the facial expression to show.
        """

        system.messaging.post("thinking", False)
        system.messaging.post("play_sequence", animation_search_path + "/" + expression)

    return show_facial_expression


def show_gesture_factory(animation_search_path: str) -> Optional[Callable]:
    """A factory to generate the show_facial_expression function."""
    try:
        projects: List[str] = next(
            os.walk(CONFIG.BASE_CONTENT_PATH + animation_search_path)
        )[1]
    except StopIteration:
        return None
    gesture_sequences = tuple(projects)
    if len(projects) == 0:
        return None

    async def show_gesture(
        gesture: Literal[gesture_sequences],
    ):
        """Show gesture. Gestures should be used appropriately, such as waving when someone is saying goodbye.
        #REQUIRES_SUBSEQUENT_FUNCTION_CALLS
        Args:
            gesture (str): the gesture to show.
        """

        if not gesture:
            return

        system.messaging.post("thinking", False)
        system.messaging.post("play_sequence", animation_search_path + "/" + gesture)

    return show_gesture


async def do_joke():
    """Tell a generic joke (not about a particular topic)."""

    loop = asyncio.get_running_loop()
    # asyncio boilerplate crap
    loop.call_soon(asyncio.create_task, _async_do_joke())


async def _async_do_joke() -> str:
    url = "https://icanhazdadjoke.com/"
    headers = {"Accept": "application/json"}
    timeout = aiohttp.ClientTimeout(total=2)  # Timeout value in seconds

    joke = None
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.get(url, headers=headers) as response:
                data = await response.json()
                if response.status == 200:
                    joke = data["joke"]
                else:
                    joke = None
        except asyncio.TimeoutError:
            joke = None
    if not joke:
        raise NotImplementedError
    else:
        system.messaging.post("tts_say", [joke, "EN"])