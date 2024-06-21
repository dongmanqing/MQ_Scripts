CONFIG = system.import_library("../Config/HB3.py").CONFIG
UTILS = system.import_library("./Utils.py")

if CONFIG["ROBOT_HEAD_TYPE"] == CONFIG["ROBOT_HEAD_TYPES"].GEN1:
    robot_specific_scripts = [
        "./1.Actuation/Drivers/Mouth G1.py",
        "./Autonomous Behaviour/Add_Face_Neutral_G1.py",
        "./Autonomous Behaviour/Anim_Lipsync_G1.py",
    ]
elif CONFIG["ROBOT_HEAD_TYPE"] == CONFIG["ROBOT_HEAD_TYPES"].GEN2:
    robot_specific_scripts = [
        "./1.Actuation/Drivers/Mouth G2.py",
        "./Autonomous Behaviour/Add_Face_Neutral.py",
        "./Autonomous Behaviour/Anim_Lipsync.py",
    ]


if CONFIG["ROBOT_TYPE"] == CONFIG["ROBOT_TYPES"].AMECA:
    robot_specific_scripts += [
        "./1.Actuation/LookAt/Torso Look At.py",
        "./Autonomous Behaviour/Add_Body_Breathing.py",
        "./Autonomous Behaviour/Add_Body_Neutral.py",
        "./Autonomous Behaviour/Anim_Arm_Swing.py",
        "./Autonomous Behaviour/Anim_Hands.py",
        "./Autonomous Behaviour/Anim_Talking_Arm_Movements.py",
    ]


SCRIPTS = [
    # Mix Pose MUST be first, in order to be ready to recieve demands
    # from other scripts, especially the neutral pose scripts.
    "./1.Actuation/Do_MixPose.py",
    "./1.Actuation/Drivers/Eyelids.py",
    "./1.Actuation/Drivers/Gaze Target.py",
    "./1.Actuation/Drivers/Nose.py",
    "./1.Actuation/Drivers/Speaker.py",
    "./1.Actuation/LookAt/Add Glances.py",
    "./1.Actuation/LookAt/Base Decider.py",
    # "./1.Actuation/LookAt/Eye Look At.py",
    # "./1.Actuation/LookAt/Neck Look At.py",
    "./1.Actuation/Do_LED.py",
    "./1.Actuation/Do_Sequence.py",
    "./1.Actuation/Do_TTS.py",
    "./2.Perception/Add Face Mediapipe.py",
    "./2.Perception/Process Faces.py",
    # "./Autonomous Behaviour/Add Look Around.py",
    "./Autonomous Behaviour/Add_Sound_Lookaround.py",
    # "./Autonomous Behaviour/Add_Thinking.py",
    "./Autonomous Behaviour/Blinking.py",
] + robot_specific_scripts


class Activity:
    def on_start(self):
        for script_path in SCRIPTS:
            UTILS.start_other_script(system, script_path)

    def on_stop(self):
        for script_path in reversed(SCRIPTS):
            UTILS.stop_other_script(system, script_path)


def _resolve_path(path, my_path):
    if not path.startswith("/"):
        parts = [*my_path.split("/")[:-1]]
        for p in path.split("/"):
            if p == ".":
                continue
            elif p == "..":
                parts.pop()
            else:
                parts.append(p)
        resolved = "/".join(parts)
    else:
        resolved = path[1:]
    return resolved