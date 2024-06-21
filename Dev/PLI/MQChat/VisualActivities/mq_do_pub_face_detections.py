"""
Add a short description of your script here

See https://docs.engineeredarts.co.uk/ for more information
"""
FaceDetectPub = system.import_library('../mq_face_detection_pub.py').MQFaceDetectPub
common = system.import_library('../mq_common.py')
encoding = common.encoding


class Activity:
    def on_start(self):
        self.face_detection_pub = FaceDetectPub()

    def on_stop(self):
        self.face_detection_pub = None

    async def on_message(self, channel, message: list):
        # todo make sure message is a list of byte object
        if channel == 'pub_face_detection':
            probe('face detect: ', message)
            probe('type msg: ', type(message))
            # system.messaging.post('send_frame', '')
            await self.face_detection_pub.pub_face_detection_data([str(m).encode(encoding) for m in message])

    def on_pause(self):
        pass

    def on_resume(self):
        pass

    # @system.tick(fps=10)
    # def on_tick(self):
    #     pass
