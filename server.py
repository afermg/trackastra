"""
Request/Reply is used for synchronous communications where each question is responded with a single answer,
for example remote procedure calls (RPCs).
Like Pipeline, it also can perform load-balancing.
This is the only reliable messaging pattern in the suite, as it automatically will retry if a request is not matched with a response.

"""

import json
import time

import pynng
import torch
import trio
from trackastra.model import Trackastra
from trio.to_thread import run_sync

MODEL = None
PARAMETERS = {}

address = "ipc:///tmp/reqrep.ipc"


def setup(model_name: str = "general_2d", mode: str = "greedy") -> dict:
    global MODEL
    device = "cuda" if torch.cuda.is_available() else "cpu"
    MODEL = Trackastra.from_pretrained(model_name, device=device)

    PARAMETERS["mode"] = mode

    info = {"model": model_name, "device": device, **PARAMETERS}
    return info


async def wait_for_data():
    while True:
        print("waiting for data")
        time.sleep(2)


async def responder(sock):
    while True:
        try:
            msg = await sock.arecv_msg()
            content = msg.bytes.decode()
            try:
                parameters = json.loads(content)
            except Exception as e:
                print("ERROR: {e}")
            # first_byte =
            # content =
            if "model_name" in parameters:  # Start
                print("NODE0: RECEIVED DATE REQUEST")
                info = setup(**parameters)
                info_str = f"Loaded model with parameters {info}"
                print("Sending model info back")
                await sock.asend(info_str.encode())

                break
        except Exception as e:
            print(f"Waiting for parameters: {e}")
            time.sleep(1)

    while True:  # Analysis loop
        try:
            msg = await sock.arecv_msg()
            content = msg.bytes.decode()
            # Add data processing here
        except Exception as e:
            print(f"Waiting for data: {e}")


async def main():
    with pynng.Rep0(listen=address, recv_timeout=300) as rep:
        async with trio.open_nursery() as nursery:
            nursery.start_soon(responder, rep)


if __name__ == "__main__":
    try:
        trio.run(main)
    except KeyboardInterrupt:
        # that's the way the program *should* end
        pass
