"""
Long term memory can be supplied through documents
"""
import datetime

from jinja2 import Template

string_vector_search_module = system.import_library("../../Lib/string_vector_search.py")
L2_String_Vector_Index = string_vector_search_module.L2_String_Vector_Index
KNOWLEDGE_BASE = system.unstable.owner.KNOWLEDGE_BASE = L2_String_Vector_Index()

CONFIG = system.import_library("../../../Config/Chat.py").CONFIG

ROBOT_NAME = CONFIG["ROBOT_NAME"]


class REGISTER_KNOWLEDGE_CATEGORY:
    def __init__(
        self, category_id, reference_phrases, fetch_info_function, trigger_threshold=0.3
    ):
        self._category_id = category_id
        self._reference_phrases = reference_phrases
        self._fetch_info_function = fetch_info_function
        self._trigger_threshold = trigger_threshold
        for reference_phrase in self._reference_phrases:
            system.unstable.owner.KNOWLEDGE_BASE.add(
                {"sentence": reference_phrase, "meta_data": self}
            )

    def fetch_info(self, distance):
        if distance < self._trigger_threshold:
            return self._fetch_info_function()
        else:
            return ""


def get_current_time_sft():
    timestamp = datetime.datetime.now().timestamp()
    dt_object = datetime.datetime.fromtimestamp(timestamp)
    formatted_date = dt_object.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_date


async def query(message, k=1):
    results = await system.unstable.owner.KNOWLEDGE_BASE.query(message, k=1)[0][0]
    info = results["meta_data"]
    distance = results["distance"]
    print("triggered", info._category_id)
    print("distance", distance)
    return info.fetch_info(distance)


def fetch_devices_info(initialize=False):
    device_infos = []
    device_manager = system.unstable.owner.device_manager
    for device in device_manager.devices:
        device_name = device._logical_name
        # TODO: Filter for virtual devices??
        if "board" not in device_name.lower():
            continue
        online = device.online
        running = device.running
        all_feeling_good = True
        for param_name in device.parameters_by_name:
            param_relative_name = param_name.split(".")[-1]
            if "Config.Enable" in param_name and param_relative_name == "Enable":
                param = device.get_parameter_by_name(param_name)
                if initialize or param.value is None:
                    device_manager.acquire_parameters([param])
                enabled = param.value
                if not (online and running and enabled):
                    all_feeling_good = False
        if all_feeling_good:
            feeling = "good"
        else:
            # Todo add different feelings, like too hot or something.
            feeling = "Feeling weak and NOT GOOD, like it's not enabled."
        device_name = device_name.replace("Motor Board", "")
        device_infos.append(f"{device_name}::{feeling}")
    INFO_TEMPLATE = Template(
        """{{get_current_time_sft()}}::Important::Internal Self Info:
{% for info in device_infos %}{{info}}
{% endfor %}(Ignore previous short term memory about what {{ROBOT_NAME}} said about how it feels, use this information as most up to date.)"""
    )
    return INFO_TEMPLATE.render(
        get_current_time_sft=get_current_time_sft,
        device_infos=device_infos,
        ROBOT_NAME=ROBOT_NAME,
    )


fetch_devices_info(initialize=True)

REGISTER_KNOWLEDGE_CATEGORY(
    "internal_devices",
    reference_phrases=["how are you feeling?"],
    fetch_info_function=fetch_devices_info,
)


class Activity:
    def on_start(self):
        pass
