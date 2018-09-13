# -*- coding: utf-8 -*- 
from __future__ import print_function

import random
import time
import grpc
import threading 
import Queue


import route_guide_pb2
import route_guide_pb2_grpc

_send_queue = Queue.Queue() 

def make_route_note(message, latitude, longitude):
    return route_guide_pb2.RouteNote(
        message=message,
        location=route_guide_pb2.Point(latitude=latitude, longitude=longitude))


def get_time():
    return time.strftime("%Y-%m-%d %X", time.localtime())

def sending_messages():
    # 这里会消耗线程
    print("sending thread. ",threading.currentThread())
    while(True):
        msg = _send_queue.get()
        print(get_time(), "Sending %s at %s" % (msg.message, msg.location))
        yield msg

_responses = 0
def recv_thread():
    global _responses
    print("recv thread. ",threading.currentThread())
    print("recv thread _responses",_responses)
    print(get_time(), "recv thread is starting...")
    # 等待接收对象创建好 
    while(True):
        if isinstance(_responses, int):
            time.sleep(0.1)
        else:
            print(get_time(), "startting recv...")
            break
   
    # 如果没有消息，每次调用next会被block
    try:
        for response in _responses:
            print(get_time(), "Received message %s at %d,%d" % (response.message, response.location.latitude, response.location.longitude))
    except grpc.RpcError:
        print(get_time(), "server is close!")

def guide_route_chat(stub):
    print("main thread. ",threading.currentThread())
    global _responses
    _responses = stub.RouteChat(sending_messages())
    print("main thread  _responses",_responses)
    # 如果将_responses当作参数给线程，会因为_responses是会block属性导致线程不启动（即使start）
    #th = threading.Thread(target=recv_thread, args = (_responses))
    th = threading.Thread(target=recv_thread)
    th.daemon = False
    th.start()
    
    # 主线程不停产生上行消息
    while(True):
        time.sleep(2)
        to_server_msg = make_route_note("from client message time:%s"%get_time(), 0, 0)
        _send_queue.put_nowait(to_server_msg)
    
def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = route_guide_pb2_grpc.RouteGuideStub(channel)
        guide_route_chat(stub)


if __name__ == '__main__':
    run()
