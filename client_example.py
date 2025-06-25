"""
Example for how to use the trackastra HTTPS client.

Run server from the root folder as `fastapi dev server.py`.
"""

import orjson
import requests
from trackastra.data import example_data_bacteria

# Serialize a numpy array using orjson (faster json serialization)
serial_numpy = orjson.dumps(example_data_bacteria(), option=orjson.OPT_SERIALIZE_NUMPY)
response = requests.post(
    "http://localhost:8000/process",
    serial_numpy,
)
print(orjson.loads(response.content))
