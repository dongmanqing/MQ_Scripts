"""
Add a short description of your script here

See https://docs.engineeredarts.co.uk/ for more information
"""
import zmq
import zmq.asyncio
from zmq.asyncio import Context

config = system.import_library('mq_common.py').Config


# # url = 'tcp://10.126.110.67:2006'
# port = 2004
# url = f'tcp://0.0.0.0:{port}'


class VTaskDealer:
    def __init__(self):
        super(VTaskDealer, self).__init__()
        print('init vtask dealer111')
        print('======')
        ctx = Context.instance()
        self._deal_sock = ctx.socket(zmq.DEALER)
        self._deal_sock.setsockopt(zmq.IDENTITY, b'vtask_dealer')
        # self._deal_sock.setsockopt(zmq.CONFLATE, 1) # NOTE, use this will cause some args being swallowed
        self._deal_sock.bind(config.visual_task_addr)
        # self._deal_sock.connect(url)

    def __del__(self):
        print('del vtask dealer222')
        print('=================')
        if self._deal_sock:
            self._deal_sock.setsockopt(zmq.LINGER, 0)
        if hasattr(self, '_deal_sock'):
            self._deal_sock = None

    # TODO check args (should be bytes-like object)
    async def deal_visual_task(self, *args):
        print('deal visual task args: ', args, type(args))
        print('====')
        await self._deal_sock.send_multipart(args)
        # print('deal vtask msg sent!!!')
        resp = await self._deal_sock.recv_multipart()
        # print(f'deal visual task resp: {resp}')
        return resp

# vtask_dealer = VTaskDealer()
