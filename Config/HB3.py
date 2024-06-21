get_layered_config = system.import_library("./utils.py").get_layered_config

CONFIG_MODULE = system.import_library("./Default/HB3.py")
ROBOT_CONFIG_MODULE = system.try_import_library("./Robot/HB3.py")

CONFIG = get_layered_config(CONFIG_MODULE, ROBOT_CONFIG_MODULE)
