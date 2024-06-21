import json
import socket
import subprocess
from glob import glob
from http import HTTPStatus
from typing import Any, Dict, List, Tuple, Literal, Optional
from datetime import datetime

import requests

gpt_functions = system.import_library("../../../Lib/OpenAI/gpt_functions.py")


RocketChat = system.import_library("../../../../Utils/rocketchat.py").RocketChat


class LogProcessor:
    priority_map: Dict[str, str] = {
        "0": "Emergency",
        "1": "Alert",
        "2": "Critical",
        "3": "Error",
        "4": "Warning",
        "5": "Notice",
        "6": "Info",
        "7": "Debug",
    }

    def __init__(self) -> None:
        self.inverse_priority_map: Dict[str, str] = {
            self.priority_map[k]: k for k in self.priority_map
        }

    def getCurrentJournal(
        self,
        unit_name: Optional[str] = None,
        n: int = 50,
        reverse: bool = False,
        min_level: int = 4,
        kernel: bool = False,
        since: Optional[str] = None,
    ) -> str:
        # journalctl _SYSTEMD_INVOCATION_ID=`systemctl show --value -p InvocationID tritium-node-gateway-plugin-host.service` -p "emerg".."warning" -o json
        args = ["journalctl"]
        if unit_name:
            cp = subprocess.run(
                ["systemctl", "show", "--value", "-p", "InvocationID", unit_name],
                capture_output=True,
            )
            inv = cp.stdout.decode("utf-8").replace("\n", "")
            args.append(f"_SYSTEMD_INVOCATION_ID={inv}")

        if reverse:
            args.append("-r")

        if kernel:
            args.append("-k")

        if since:
            args += ["--since", since]

        args += ["-b", "-p", str(min_level), "-o", "json"]
        result = subprocess.run(args, capture_output=True)
        return self._formatJournalctlJson(result.stdout.decode("utf-8"), n)

    def getSystemctlUnits(
        self, unit_pattern: Optional[str] = None
    ) -> Tuple[List[str], str]:
        """Get `systemd` units that fits the pattern and its status in a string format

        Args:
            unit_pattern (Optional[str]): systemctl unit pattern. If non is specified all units will be listed.

        Returns:
            unit_list, status (Tuple[List[str], str]): List of all the units that fits the pattern, and a string that represent the status of the units.
        """
        # systemctl list-units tritium*

        args = ["systemctl", "list-units", "--no-pager"]
        if unit_pattern:
            args.append(unit_pattern)
        result = subprocess.run(args, capture_output=True)
        buffer: List[str] = []
        units: List[str] = []

        legend_start_index: int = -5
        raw_out: str = result.stdout.decode("utf-8")
        legend: List[str] = raw_out.splitlines()[legend_start_index:]
        white_space_removed_lines: List[str] = self._remove_extra_spaces(
            raw_out
        ).splitlines()
        for line in white_space_removed_lines[:legend_start_index]:
            cells = line.split()
            if len(cells) <= 0:
                continue
            unit = cells[0]
            active = cells[2]
            description = "".join(cells[4:])
            buffer.append(unit + "\t" + active + '\t"' + description + '"')
            units.append(unit)
        return units, "\n".join(buffer + legend)

    def _remove_extra_spaces(self, text) -> str:
        new_text = ""
        prev_char = ""
        for char in text:
            if char == " " and prev_char == " ":
                continue
            new_text += char
            prev_char = char
        return new_text

    def _formatJournalctlJson(self, json_strings: str, n: int) -> str:
        empty_r_val: str = "-- No entries --"
        key_order = ("SYSLOG_IDENTIFIER", "PRIORITY", "MESSAGE")
        str_buffer: List[str] = ["\t".join(key_order)]

        j_str_list = json_strings.splitlines()[:n]
        for j_str in j_str_list:
            try:
                j = json.loads(j_str)
                msg: str = j[key_order[2]]
                unit = j[key_order[0]]
                priority = self.priority_map[j[key_order[1]]]
                msg = msg.replace("\n", "")
                str_buffer.append(f"{unit}\t{priority}\t{msg}")
            except Exception:
                continue

        if len(str_buffer) <= 1:
            return empty_r_val

        return "\n".join(str_buffer)


