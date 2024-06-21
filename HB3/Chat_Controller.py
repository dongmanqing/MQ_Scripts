from typing import List, Optional

from jinja2 import Template
import time

"""
System
"""

UTILS = system.import_library("./Utils.py")
SCRIPTS_TO_START = [
    "./HB3_Controller.py",
]
SCRIPTS = [
    "./2.Perception/Add_Speech.py",
    "./Autonomous Behaviour/Anim_Talking_Sequence.py",
]

"""
Action Decider
"""
PROFILES = system.import_library("./Decisive Behaviour/Knowledge/Profiles.py")
INTERACTION_HISTORY = system.import_library(
    "./Decisive Behaviour/Knowledge/Interaction_History.py"
)
ENVIRONMENT_KNOWLEDGE = system.import_library(
    "./Decisive Behaviour/Knowledge/Environment_Knowledge.py"
)
"""
Skills
"""
MODE_CONTROLLER = system.import_library(
    "./Decisive Behaviour/Skills/mode_controller.py"
)

CONFIG = system.import_library("../Config/Chat.py").CONFIG

DIAGNOSTICS_MODE_MODULE = system.import_library(
    "./Decisive Behaviour/Skills/modes/diagnostics_mode.py"
)
NORMAL_MODE_MODULE = system.import_library(
    "./Decisive Behaviour/Skills/modes/normal_mode.py"
)
SLEEP_MODE_MODULE = system.import_library(
    "./Decisive Behaviour/Skills/modes/sleep_mode.py"
)

DRAWING_MODE_MODULE = system.import_library(
    "./Decisive Behaviour/Skills/modes/drawing_mode.py"
)

MODE_MODULES = [
    DIAGNOSTICS_MODE_MODULE,
    NORMAL_MODE_MODULE,
    SLEEP_MODE_MODULE,
    DRAWING_MODE_MODULE,
]

MODES = {}
for mode_module in MODE_MODULES:
    mode = mode_module.MODE()
    if mode.MODE_NAME in CONFIG["MODES"]:
        MODES[mode.MODE_NAME] = mode

CHAT_SYSTEM_TYPE = CONFIG["CHAT_SYSTEM_TYPE"]
DISABLE_ASR_WHILE_SPEAKING = CONFIG["DISABLE_ASR_WHILE_SPEAKING"]
RULES_BASED_CHATBOT_MODULE = system.import_library(
    "./Decisive Behaviour/Skills/rules_based_chatbot.py"
)


class Activity:
    silent_mode = False
    mode_controller = None

    def on_start(self):
        for script_path in SCRIPTS + SCRIPTS_TO_START:
            UTILS.start_other_script(system, script_path)

        system.messaging.post("asr_enable", True)

        self.chat_system: CHAT_SYSTEM_TYPE = CONFIG.get("CHAT_SYSTEM")
        self.interaction_history = INTERACTION_HISTORY.InteractionHistory()
        self.interaction_history.reset()
        self.telepresence_started = False
        self.mode_controller = (
            MODE_CONTROLLER.ModeController(MODES, "normal")
            if self.chat_system == CHAT_SYSTEM_TYPE.CHAT_FUNCTION_CALL
            else None
        )
        if self.chat_system == CHAT_SYSTEM_TYPE.RULES_BASED_CHATBOT:
            url: Optional[str] = CONFIG["RULES_BASED_CHATBOT_URL"]
            self.rules = RULES_BASED_CHATBOT_MODULE.RulesBasedChatbot(url)

        probe("Chat System", self.chat_system)
        probe("Speech Mode", None)

    def on_stop(self):
        system.messaging.post("set_led", (0, 0, 0))
        for script_path in SCRIPTS:
            UTILS.stop_other_script(system, script_path)
        self.mode_name = None

    async def on_message(self, channel, message):
        is_interaction: bool = False
        # if channel == "speech_recognized":
        #     print(f'on message channel: {channel}, message: {message}')
            # import traceback
            # traceback.print_stack()
            # print('====')
        # print('model controller: ', self.mode_controller) # script_1037.ModelController.py

        if channel == "speech_recognized":
            if DISABLE_ASR_WHILE_SPEAKING:
                system.messaging.post("asr_enable", False)
            speaker = ENVIRONMENT_KNOWLEDGE.get_speaker()
            self.interaction_history.add_to_memory(
                INTERACTION_HISTORY.SpeechRecognisedEvent(speaker, message)
            )
            print(f"{speaker}: {message}")
            is_interaction = True

        if channel == "non_verbal_interaction_trigger":
            world_face = message
            trigger_description: str = ", ".join(world_face.events)
            self.interaction_history.add_to_memory(
                INTERACTION_HISTORY.NonVerbalInteractionEvent(
                    world_face.id, trigger_description
                )
            )
            interaction_discription: str = self.interaction_history.history[
                -1
            ].event.to_text()
            print(
                f"non_verbal_interaction_trigger: {interaction_discription}: {world_face.id}"
            )
            is_interaction = True

        elif channel == "silent_mode":
            self.silent_mode = message
        elif channel == "telepresence":
            if message.get("type", "") == "session_active":
                self.telepresence_started = message.get("value", False)
        if self.mode_controller is not None:
            await self.mode_controller.on_message(channel, message)
        elif is_interaction:
            system.messaging.post("thinking", True)
            await self.react_to_interaction(message)
            system.messaging.post("thinking", False)

    async def react_to_interaction(self, message: str):
        if self.telepresence_started:
            return

        if self.chat_system == CHAT_SYSTEM_TYPE.RULES_BASED_CHATBOT:
            speech_list: List[
                RULES_BASED_CHATBOT_MODULE.RulesBasedSpeech
            ] = await self.rules.call_rules_based_chatbot(message)
            for speech in speech_list:
                if speech.animation_path:
                    system.messaging.post("play_sequence", speech.animation_path)
                else:
                    system.messaging.post("tts_say", [speech.speech, "EN"])

    @system.tick(fps=1)
    def on_tick(self):
        probe("Telepresence Started", self.telepresence_started)
        # print('hellow world!!!')
        # print(time.time())

        if self.mode_controller is not None:
            probe("Speech Mode", self.mode_controller.mode_name)