# dash_app.py

import json
import logging
import argparse
import threading
import queue

import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
import websocket  # We're using websocket-client library here

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

app = dash.Dash(__name__)

# Global variables
ws_app = None
message_queue = queue.Queue(maxsize=5)

app.layout = html.Div([
    html.H1("Dash WebSocket Client with DataTable"),
    dcc.Input(id='input-box', type='text', placeholder='Enter message'),
    html.Button('Send', id='send-button'),
    html.Div(id='output-div'),
    dash_table.DataTable(
        id='data-table',
        columns=[{"name": i, "id": i} for i in ["Exchange", "Symbol", "Price", "Volume"]],
        data=[],
        style_table={'height': '300px', 'overflowY': 'auto'}
    ),
    dcc.Store(id='websocket-store'),
    dcc.Interval(id='interval-component', interval=500, n_intervals=0)
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
    ws_app = websocket.WebSocketApp(f"ws://{WEBSOCKET_HOST}:{WEBSOCKET_PORT}",
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close,
                                    on_open=on_open)
    ws_app.run_forever()

# Start WebSocket connection in a separate thread
threading.Thread(target=run_websocket, daemon=True).start()

@app.callback(
    Output('websocket-store', 'data'),
    Input('send-button', 'n_clicks'),
    State('input-box', 'value'),
    prevent_initial_call=True
)
def send_message(n_clicks, value):
    if n_clicks and value and ws_app and ws_app.sock and ws_app.sock.connected:
        try:
            ws_app.send(json.dumps({"type": "message", "content": value}))
            logger.info(f"Sent message: {value}")
            return {"type": "sent", "content": value}
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return {"type": "error", "content": str(e)}

@app.callback(
    [Output('output-div', 'children'),
     Output('data-table', 'data')],
    Input('interval-component', 'n_intervals')
)
def update_from_queue(n):
    logger.debug("###################################Checking for message")
    if not message_queue.empty():
        message = message_queue.get()
        logger.debug(f"Received message: {message}")
        try:
            data = json.loads(message)
            if data["type"] == "response":
                logger.debug("Output-div: Received response")
                return f"{data['content']}", dash.no_update
            elif data["type"] == "table_data":
                df = pd.DataFrame(data['content'])
                return dash.no_update, df.to_dict('records')
        except json.JSONDecodeError:
            logger.error(f"Failed to decode message: {message}")
            return f"Received invalid message format: {message}", dash.no_update
    return dash.no_update, dash.no_update

if __name__ == '__main__':
    logger.info(f"Connecting to WebSocket server at ws://{WEBSOCKET_HOST}:{WEBSOCKET_PORT}")
    app.run_server(debug=True, host='0.0.0.0', port=8050)