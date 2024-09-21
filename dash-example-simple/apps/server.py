# server.py
import asyncio
import json
import logging
import random
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simulated data for the table
table_data = [
    {"Exchange": "Binance", "Symbol": "BTC/USDT", "Price": 50000, "Volume": 100},
    {"Exchange": "Coinbase", "Symbol": "ETH/USDT", "Price": 3000, "Volume": 200},
    {"Exchange": "Kraken", "Symbol": "ADA/USDT", "Price": 2, "Volume": 5000},
]

# WebSocket connections
connected_clients = set()

async def update_table_data():
    while True:
        for row in table_data:
            row["Price"] += random.uniform(-100, 100)
            row["Volume"] += random.uniform(-1000, 1000)
        
        if connected_clients:  # Only send updates if there are connected clients
            message = json.dumps({"type": "table_data", "content": table_data})
            for client in connected_clients:
                await client.send_text(message)
        
        await asyncio.sleep(1)  # Update every second

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(update_table_data())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    logger.info("New WebSocket connection")
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            if message['type'] == 'message':
                response = {"type": "response", "content": message['content']}
                await websocket.send_text(json.dumps(response))
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")
    finally:
        connected_clients.remove(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)