"""Do Visual Question Answering."""

import io
import asyncio
from typing import Optional

import aiohttp
from PIL import Image

CONFIG = system.import_library("../../../../Config/HB3.py").CONFIG


class VqaClient:
    VQA_SERVER_ADDRESS = CONFIG["VQA_SERVER_ADDRESS"]

    def __init__(self):
        self.server = None
        self.vqa_server_address = self.__class__.VQA_SERVER_ADDRESS
        if self.VQA_SERVER_ADDRESS is not None:
            try:
                self.server = aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=2)
                )
            except Exception:
                self.__class__.VQA_SERVER_ADDRESS = None
        self._vc_socket = system.unstable.owner.subscribe_to(
            "ipc:///run/tritium/sockets/video_capture_data",
            self._on_video_capture_data,
            description="video frames",
            conflate=True,
        )
        self.vcap_data = None

    def __del__(self):
        try:
            import zmq
        except ImportError:
            pass
        else:
            if self._vc_socket:
                self._vc_socket.setsockopt(zmq.LINGER, 0)
        if hasattr(self, "_vc_socket"):
            system.unstable.owner._stop_listening_to(self._vc_socket)
        self._vc_socket = None

    def _on_video_capture_data(self, data):
        self.vcap_data = data

    async def vqa(self, query: str) -> Optional[str]:
        """Query the current view of the robot with a natural language question.

        This function has no concept of the names of each person in the image.
        The function returns None if the vqa call did not work for some reason.

        #REQUIRES_SUBSEQUENT_FUNCTION_CALLS

        Args:
            query: The query to ask to the current view e.g. how many fingers is the person holding up

        Returns:
            The answer to the query
        """
        if self.server is not None:
            if self.vcap_data is None or self.vqa_server_address is None:
                return None
            # TODO: Use the sensors section of stash not this.
            res = {
                w * h * 3: (w, h) for w, h in [(1920, 1080), (1280, 720), (640, 480)]
            }[len(self.vcap_data)]
            image = Image.frombytes("RGB", res, self.vcap_data)

            arr = io.BytesIO()
            image.save(arr, format="PNG")
            arr.seek(0)

            # Prepare a message for the face rec server
            data = aiohttp.FormData()
            data.add_field("query", query, content_type="multipart/form-data")
            data.add_field("image", arr, content_type="multipart/form-data")
            try:
                async with self.server.post(self.vqa_server_address, data=data) as resp:
                    response = await resp.json()
                    return response["response"]
            except Exception as e:
                print(e)
                return None
        else:
            return None


# vqa_client = VqaClient()
# vqa = vqa_client.vqa