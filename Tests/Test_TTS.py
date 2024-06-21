"""
Add a short description of your script here

See https://tritiumrobot.cloud/docs/ for more information
"""

from pathlib import Path
import os


class Activity:
    def on_start(self):  # self.set_debug_value
        print('Path.home(): ', Path.home())
        print(f'current dir: {os.getcwd()}')
        response = 'thumbing up'
        # system.messaging.post("speech_recognized", [f": look at me, i am {response}, what would be your best reaction on this? and could you please make some approapriate expressions in response to this", "EN"])
        system.messaging.post("tts_say", ["I can't see clearly.", "EN"])
