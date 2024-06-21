"""
I am not sure why my changes are lost, so I create this script functioning like
"mq_do_visual_tasks.py" that I created yestoday.

See https://docs.engineeredarts.co.uk/ for more information
"""

VTaskDealer = system.import_library('../mq_visual_task_dealer.py').VTaskDealer
common = system.import_library('../mq_common.py')
encoding = common.encoding
VisualTasks = common.VisualTasks
ResponseCode = common.ResponseCode

HUMAN_ACTION_QUEUE = []


def on_vqa_resp(response):
    if response[0] == 'None':
        system.messaging.post("tts_say", ["sorry, could you please repeat your question?", 'EN'])
        return
    msg = f"There is {response[0]} in front of you."

    system.messaging.post("speech_recognized", [msg, "EN"])
    # system.messaging.post("tts_say", [response[0], "EN"])


def on_face_recog(response):
    name = response[0]
    if name == 'None':
        system.messaging.post("tts_say", ["sorry, could you please repeat your question?", 'EN'])
        system.messaging.post("play_sequence", 'Chat Expressions.dir/Chat_G2_Happy_1.project')
        return
    msg = f"I am {name}, how is everything going?"
    system.messaging.post("speech_recognized", [msg, "EN"])
    system.messaging.post("play_sequence", 'Chat Expressions.dir/Chat_G2_Happy_1.project')


def on_vrec_resp(response):
    action = response[0]
    if action == 'None':
        system.messaging.post("tts_say", ['sorry, could you please repeat your question?', 'EN'])
        return
    system.messaging.post("tts_say", [f'the action is recognized as {action}', "EN"])


def on_vrec_posegen_resp(response):  # [human_action, anim.project] TODO generate poses
    action = response[0]
    if action == 'None':
        system.messaging.post("tts_say", ['sorry, could you please repeat your question?', 'EN'])
        system.messaging.post("play_sequence", 'Chat Expressions.dir/Chat_G2_Happy_1.project')
        return

    # HUMAN_ACTION_QUEUE.append(response[0])
    msg = f"i am {action}, could you please give an approapriate response to this? Remember to mention the phrase: {action} in your answer."
    system.messaging.post("speech_recognized", [msg, "EN"])  # wait until the animtion is finished
    sequence = response[1]
    print(f'trigger play sequence {sequence}')
    system.messaging.post(
        "play_sequence", sequence
    )

    # msg = f"I am {response[0]}, could you please speak this action out, and give an approapriate response to this?"
    # system.messaging.post("speech_recognized", [msg, "EN"]) # wait until the animtion is finished
    # print(f'anim: {response[1:]}')
    # SEQUENCE_QUEUE.append(response[1])
    # system.messaging.post(
    #         "play_sequence", "Chat Expressions.dir/Chat_G2_Confused_1.project"
    #     )
    # TODO apply pose


def on_emorec_resp(response):
    emotion = response[0]
    if emotion == 'None':
        # system.messaging.post("tts_say", ['sorry, let me observe ', 'EN'])
        return
    system.messaging.post("tts_say", [f'the emotion is recognized as {emotion}', 'EN'])


RESP_DISPATCHER = {
    VisualTasks.VQA: on_vqa_resp,
    VisualTasks.FaceRecognition: on_face_recog,
    VisualTasks.VideoRecognition: on_vrec_resp,
    VisualTasks.VideoRecogPoseGen: on_vrec_posegen_resp,
    VisualTasks.EmoRecognition: on_emorec_resp,

}


class Activity:
    def on_start(self):
        # action = 'exercising arm'#'drinking' #'applying cream' #'clapping' # 'doing laundary'
        # # system.messaging.post("tts_say", [f'I see you are {action}', "EN"])
        # msg = f"i am {action}, could you please give an approapriate response to this? Remember to mention the phrase: {action} in your answer"
        # system.messaging.post("speech_recognized", [msg, "EN"]) # wait until the animtion is finished

        HUMAN_ACTION_QUEUE = []
        # on_vrec_posegen_resp(['walking the dog', "Mouth Neutral"])
        self.vtask_dealer = VTaskDealer()

    def on_stop(self):
        HUMAN_ACTION_QUEUE = []
        self.vtask_dealer = None

    def on_response(self, response, task_query):  # TODO refine the answer use GPT
        res_code, ans = response[0], response[1:]
        # res code: 1, <class 'str'>, Penny, <class 'str'>
        # print(f'response : {response}, rescode: {res_code}, ans: {ans}')
        # print(f'res code: {res_code}, {type(res_code)}, {ans}, {type(ans)}')
        if int(res_code) == ResponseCode.KeepSilent:
            return  # if keep silent then do nothing
        task_type = task_query[0]
        RESP_DISPATCHER[task_type](ans)

    async def on_message(self, channel, message: list):
        if channel == 'deal_vtasks':
            print('do visual tasks on message: ', message)
            print('=====')
            # print('is instance bytes? ', isinstance(message[0], bytes), type(message[0]))
            assert (isinstance(message[0], bytes), 'message should be a list of bytes-like object')
            resp = await self.vtask_dealer.deal_visual_task(*message)
            # if resp[0] == b'None':
            #     return
            self.on_response([item.decode(encoding) for item in resp], [item.decode(encoding) for item in message])
        # elif channel == 'tts_stop':
        #     print('tts stop!!!!')
        #     pass

    def on_pause(self):
        pass

    def on_resume(self):
        pass

    @system.tick(fps=1)
    def on_tick(self):
        return
        # probe('type state: ', type(system.unstable.state_engine._state))
        # probe('len activities: ', len(system.unstable.state_engine._state.activities))  # 36
        # probe('type activities: ', type(system.unstable.state_engine._state.activities)) # dic_values
        sequence_running = False
        for activity in system.unstable.state_engine._state.activities:
            # probe('type activity: ', type(activity)) # Activity
            # probe('activity: ', activity)
            if activity.properties is None:
                continue
            file_path = activity.properties.get("file_path")
            if file_path is not None:
                sequence_running = True
                break
            probe('file_path', file_path)
        if not sequence_running and HUMAN_ACTION_QUEUE:
            action = HUMAN_ACTION_QUEUE.pop(0)
            msg = f"i am {action}, could you please give an approapriate response to this? Remember to mention the phrase: {action} in your answer"
            system.messaging.post("speech_recognized", [msg, "EN"])  # wait until the animtion is finished
            pass
