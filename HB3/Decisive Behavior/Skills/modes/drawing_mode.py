"""Robot can do drawings."""

from os import walk
from enum import Enum
from typing import Any, Optional

from jinja2 import Template
from tritium import log

string_vector_search_module = system.import_library(
    "../../../Lib/string_vector_search.py"
)

gpt_decider_mode = system.import_library("./gpt_decider_mode.py")
gpt_model = system.import_library("../../../Lib/OpenAI/gpt_model.py")

system_actions = system.import_library("../actions/system_actions.py")

system_message = """You are a humanoid robot who can do drawings for people.

Work out what the user wants you to draw, and then draw it."""


user_prompt_template = Template("""{{MESSAGE}}""")

MODEL = gpt_model.GPTModel(
    model="gpt-3.5-turbo-0613",
    system_message=system_message,
    functions=[],
    user_prompt_template=user_prompt_template,
)

DRAWING_SCRIPT = "Drawing/Draw.py"


class DrawingStates(Enum):
    IN_OTHER_MODE = "in other mode"
    WAITING_FOR_USER_INPUT = "waiting for user input"
    DRAWING = "drawing"
    FINISHED = "finished drawing"
    STOPPING = "stopping drawing at user request"
    STOPPED = "stopped drawing at user request"
    WIPING = "wiping board"


class DrawingMode(gpt_decider_mode.GPTDeciderMode):
    """
    Robot can drawing in this mode.
    """

    MODE_NAME = "drawing"
    DECISION_MODEL = MODEL

    def __init__(self) -> None:
        self.__to_state(DrawingStates.IN_OTHER_MODE)
        self.__knowledge_base = string_vector_search_module.L2_String_Vector_Index()
        for _, _, filenames in walk("/var/opt/tritium/content/Drawing.dir/Images.dir"):
            for filename in filenames:
                if filename.endswith(".json") and not filename.startswith("."):
                    thing_to_draw = filename[:-5]
                    self.__knowledge_base.add(
                        {"sentence": thing_to_draw, "meta_data": thing_to_draw}
                    )

        DrawingMode.DECISION_MODEL.set_functions(
            [
                self.__draw,
                # self.__generate_and_draw,
                self.__stop,
                system_actions.normal_mode,
            ]
        )

    def on_mode_exit(self):
        """
        Called when you exit drawing mode.
        """
        self.__to_state(DrawingStates.IN_OTHER_MODE)
        system.messaging.post("tts_say", ["It's been great drawing with you.", "EN"])

    def on_mode_entry(self, from_mode_name: Optional[str]):
        """
        Called when you enter drawing mode.

        Say something, and switch the LED colour.

        Args:
            from_mode_name (str): the mode you have come from
        """
        self.__to_state(DrawingStates.WAITING_FOR_USER_INPUT)
        system.messaging.post("tts_say", ["Yahooo let's do some drawing!!", "EN"])
        system.messaging.post("tts_say", ["What would you like me to draw?", "EN"])
        system.messaging.post("set_led", (0, 1, 1))
        system.unstable.state_engine.start_activity(
            cause="Entering drawing mode",
            activity_class="script",
            properties={
                "script": DRAWING_SCRIPT,
                "script_file_path": f"/var/opt/tritium/scripts/{DRAWING_SCRIPT}",
            },
        )

    async def on_message(self, channel: str, message: Any):
        await super().on_message(channel, message)
        match channel:
            case "drawing":
                match message[0]:
                    case "finished":
                        self.__to_state(DrawingStates.FINISHED)
                        system.messaging.post("tts_say", ["Drawing is finished.", "EN"])
                        system.messaging.post("tts_say", ["How do you like it?", "EN"])
                    case "stopped":
                        self.__to_state(DrawingStates.STOPPED)
                        system.messaging.post(
                            "tts_say", ["I stopped drawing as you requested.", "EN"]
                        )

    async def __draw(self, description: str):
        """
        Do a drawing of something.

        Args:
            description: a description of what to draw.
        """
        match self.__state:
            case DrawingStates.DRAWING:
                system.messaging.post("tts_say", ["I am drawing, be patient.", "EN"])
            case DrawingStates.WAITING_FOR_USER_INPUT | DrawingStates.FINISHED | DrawingStates.STOPPED:
                self.__to_state(DrawingStates.DRAWING)
                results = await self.__knowledge_base.query(description)
                result = results[0][0]
                thing_to_draw = result["content"]
                log.info(
                    f"Closest thing to '{description}' was found to be '{thing_to_draw}' with distance {result['distance']}"
                )
                system.messaging.post("drawing", ["load_and_draw", thing_to_draw])
                system.messaging.post(
                    "tts_say", [f"Drawing a picture of {thing_to_draw}", "EN"]
                )

    async def __generate_and_draw(self, description: str):
        """
        Generate image and draw it.

        Args:
            description: a description of what to draw.
        """
        system.messaging.post("drawing", ["generate_and_draw", description])
        system.messaging.post(
            "tts_say", [f"Generating a picture of {description}", "EN"]
        )

    async def __stop(self):
        """
        Stop drawing.
        """
        match self.__state:
            case DrawingStates.DRAWING:
                self.__to_state(DrawingStates.STOPPING)
                system.messaging.post("drawing", ["stop"])
            case DrawingStates.STOPPING:
                system.messaging.post(
                    "tts_say", ["I am stopping already, no need to repeat.", "EN"]
                )

    def __to_state(self, state: DrawingStates) -> None:
        """
        Transition to given state.
        """
        log.info(f"Drawing mode is entering state: {state}")
        self.__state = state


MODE = DrawingMode
