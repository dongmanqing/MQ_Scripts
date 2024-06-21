"""Robot becomes a diagnostics tool."""

from typing import Any, Optional

from jinja2 import Template

gpt_decider_mode = system.import_library("./gpt_decider_mode.py")
gpt_model = system.import_library("../../../Lib/OpenAI/gpt_model.py")

system_actions = system.import_library("../actions/system_actions.py")
diagnostics_actions = system.import_library("../actions/diagnostics_actions.py")

control_scripts_obj = diagnostics_actions.ControlScripts()

system_message = """A chat between a user and Ameca's diagnostics system.
The diagnostics system is an expert in Linux, software, electronics, and robotics.
Reply in short sentences, do not use lists."""


user_prompt_template = Template("""{{MESSAGE}}""")

MODEL = gpt_model.GPTModel(
    model="gpt-3.5-turbo-0613",
    system_message=system_message,
    functions=[
        diagnostics_actions.check_log_factory(),
        diagnostics_actions.control_node_factory(),
        diagnostics_actions.connectivity_check,
        control_scripts_obj.control_scripts,
        diagnostics_actions.rocket_chat_factory("RobotDiagnostics"),
        diagnostics_actions.upgrade_packages,
        diagnostics_actions.get_ip,
        system_actions.normal_mode,
    ],
    user_prompt_template=user_prompt_template,
)


class DiagnosticsMode(gpt_decider_mode.GPTDeciderMode):
    """Robot can give you diagnostics information about itself."""

    MODE_NAME = "diagnostics"
    DECISION_MODEL = MODEL

    def on_mode_exit(self):
        """Called when you exit diagnostics mode."""
        system.messaging.post("tts_say", ["Exiting diagnostics mode.", "EN"])

    def on_mode_entry(self, from_mode_name: Optional[str]):
        """Called when you enter diagnostics mode.

        Say something, and switch the LED colour.

        Args:
            from_mode_name (str): the mode you have come from
        """
        system.messaging.post("tts_say", ["Entering diagnostics mode.", "EN"])
        system.messaging.post("set_led", (0, 1, 0))


MODE = DiagnosticsMode
