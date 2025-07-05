"""
Request/Reply is used for synchronous communications where each question is responded with a single answer,
for example remote procedure calls (RPCs).
Like Pipeline, it also can perform load-balancing.
This is the only reliable messaging pattern in the suite, as it automatically will retry if a request is not matched with a response.

"""

import json

import pynng

DATE = "DATE"

address = "ipc:///tmp/reqrep.ipc"


def node1():
    with pynng.Req0() as sock:
        sock.dial(address)
        print(f"NODE1: SENDING MODEL REQUEST")
        parameters = {"model_name": "general_2d"}
        packet_out = json.dumps(parameters).encode()

        sock.send(packet_out)
        msg = sock.recv_msg()
        print(f"NODE1: RECEIVED DATE {msg.bytes.decode()}")


node1()
