"""
Add a short description of your script here

See https://docs.engineeredarts.co.uk/ for more information
"""
common = system.import_library('../mq_common.py')
VisualTasks = common.VisualTasks
encoding = common.encoding


class Activity:
    def on_start(self):
        system.messaging.post('deal_vtasks', [VisualTasks.VideoRecogPoseGen.encode(encoding)])
        pass

    def on_stop(self):
        pass

    def on_pause(self):
        pass

    def on_resume(self):
        pass

    @system.tick(fps=0.1)
    def on_tick(self):
        pass
        # system.messaging.post('deal_vtasks', [VisualTasks.VideoRecogPoseGen.encode(encoding)])