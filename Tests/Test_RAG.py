class Activity:
    def on_start(self):
        msg = "what's the weather like today?"
        # msg = f"You have provided the answer: 'bottle' to my question, now enrich it a little bit, no more than 3 sentences."
        system.messaging.post("speech_recognized", msg)
