from jinja2 import Template

gpt_decider_mode = system.import_library("./gpt_decider_mode.py")
gpt_model = system.import_library("../../../Lib/OpenAI/gpt_model.py")

diagnostics_actions = system.import_library("../actions/diagnostics_actions.py")

system_message = """Base on the information the user provided, act accordingly as follows:

Any other critical error should be reported via rocket chat with the source log included in the massage.

The following errors should be ignored:
`usb <address.port usb_spec> cannot get freq at ep <endpoint_id>`
`MMIO Stale Data CPU bug present and SMT on`
`interrupt took <number> ns`
any `ata` log message

"""

user_prompt_template = Template("""{{MESSAGE}}""")


MODEL = gpt_model.GPTModel(
    model="gpt-3.5-turbo-0613",
    system_message=system_message,
    functions=[diagnostics_actions.rocket_chat_factory("RobotDiagnostics")],
    user_prompt_template=user_prompt_template,
)


class MonitorMode(gpt_decider_mode.GPTDeciderMode):
    MODE_NAME = "monitor"
    DECISION_MODEL = MODEL