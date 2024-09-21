# dash_app.py

import json

import dash
import pandas as pd
from dash import dash_table, dcc, html
from dash.dependencies import Input, Output, State
from dash_extensions import WebSocket

app = dash.Dash(__name__)
server = app.server

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
    WebSocket(url=f"ws://localhost:5000/ws", id="ws")
])

@app.callback(
    Output("ws", "send"),
    Input('send-button', 'n_clicks'),
    State('input-box', 'value'),
    prevent_initial_call=False
)
def send_message(n_clicks, value):
    """ Send message to the server"""
    if n_clicks:
        return json.dumps({"type": "message", "content": value})

@app.callback(
    Output('output-div', 'children'),
    Input("ws", "message")
)
def update_output(message):
    """ Update displayed output with message received from server"""
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
    """ Update DataTable with data received from server"""
    if message is None:
        return []
    data = json.loads(message["data"])
    if data["type"] == "table_data":
        df = pd.DataFrame(data['content'])
        return df.to_dict('records')
    return dash.no_update

if __name__ == '__main__':
    app.run_server()