def check_kernel_factory():
    system_input_template = """You function as a system monitor specialized in analyzing kernel
logs within a Linux-based operating environment.

Upon receiving a posted kernel log from the user, respond with a  JSON conforming to the following schema (Do not put the schema into the reply):

``` JSON schema
{
    "type": "object",
    "properties": {
    "status": {
        "type": "string",
        "enum": ["good", "bad"]
    },
    "comment": {
        "type": "string"
    },
    "source": {
        "type": "array",
        "items":  {
        "type": "string"
        },
        "maxItems": 5
    }
    },
    "required": [
    "status",
    "comment",
    "source"
    ]
}
```


The "status" field indicates the overall health of the system, the "comment" field provides an explanation of any identified issues, and the "source" field comprises an array containing relevant lines of log entries including timestamps."""

    user_input_template = "{kernel_logs}"

    log_processor = LogProcessor()

    log_level_enum = tuple(log_processor.inverse_priority_map.keys())

    async def check_kernel(
        log_level: Literal[log_level_enum] = "Warning", since: Optional[datetime] = None
    ) -> str:
        """Use the system logs to check what has gone wrong with the `node`.

        #REQUIRES_SUBSEQUENT_FUNCTION_CALLS
        Args:
            log_level: logs below this log level will be filtered out.

        Returns:
            The response from the call.
        """
        nonlocal system_input_template, user_input_template, log_processor
        log_level_int: int = int(log_processor.inverse_priority_map[log_level])
        kwargs = {}
        if since:
            kwargs = {"since": str(since)}

        log = log_processor.getCurrentJournal(
            min_level=log_level_int, kernel=True, **kwargs
        )
        user_content = user_input_template.replace("{kernel_logs}", log)

        chat_msg = [
            {
                "role": "system",
                "content": system_input_template,
            },
            {"role": "user", "content": user_content},
        ]

        response = await gpt_functions.run_chat(
            model="gpt-4", messages=chat_msg, temperature=0.2
        )

        reply = response["content"]
        print(reply)
        return reply

    return check_kernel


def check_log_factory():
    user_input_template = """{user_input}
Summarize the result to two or three sentences. Try to interpret the source of the issue, report the file name (not path) and the line number where the error occurred if possible.
The following is the `journalctl` logs from `{journalctl_unit}`:

```
{journalctl_log}
```
"""

    log_processor = LogProcessor()
    units = [
        unit.replace(".service", "")
        for unit in log_processor.getSystemctlUnits("tritium-node-*")[0]
    ]
    units_enum = tuple(["All"] + units)

    log_level_enum = tuple(log_processor.inverse_priority_map.keys())

    async def check_log(
        query: str,
        node_identifier: Literal[units_enum],
        log_level: Literal[log_level_enum] = "Warning",
    ) -> str:
        """Use the `systemd` logs to check what has gone wrong with the `node`.

        Args:
            query: the query to make about the logs. E.g. `What is wrong with the mediapipe node`
            node_identifier: use 'All' to check the logs for all nodes, or identifier for the `node`.
            log_level: logs below this log level will be filtered out.

        Returns:
            The response from the call.
        """
        nonlocal user_input_template, log_processor
        log_level_int: int = int(log_processor.inverse_priority_map[log_level])

        if node_identifier != "All":
            node_identifier = (
                "tritium-node-scripts-py3"
                if (node_identifier == "tritium-node-scripts")
                else node_identifier
            )  # Jank jank jank bad jank
            log = log_processor.getCurrentJournal(
                node_identifier, min_level=log_level_int
            )
        else:
            log = log_processor.getCurrentJournal(min_level=log_level_int)

        user_content = (
            user_input_template.replace("{user_input}", query)
            .replace("{journalctl_unit}", node_identifier)
            .replace("{journalctl_log}", log)
        )

        chat_msg = [
            {
                "role": "system",
                "content": "You are a Linux expert that troubleshoots issues.",
            },
            {"role": "user", "content": user_content},
        ]

        response = await gpt_functions.run_chat(
            model="gpt-3.5-turbo-16k", messages=chat_msg, temperature=0.2
        )

        reply = response["content"]
        return reply

    return check_log


def control_node_factory():
    """A factory to generate the control_node function."""
    log_processor = LogProcessor()
    units, _ = log_processor.getSystemctlUnits("tritium-node-*")
    identifiers = [
        n.replace("tritium-node-", "").replace("-", "_").replace(".service", "")
        for n in units
    ]
    node_identifier_options = tuple(["All"] + identifiers)

    async def control_node(
        command: Literal["start", "stop", "restart", "enable", "disable"],
        node_indentifier: Literal[node_identifier_options],
    ) -> str:
        """'start', 'stop', 'restart', 'enable', or 'disable' a `node`.

        #REQUIRES_SUBSEQUENT_FUNCTION_CALLS
        Args:
            command (str): command to issue to the target `node`.
            node_indentifier (str): use "All" restart all the units, or identifier of the `node`.

        Returns:
            The results of the operation.
        """
        targets: list[str] = []
        if node_indentifier == "All":
            targets = identifiers
        else:
            targets.append(node_indentifier)

        results: list[str] = []
        for target in targets:
            # /opt/tritium/bin/tritium_control_node restart sequence_player
            args = ["sudo", "/opt/tritium/bin/tritium_control_node", command, target]
            process = subprocess.run(args, capture_output=True)
            result = (
                target + " " + command + " Failed"
                if process.returncode
                else "Successfully"
            )
            print(process.stdout.decode("utf-8"))
            results.append(result)

        return ", ".join(results)

    return control_node


