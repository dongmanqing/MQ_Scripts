"""
Loads layered LookAt Config for use by other scripts
"""


def module_to_dict(module):
    return {
        key: value
        for key, value in module.__dict__.items()
        if (not key.startswith("__")) and (not key.endswith("__"))
    }


LOOKAT_CONFIG_MODULE = system.import_library("./Default/LookAt.py")

# TODO: Layer robot-specific config on top
CONFIG = module_to_dict(LOOKAT_CONFIG_MODULE)
