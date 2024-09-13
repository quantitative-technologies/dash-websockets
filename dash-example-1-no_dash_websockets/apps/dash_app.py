import argparse
import asyncio
import dash
import logging
import queue
import threading
import json
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from dash_extensions.enrich import DashProxy, Output, Input
import websocket

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Parse command line arguments
parser = argparse.ArgumentParser(description="Dash WebSocket Client")
parser.add_argument('--port', type=int, default=5000, help='WebSocket server port')
args = parser.parse_args()

WEBSOCKET_HOST = 'websocket-server'
WEBSOCKET_PORT = args.port

# server = Quart(__name__)
# server = cors(server, allow_origin="*")  # Be cautious with CORS in production
# app = DashProxy(__name__, server=server, suppress_callback_exceptions=True)

app = Dash(__name__)

message_queue = queue.Queue(maxsize=5)

app.layout = html.Div([
    dcc.Graph(id="graph"),
    dcc.Interval(id="interval-component", interval=1000, n_intervals=0),
])

def on_message(ws, message):
    logger.debug(f"Received message: {message}")
    message_queue.put(message)

def on_error(ws, error):
    logger.error(f"WebSocket error: {error}")

def on_close(ws, close_status_code, close_msg):
    logger.info("WebSocket connection closed")

def on_open(ws):
    logger.info("WebSocket connection opened")

def run_websocket():
    global ws_app
    websocket.enableTrace(True)
    ws_app = websocket.WebSocketApp(f"ws://{WEBSOCKET_HOST}:{WEBSOCKET_PORT}/random_data",
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close,
                                    on_open=on_open)
    ws_app.run_forever()

# Start WebSocket connection in a separate thread
threading.Thread(target=run_websocket, daemon=True).start()

@app.callback(Output("graph", "figure"), Input("interval-component", "n_intervals"))
def update_graph(n):
    if not message_queue.empty():
        message = message_queue.get()
        data = json.loads(message)
        return go.Figure(data=[go.Scatter(y=data)])
    
    return dash.no_update

if __name__ == "__main__":
    logger.info(f"Connecting to WebSocket server at ws://{WEBSOCKET_HOST}:{WEBSOCKET_PORT}")
    app.run_server(debug=True, host='0.0.0.0', port=8050)