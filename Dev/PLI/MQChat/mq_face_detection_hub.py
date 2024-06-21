"""
publish face detection results to backend server

See https://docs.engineeredarts.co.uk/ for more information
"""

import asyncio
from typing import Optional
import io
import time

config = system.import_library('mq_common.py').Config


# face_det_pub_addr = 'tcp://10.126.110.67:6666'  # backed server address


class MQFaceDetectPub:

    def __init__(self):
        super(MQFaceDetectPub, self).__init__()
        print('init mq face detect pub1111')
        print('====================')
        try:
            import zmq
            import zmq.asyncio
            from zmq.asyncio import Context
            context = Context.instance()
            self._pub_socket = context.socket(zmq.PUB)
            # self._pub_socket.setsockopt(zmq.CONFLATE, 1) # will cause data loss
            self._pub_socket.bind(config.face_det_pub_addr)
        except Exception as e:
            print('init face detect pub error222222', str(e))

    def __del__(self):
        print('del mq face detect pub2222!!!')
        print('===============')
        try:
            import zmq
        except ImportError:
            pass
        else:
            if self._pub_socket:
                self._pub_socket.setsockopt(zmq.LINGER, 0)
        self._pub_socket = None

    async def pub_face_detection_data(self, data: list):
        await self._pub_socket.send_multipart(data)
        # self._pub_socket.send(data)  # no
        # await self._pub_socket.send(data) # no
        # await self._pub_socket.send_multipart([data, str(time.time()).encode(encoding)])