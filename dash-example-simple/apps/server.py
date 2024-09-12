# main_app.py - Claude Version 5.1

import asyncio
import websockets
import json
import logging
import random
import argparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Parse command line arguments
parser = argparse.ArgumentParser(description="WebSocket Server")
parser.add_argument('--port', type=int, default=5000, help='WebSocket server port')
args = parser.parse_args()

WEBSOCKET_HOST = 'localhost'
WEBSOCKET_PORT = args.port

connected = set()

# Simulated data for the table
table_data = [
    {"Exchange": "Binance", "Symbol": "BTC/USDT", "Price": 50000, "Volume": 100},
    {"Exchange": "Coinbase", "Symbol": "ETH/USDT", "Price": 3000, "Volume": 200},
    {"Exchange": "Kraken", "Symbol": "ADA/USDT", "Price": 2, "Volume": 5000},
]

async def update_table_data():
    while True:
        for row in table_data:
            row["Price"] += random.uniform(-100, 100)
            row["Volume"] += random.uniform(-1000, 1000)
        
        if connected:  # Only send updates if there are connected clients
            message = json.dumps({"type": "table_data", "content": table_data})
            websockets.broadcast(connected, message)
        
        await asyncio.sleep(1)  # Update every second

async def handle_websocket(websocket):
    logger.info("New WebSocket connection")
    connected.add(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)
            if data['type'] == 'message':
                response = {"type": "response", "content": f"Received: {data['content']}"}
                await websocket.send(json.dumps(response))
    except websockets.exceptions.ConnectionClosed:
        logger.info("WebSocket connection closed")
    finally:
        connected.remove(websocket)

async def main():
    server = await websockets.serve(
        handle_websocket, 
        WEBSOCKET_HOST, 
        WEBSOCKET_PORT,
        process_request=process_request
    )
    logger.info(f"WebSocket server started on {WEBSOCKET_HOST}:{WEBSOCKET_PORT}")
    
    update_task = asyncio.create_task(update_table_data())
    
    await server.wait_closed()
    update_task.cancel()
    try:
        await update_task
    except asyncio.CancelledError:
        pass

async def process_request(path, headers):
    if "Origin" in headers:
        headers["Access-Control-Allow-Origin"] = headers["Origin"]
    return None

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Received exit signal (CTRL+C)")