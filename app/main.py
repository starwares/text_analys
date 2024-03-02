import time
from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel

from app.model import process, processCollections

app = FastAPI()


class Item(BaseModel):
    message: str
    filters: list = []


class ItemsCollection(BaseModel):
    messages: list
    filters: list = []


@app.post("/")
async def root(data: Item):
    st = time.time()
    return {
        **process(data.message, data.filters),
        "execution": str((time.time() - st) * 1000) + ' ms'
    }


@app.post("/collection")
async def root(data: ItemsCollection):
    st = time.time()

    results = []

    for message in data.messages:
        results.append(processCollections(message))

    return {
        "results": results,
        "execution": str((time.time() - st) * 1000) + ' ms'
    }


@app.post("/summary")
async def root(data: ItemsCollection):
    st = time.time()

    results = []

    for message in data.messages:
        results.append(processCollections(message))

    output = {
        "mood": {
            "neutral": 0,
            "skip": 0,
            "positive": 0,
            "negative": 0,
            "speech": 0,
        },
        "toxicity": {
            "non-toxic": 0,
            "insult": 0,
            "obscenity": 0,
            "threat": 0,
            "dangerous": 0,
        },
    }

    for result in results:
        for k, v in result.items():
            if k in ["mood", "toxicity"]:
                for k2, v2 in v.items():
                    output[k][k2] = (output[k][k2] + v2) / 2

    return {
        **output,
        "execution": str((time.time() - st) * 1000) + ' ms'
    }
