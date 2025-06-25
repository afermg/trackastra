import numpy
import orjson
import torch
from fastapi import FastAPI, Request, Response
from trackastra.model import Trackastra
from trackastra.tracking import graph_to_edge_table

app = FastAPI()
device = "cuda" if torch.cuda.is_available() else "cpu"
model = Trackastra.from_pretrained("general_2d", device=device)


@app.post("/process")
async def process_one(request: Request) -> Response:
    # Convert list to numpy array
    imgs, masks = numpy.asarray(orjson.loads(await request.body()))
    # Track both matrices

    # Track the cells
    track_graph = model.track(
        imgs, masks, mode="greedy"
    )  # or mode="ilp", or "greedy_nodiv"

    return Response(
        orjson.dumps(graph_to_edge_table(track_graph).to_dict(orient="records")),
        media_type="application/json",
    )
