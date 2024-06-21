"""
Add a short description of your script here

See https://tritiumrobot.cloud/docs/ for more information
"""


class Activity:
    def on_start(self):
        msg = "Turn your head blue"
        msg = f"""
        bottle.
        I see you are hodling a bottle.
        phone.
        I see you are holding a phone.
        glasses.
        """
        msg = "enter proactive mode"
        # msg = f"You have provided the answer: 'bottle' to my question, now enrich it a little bit, no more than 3 sentences."
        system.messaging.post("speech_recognized", msg)
