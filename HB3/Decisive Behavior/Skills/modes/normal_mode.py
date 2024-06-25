from typing import Any, Optional

from jinja2 import Template

CONFIG = system.import_library("../../../../Config/Chat.py").CONFIG
SPEAKER_MAP = CONFIG["SPEAKER_MAP"]
PERSONALITY = CONFIG["PERSONALITY"]
ROBOT_NAME = CONFIG["ROBOT_NAME"]
USE_MULTI_LANG = CONFIG["USE_MULTI_LANG"]
LOADED_PROFILE = CONFIG["LOADED_PROFILE"]
HISTORY_LIMIT = CONFIG["NORMAL_MODE_HISTORY_LIMIT"]

#### IMPORTS ####

gpt_decider_mode = system.import_library("./gpt_decider_mode.py")
mode = system.import_library("./mode.py")
mode_controller = system.import_library("../mode_controller.py")
gpt_model = system.import_library("../../../Lib/OpenAI/gpt_model.py")

vqa = system.import_library("../actions/vqa.py")
system_actions = system.import_library("../actions/system_actions.py")
interaction_actions = system.import_library("../actions/interaction_actions.py")
lookat_actions = system.import_library("../actions/lookat_actions.py")
# mq_vqa = system.import_library("../../../../Dev/PLI/MQChat/mq_vqa.py")
# mq_vqa_gpt4v = system.import_library("../../../../Dev/PLI/MQChat/mq_vqa_gpt4v.py")
mq_actions = system.import_library("../../../../Dev/PLI/MQChat/GPTFuncCalls/funcs.py")
mq_visual_funcs = system.import_library("../../../../Dev/PLI/MQChat/GPTFuncCalls/mq_visual_funcs.py")
mq_nlp_funcs = system.import_library("../../../../Dev/MQ/functions/nlp_funcs.py")


#### Idle Model ####

# This is used when the robot is currently idle / not talking

# Disable profile until identity is stable
# PROFILE_INSTRUCTIONS = """You will be provided with PROFILES - a json description of the known people around you.
# If someone asks you to forget certain details about them, or about them entirely - please do as asked.
# Note 'Person x' (e.g. Person 1, Person 2) are internal identifiers. They are NOT the names of the people. You MUST NEVER refer to people by these identifiers."""
PROFILE_INSTRUCTIONS = ""

system_message_template_idle = Template(
    f"""{{{{{'PERSONALITY'}}}}}

{PROFILE_INSTRUCTIONS}
You will also be provided with the conversation up until now.

"""
)


# PROFILE_INFO = """PROFILES:
# {{PROFILES}}
# """

PROFILE_INFO = ""

user_prompt_template_idle = Template(
    f"""{PROFILE_INFO}
CONVERSATION:
{{{{{'CONVERSATION'}}}}}"""
)


MODEL_FUNCTIONS_IDLE = [
    mq_visual_funcs.vqa_func,
    mq_visual_funcs.face_recog_func,
    mq_visual_funcs.video_recog_func,
    # mq_vqa.get_current_weather,
    # mq_vqa.mq_vqa_func,
    # mq_vqa.mq_query_person,
    mq_actions.switch_to_proactive_chat,
    mq_actions.switch_to_reactive_chat,
    # vqa.vqa, # disable until look_at / thinking animation is compatible
    mq_nlp_funcs.rag_func,
    system_actions.turn_volume_up,
    system_actions.turn_volume_down,
    system_actions.change_head_colour,
    system_actions.wait_for,
    interaction_actions.introduction_information,
    # interaction_actions.do_joke,
    system_actions.sleep_mode,
    system_actions.diagnostics_mode,
    # lookat_actions.head_look_up,
    # lookat_actions.head_look_down,
]

if "drawing" in CONFIG["MODES"]:
    MODEL_FUNCTIONS_IDLE.append(system_actions.drawing_mode)

if show_facial_expressions := interaction_actions.show_facial_expression_factory(
    "Chat Expressions.dir"
):
    MODEL_FUNCTIONS_IDLE.append(show_facial_expressions)

if show_gestures := interaction_actions.show_gesture_factory("Chat Gesture.dir"):
    MODEL_FUNCTIONS_IDLE.append(show_gestures)


DECISION_MODEL_IDLE = gpt_model.GPTModel(
    model="gpt-4-0613",
    system_message=system_message_template_idle.render(PERSONALITY=PERSONALITY),
    functions=MODEL_FUNCTIONS_IDLE,
    user_prompt_template=user_prompt_template_idle,
    history_limit=HISTORY_LIMIT,
    **LOADED_PROFILE.openai_params,
)

#### Talking Model ####
# This is used when the robot is currently talking
# It is used to decide whether to interrupt what the robot is saying

system_message_talking = f"""Your name is {ROBOT_NAME}. You are currently talking. You have just heard something being said, although it is not necessarily addressed to you.

You must either stop talking if someone is asking you to, but keep talking if no has asked you to. If you want to continue, just reply with nothing.
"""

user_prompt_template_talking = Template(
    """Someone just said: {{MESSAGE}}
To keep talking, respond with nothing."""
)

DECISION_MODEL_TALKING = gpt_model.GPTModel(
    model="gpt-3.5-turbo-0613",
    system_message=system_message_talking,
    functions=[system_actions.stop_talking],
    user_prompt_template=user_prompt_template_talking,
    **LOADED_PROFILE.openai_params,
)


class NormalMode(gpt_decider_mode.GPTDeciderMode):
    """The normal interaction mode."""

    MODE_NAME = "normal"
    DECISION_MODEL = DECISION_MODEL_IDLE

    def __init__(self):
        self.talking = False
        self.DECISION_MODEL = DECISION_MODEL_IDLE

    def on_mode_entry(self, from_mode_name: Optional[str]):
        """Called when you enter normal mode.

        Switch the LED colour.

        Args:
            from_mode_name (Optional[str]): the mode you have come from
        """
        self.DECISION_MODEL.interaction_history.reset()
        system.messaging.post("set_led", (1, 0, 1))
        self.output_stream: gpt_decider_mode.stream_module.StreamOutput = (
            gpt_decider_mode.stream_module.streamToMultiLangTTS
            if USE_MULTI_LANG
            else gpt_decider_mode.stream_module.streamToDefaultTTS
        )

    async def on_message(self, channel: str, message: Any):
        """Called when a system message is received.

        Args:
            channel (str): the channel the message was sent on
            message (Any): the message content
        """
        if channel == "tts_saying":
            self.talking = True
        elif channel == "tts_idle":
            self.talking = False
        elif not self.talking:
            if channel == "speech_recognized":
                self.DECISION_MODEL = DECISION_MODEL_IDLE
                if channel == "speech_recognized":
                    system.messaging.post("thinking", True)
                    await self.recursively_call_llm(
                        message, output_stream=self.output_stream
                    )
                    system.messaging.post("thinking", False)
            elif channel == "non_verbal_interaction_trigger":
                await self.recursively_call_llm(
                    message, output_stream=self.output_stream
                )
        elif channel == "speech_recognized":
            system.messaging.post("tts_interrupt", None)
            self.DECISION_MODEL = DECISION_MODEL_TALKING
            print(self.output_stream)
            await self.recursively_call_llm(message, output_stream=self.output_stream)
            system.messaging.post("tts_continue", None)


MODE = NormalMode
