"""
start all relevant visual activities

See https://docs.engineeredarts.co.uk/ for more information
"""
UTILS = system.import_library('../../HB3/Utils.py')

SCRIPTS = [
    # '../mq_do_pub_vcap.py',
    'do_nlp_tasks.py',
    # '../mq_do_pub_face_detections.py',

]


class Activity:
    def on_start(self):
        for script_path in SCRIPTS:
            UTILS.start_other_script(system, script_path)

    def on_stop(self):
        for script_path in reversed(SCRIPTS):
            UTILS.stop_other_script(system, script_path)
        pass

    def on_pause(self):
        pass

    def on_resume(self):
        pass

    @system.tick(fps=10)
    def on_tick(self):
        pass

