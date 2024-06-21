"""
See https://docs.engineeredarts.co.uk/ for more information
"""


class Activity:
    def on_start(self):
        pass

    def on_stop(self):
        pass

    async def on_message(self, channel, message: list):
        pass
        # todo make sure message is a list of byte object

    def on_pause(self):
        pass

    def on_resume(self):
        pass