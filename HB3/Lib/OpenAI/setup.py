from pathlib import Path

import openai
from packaging import version

if version.parse(openai.__version__) < version.parse("1.0.0"):
    log.error(
        f"OpenAI package not up to date. Version is {openai.__version__}, but needs to be > 1.0.0. Please run `pip3 install -U openai`."
    )

from openai import AsyncOpenAI

try:
    with open(Path.home() / "openai_key.txt") as fd:
        KEY = fd.read().strip()
    CLIENT = AsyncOpenAI(api_key=KEY)
except FileNotFoundError:
    log.error(
        "Could not find the openai_key file. Please add this in at /home/tritium/openai_key.txt"
    )
    CLIENT = None