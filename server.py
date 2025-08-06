"""Request/Reply is used for synchronous communications where each question is responded with a single answer,
for example remote procedure calls (RPCs).
Like Pipeline, it also can perform load-balancing.
This is the only reliable messaging pattern in the suite, as it automatically will retry if a request is not matched with a response.

"""

import json
import sys
import time

import pynng
import torch
import trio
from loguru import logger
from nahual.serial import deserialize_numpy
from trackastra.model import Trackastra
from trackastra.tracking import graph_to_edge_table

PARAMETERS = {}

address = sys.argv[1]


def setup(
    model: str = "general_2d",
    mode: str = "greedy",
    logfile: str | None = "errors.log",
) -> dict:
    """Set up the tracking model and configuration.

    Parameters
    ----------
    model : str, optional
        The name of the pre-trained model to load. Defaults to "general_2d".
    mode : str, optional
        The mode of operation for the model. Defaults to "greedy".

    Returns
    -------
    dict
        A dictionary containing the device information and configuration parameters.
    """
    if logfile:
        logger.add(logfile)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    processor = Trackastra.from_pretrained(model, device=device)

    PARAMETERS["model"] = model
    PARAMETERS["mode"] = mode

    info = {"device": device, **PARAMETERS}
    logger.debug(f"Model info: {info}")
    return processor, info


async def responder(sock, processor):
    """Asynchronous responder function for handling model setup and data processing.

    This function continuously listens for incoming messages via a socket. It handles two
    modes: initializing a model based on received parameters and processing data using
    an already loaded model.

    Parameters
    ----------
        sock: pynng. (object): The socket object used for receiving and sending messages.

    Returns
    -------
        None: This function does not return a value but sends responses via the socket.

    Raises
    ------
        Exception: If an error occurs during message handling or processing.

    Notes:
        - The function uses JSON for message serialization.
        - The 'setup' function is called to initialize the model.
        - The 'process' function is used to compute results from input data.
    """
    while True:
        if processor is None:
            try:
                msg = await sock.arecv_msg()
                content = msg.bytes.decode()
                parameters = json.loads(content)
                if "model" in parameters:  # Start
                    print("NODE0: RECEIVED REQUEST")
                    processor, info = setup(**parameters)
                    info_str = f"Loaded model with parameters {info}"
                    print(info_str)
                    print("Sending model info back")
                    await sock.asend(json.dumps(info).encode())

                    print("Model loaded. Will wait for data.")
            except Exception as e:
                print(f"Waiting for parameters: {e}")
                time.sleep(1)
        else:
            try:
                # Receive data
                msg = await sock.arecv_msg()
                try:
                    content_np = deserialize_numpy(msg.bytes)
                except Exception as e:
                    logger.debug(f"Invalid data: {e}")
                    await sock.asend(json.dumps("Invalid data").encode())

                print(content_np.shape, content_np.dtype)
                # Add data processing here
                img, masks = content_np
                result = process(img, masks, processor=processor)
                await sock.asend(json.dumps(result).encode())

            except Exception as e:
                print(f"Waiting for data: {e}")


def process(img, masks, processor) -> dict:
    """Process an image and masks to generate a graph-based tracking representation.

    Parameters
    ----------
    img : array-like
        The input image data.
    masks : array-like
        The input masks data.

    Returns
    -------
    dict
        A dictionary containing the edge table representation of the tracking graph.
    """
    try:
        track_graph = processor.track(
            img, masks, **PARAMETERS
        )  # or mode="ilp", or "greedy_nodiv"
        result = graph_to_edge_table(track_graph).to_dict()
    except Exception as e:
        logger.debug(f"Trackastra failed: {e}")
        result = {
            "source_frame": dict(),
            "source_label": dict(),
            "target_frame": dict(),
            "target_label": dict(),
        }

    return result


async def main():
    """Main function for the asynchronous server.

    This function sets up a nng connection using pynng and starts a nursery to handle
    incoming requests asynchronously.

    Parameters
    ----------
    address : str
        The network address to listen on.

    Returns
    -------
    None
    """
    processor = None
    with pynng.Rep0(listen=address, recv_timeout=300) as sock:
        print(f"Server listening on {address}")
        async with trio.open_nursery() as nursery:
            nursery.start_soon(responder, sock, processor)


if __name__ == "__main__":
    try:
        trio.run(main)
    except KeyboardInterrupt:
        # that's the way the program *should* end
        pass
