"""
Add a short description of your script here

See https://docs.engineeredarts.co.uk/ for more information
"""


class Activity:
    def on_start(self):
        pass

    def on_stop(self):
        pass

    def on_pause(self):
        pass

    def on_resume(self):
        pass

    @system.tick(fps=10)
    def on_tick(self):
        pass
