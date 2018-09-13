# -*- coding: utf-8 -*- 
from concurrent import futures
import time
import math
import threading 
import Queue

import grpc
import traceback
import route_guide_pb2
import route_guide_pb2_grpc


_send_queue = Queue.Queue() 
_recv_queue = Queue.Queue()

def get_time():
    return time.strftime("%Y-%m-%d %X", time.localtime())

# 因为遍历request_iterator 会block, 这里创建线程处理
def recv_thread(request_iterator, context):
    print("Recv thread. ",threading.currentThread())
    try:
        for game_msg in request_iterator:
            print(get_time(), "recv client request. ", game_msg)
            _recv_queue.put_nowait(game_msg)
    except grpc.RpcError:
        print(get_time(), "error for client.", context.peer_identity_key())

# 使用继承方式实现服务
class RouteGuideServicer(route_guide_pb2_grpc.RouteGuideServicer):
    """Provides methods that implement functionality of route guide server."""

    def __init__(self):
        pass

    def RouteChat(self, request_iterator, context):
        th = threading.Thread(target=recv_thread, args = (request_iterator, context))
        th.daemon = False
        th.start()

        # 这个回调的线程将被下面hold,消耗了线程池
        # 本例子中只能有10个
        print("Sending(RouteChat) thread. ",threading.currentThread())
        while(True):
            to_client_msg = _send_queue.get()
            print("send to client. ", to_client_msg)
            yield to_client_msg

def serve():
    # 预分配线程10个
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # 注册服务 
    route_guide_pb2_grpc.add_RouteGuideServicer_to_server(
        RouteGuideServicer(), server)
    # 监听端口
    server.add_insecure_port('[::]:50051')
    server.start()

    print("main thread. ",threading.currentThread())
    try:
        while True:
            # 主线程不停的产生下行
            time.sleep(1)
            new_msg_to_client = route_guide_pb2.RouteNote(message="come from server %s"%get_time(), location=route_guide_pb2.Point(latitude=100, longitude=99))
            _send_queue.put_nowait(new_msg_to_client)

    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
