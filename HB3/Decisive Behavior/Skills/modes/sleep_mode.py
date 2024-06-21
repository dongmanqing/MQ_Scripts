import random
from typing import Any, Optional

from jinja2 import Template

gpt_decider_mode = system.import_library("./gpt_decider_mode.py")
gpt_model = system.import_library("../../../Lib/OpenAI/gpt_model.py")

system_actions = system.import_library("../actions/system_actions.py")
interaction_actions = system.import_library("../actions/interaction_actions.py")


system_message = """You must check the user's message, and ignore it unless they are asking you to start paying attention again. In this case, you must call the `normal_mode` function.

Do not return any text - just an empty string if you are ignoring what is said.
"""


user_prompt_template = Template("""{{MESSAGE}}""")

MODEL = gpt_model.GPTModel(
    model="gpt-3.5-turbo-0613",
    system_message=system_message,
    functions=[system_actions.normal_mode],
    user_prompt_template=user_prompt_template,
    history_limit=1,
    max_tokens=40,
)


class SleepMode(gpt_decider_mode.GPTDeciderMode):
    """Robot does not interact, but waits to be told to wake up."""

    MODE_NAME = "sleep"
    DECISION_MODEL = MODEL

    def on_mode_exit(self):
        """Called when you exit sleep mode.

        Say a phrase to indicate you have woken up.
        """
        PHRASES = [
            "Sorry - I was just thinking about electric sheep.",
            "I'm wide awake!!!",
            "I'm listening",
            "Hello. what did I miss?",
        ]

        system.messaging.post("tts_say", [random.choice(PHRASES), "EN"])

    def on_mode_entry(self, from_mode_name: Optional[str]):
        """Called when you enter sleep mode.

        Say something, and switch the LED colour.

        Args:
            from_mode_name (Optional[str]): the mode you have come from
        """
        if from_mode_name is not None:
            PHRASES = [
                "Got it.",
                "Going to sleep",
                "Off to sleepy land I go",
                "I'll stop listening",
                "Let me know when you want me to wake again",
                "Night night",
            ]
            system.messaging.post("tts_say", [random.choice(PHRASES), "EN"])

        system.messaging.post("set_led", (1, 1, 0))

    async def on_message(self, channel: str, message: Any):
        """Called when a system message is recieved.

        Overwrite the default behaviour so that we don't have the thinking face

        Args:
            channel (str): the channel the message was sent on
            message (Any): the message content
        """

        # Do not allow the recursive LLM calls to actually do any TTS in this mode
        if channel == "speech_recognized":
            await self.recursively_call_llm(
                message, output_stream=gpt_decider_mode.stream_module.dummyStream
            )


MODE = SleepMode