async def connectivity_check(url: str = "https://www.google.com/") -> str:
    """Check if a url is reachable via the internet.

    Uses an HTTP GET request.

    #REQUIRES_SUBSEQUENT_FUNCTION_CALLS

    Args:
        url: the url to query.

    Returns:
        The result.
    """
    try:
        response = requests.get(url)
        return (
            f"`{url}` returned a status code of {response.status_code}: "
            + HTTPStatus(response.status_code).description
        )
    except Exception as e:
        err_template: str = "While trying to reach {0}, An exception of type {1} occurred. Arguments:\n{2!r}"
        return err_template.format(url, type(e).__name__, e.args)


class ControlScripts:
    default_base_script_path = "/var/opt/tritium/scripts"

    def __init__(
        self, base_script_path: Optional[str] = default_base_script_path
    ) -> None:
        self.base_script_path = base_script_path

        path_enum = tuple(self._getScriptRelativePaths())

        async def control_scripts(
            self, command: Literal["start", "stop", "restart"], path: Literal[path_enum]
        ) -> str:
            """'start', 'stop', 'restart', Tritium `scripts`.

            #REQUIRES_SUBSEQUENT_FUNCTION_CALLS

            Args:
                command: Command to issue to the target `script`
                path: Target `script` path

            Returns:
                Result of control operation.
            """
            if command != "start":
                self._stopScript(path)
            if command != "stop":
                self._startScript(path)

            return "`script` " + command + "ed"

        self.control_scripts = control_scripts

    def _getScriptRelativePaths(self) -> List[str]:
        paths = glob(self.base_script_path + "/**/*.py", recursive=True)
        return [p.strip(self.base_script_path + "/") for p in paths]

    def _is_other_script_running(self, relative_path: str):
        script_path = self.base_script_path + "/" + relative_path
        for activity in system.unstable.state_engine._state.activities:
            if activity.get_property("script") == script_path:
                return True
        return False

    def _startScript(self, relative_path: str):
        if self._is_other_script_running(relative_path):
            return
        return system.unstable.state_engine.start_activity(
            f"Started by [Diagnostic mode] with <{self.name}>",
            "script",
            properties={
                "script": relative_path,
                "script_file_path": self.base_script_path + "/" + relative_path,
            },
        )

    def _stopScript(self, relative_path: str):
        for activity in system.unstable.state_engine._state.activities:
            if activity.get_property("script") == relative_path:
                return system.unstable.state_engine.stop_activity(
                    f"stopped by script: {system._path!r}", activity
                )


def rocket_chat_factory(
    channel: str,
):
    rocket = RocketChat()

    async def rocket_chat(message: str):
        """Send / post information to the user on the `rocket chat` channel.

        #REQUIRES_SUBSEQUENT_FUNCTION_CALLS

        Args:
            message: the message to send.

        """
        nonlocal rocket
        return rocket.send(channel, message)

    return rocket_chat


async def upgrade_packages() -> str:
    """Update and upgrade packages, such as `nodes`

    #REQUIRES_SUBSEQUENT_FUNCTION_CALLS

    Returns:
        The output result.
    """
    update = subprocess.run(["sudo", "apt", "update"], capture_output=True)
    if update.returncode:
        cout = update.stdout.decode("utf-8")
        ceer = update.stderr.decode("utf-8")
        return "apt update failed:\n" + cout + ceer

    upgrade = subprocess.run(["sudo", "apt", "upgrade", "-y"], capture_output=True)
    cout = upgrade.stdout.decode("utf-8")
    if upgrade.returncode:
        ceer = upgrade.stderr.decode("utf-8")
        return "apt upgrade failed:\n" + cout + ceer

    return cout


async def get_ip() -> str:
    """Get the IP address of the robot.

    #REQUIRES_SUBSEQUENT_FUNCTION_CALLS

    Returns:
        The IP address.
    """

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip: str = s.getsockname()[0]
    s.close()
    return ip
