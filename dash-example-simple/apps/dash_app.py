# dash_app.py

import json
import logging
import argparse

import dash
import pandas as pd
from dash import dash_table, dcc, html
from dash.dependencies import Input, Output, State
from dash_extensions import WebSocket

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Parse command line arguments
parser = argparse.ArgumentParser(description="Dash WebSocket Client")
parser.add_argument('--port', type=int, default=5000, help='WebSocket server port')
args = parser.parse_args()

WEBSOCKET_HOST = 'localhost'
WEBSOCKET_PORT = args.port

app = dash.Dash(__name__)

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
    WebSocket(url=f"ws://{WEBSOCKET_HOST}:{WEBSOCKET_PORT}", id="ws")
])

@app.callback(
    Output("ws", "send"),
    Input('send-button', 'n_clicks'),
    State('input-box', 'value'),
    prevent_initial_call=False
)
def send_message(n_clicks, value):
    if n_clicks:
        logger.info(f"Sending message: {value}")
        return json.dumps({"type": "message", "content": value})

@app.callback(
    Output('output-div', 'children'),
    Input("ws", "message")
)
def update_output(message):
    if message is None:
        return "No messages received yet."
    data = json.loads(message["data"])
    if data["type"] == "response":
        return f"Received: {data['content']}"
    return dash.no_update

@app.callback(
    Output('data-table', 'data'),
    Input("ws", "message")
)
def update_table(message):
    if message is None:
        return []
    data = json.loads(message["data"])
    if data["type"] == "table_data":
        df = pd.DataFrame(data['content'])
        return df.to_dict('records')
    return dash.no_update

if __name__ == '__main__':
    logger.info(f"Connecting to WebSocket server at ws://{WEBSOCKET_HOST}:{WEBSOCKET_PORT}")
    app.run_server(debug=True, host='0.0.0.0', port=8050)