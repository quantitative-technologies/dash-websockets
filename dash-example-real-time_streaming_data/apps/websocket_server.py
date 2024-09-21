import asyncio
import json
import random
from quart import websocket, Quart

# object called by uvicorn
app = Quart(__name__)

@app.websocket("/random_data")
async def random_data():
    while True:
        output = json.dumps([random.random() for _ in range(10)])
        await websocket.send(output)
        await asyncio.sleep(1)
