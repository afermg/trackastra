# Trackastra Nahual OCI image

The flake builds a reproducible OCI-compatible archive containing the same Nix
closure as the Trackastra Nahual app. Nix is not required at runtime.

```console
nix build .#oci-image
podman load < result                 # or: docker load < result
podman run --rm --name nahual-trackastra \
  --device nvidia.com/gpu=all \
  -p 5555:5555 \
  -v nahual-trackastra-cache:/tmp/nahual \
  nahual/trackastra:local
```

For Docker, replace the CDI option with `--gpus all`. Without a GPU, Trackastra
falls back to CPU. The endpoint defaults to `tcp://0.0.0.0:5555`; a different
NNG endpoint may be supplied as the container argument. The volume persists
pretrained weights and logs.

## Full smoke inference

```console
python3 -m venv .venv
. .venv/bin/activate
pip install 'nahual==0.0.8' numpy
NAHUAL_ADDRESS=tcp://127.0.0.1:5555 python oci/smoke_test.py
```

The test downloads `general_2d`, submits a short moving-object sequence, runs
greedy tracking, and validates the returned edge table.
