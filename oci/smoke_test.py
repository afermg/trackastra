#!/usr/bin/env python3
"""End-to-end smoke inference against the Trackastra OCI container."""

import json
import os

os.environ.setdefault("NAHUAL_IPC_TIMEOUT_MS", "900000")

import numpy as np
from nahual.process import dispatch_setup_process


def main() -> None:
    address = os.environ.get("NAHUAL_ADDRESS", "tcp://127.0.0.1:5555")
    setup, process = dispatch_setup_process("trackastra")
    info = setup(
        {"model": "general_2d", "mode": "greedy", "logfile": None},
        address=address,
    )

    rng = np.random.default_rng(42)
    images = rng.normal(0.0, 0.02, size=(4, 128, 128)).astype(np.float32)
    masks = np.zeros_like(images, dtype=np.int32)
    for frame in range(4):
        x0 = 48 + frame * 2
        masks[frame, 48:72, x0 : x0 + 24] = 1
        images[frame][masks[frame] == 1] = 1.0

    result = process(np.stack((images, masks)), address=address)
    expected = {
        "source_frame",
        "source_label",
        "target_frame",
        "target_label",
        "weight",
    }
    assert set(result) == expected, result
    assert len(result["weight"]) >= 3, result
    print(json.dumps({"setup": info, "edges": len(result["weight"])}))


if __name__ == "__main__":
    main()
