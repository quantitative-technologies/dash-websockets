import asyncio
import websockets
import json
from quart import Quart
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from dash_extensions.enrich import DashProxy, Output, Input
from quart_cors import cors

server = Quart(__name__)
server = cors(server, allow_origin="*")  # Be cautious with CORS in production
app = DashProxy(__name__, server=server, suppress_callback_exceptions=True)

app.layout = html.Div([
    dcc.Graph(id="graph"),
    dcc.Interval(id="interval-component", interval=1000, n_intervals=0),
])

# Global variable to store the latest data
latest_data = []

async def websocket_client():
    uri = "ws://websocket-server:5000/random_data"
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                while True:
                    message = await websocket.recv()
                    global latest_data
                    latest_data = json.loads(message)
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed. Reconnecting...")
            await asyncio.sleep(5)

@app.callback(Output("graph", "figure"), Input("interval-component", "n_intervals"))
def update_graph(n):
    global latest_data
    return go.Figure(data=[go.Scatter(y=latest_data)])

@server.before_serving
async def startup():
    server.websocket_task = asyncio.create_task(websocket_client())

@server.after_serving
async def shutdown():
    server.websocket_task.cancel()
    await server.websocket_task

@server.route("/")
async def hello():
    return "Quart server is running"

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8050)