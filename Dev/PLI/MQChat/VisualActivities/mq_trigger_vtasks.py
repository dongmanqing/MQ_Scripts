"""
Add a short description of your script here

See https://docs.engineeredarts.co.uk/ for more information
"""
common = system.import_library('../mq_common.py')
encoding = common.encoding
VisualTasks = common.VisualTasks

# debug only
vfuncs = system.import_library('../GPTFuncCalls/mq_visual_funcs.py')
import time

INSPECTION_TIME = 30  # maintain proactive mode for {INSPECTION_TIME} seconds


class Activity:

    def on_start(self):
        self.task_end_time = time.time() + INSPECTION_TIME
        pass
        # query = b'what is this in this picture?'
        # message = [VisualTasks.VQA.encode(encoding), query]
        # query = b'what am i doing? '
        # message = [VisualTasks.VideoRecognition.encode(encoding), query]
        # utterance = b'hahaha, that is amazing!'
        # message = [VisualTasks.EmoRecognition.encode(encoding), utterance]
        # query = b'do you remember me?'
        # force_recog = b'0'
        # message = [VisualTasks.FaceRecognition.encode(encoding), query, force_recog]

        # self.trigger_vtask(message)

    def trigger_vtask(self, message):
        # system.messaging.post('deal_vtasks', message)
        print('deal task', message)
        system.messaging.post('deal_vtasks', message)

    def on_stop(self):
        pass

    def on_pause(self):
        pass

    def on_resume(self):
        pass

    @system.tick(fps=0.2)
    def on_tick(self):
        return
        if time.time() > self.task_end_time:
            return
        # utterance = b'hahaha, that is amazing!'
        # message = [VisualTasks.EmoRecognition.encode(encoding), utterance]
        # self.trigger_vtask(message)

        query = b'do you remember me?'
        force_recog = b'0'
        message = [VisualTasks.FaceRecognition.encode(encoding), query, force_recog]
        self.trigger_vtask(message)

        # sequence = 'Chat Expressions.dir/Chat_G2_Happy_2.project'
        # sequence = 'Chat Expressions.dir/Chat_G2_Dislike_2.project'
        # system.messaging.post(
        #     "play_sequence", sequence)
        # vfuncs.vqa_func('HGello')
        # system.messaging.post('deal_vtask', [])

        # system.messaging.post('deal_vtasks', [VisualTasks.VideoRecognition.encode(encoding)])
        pass
