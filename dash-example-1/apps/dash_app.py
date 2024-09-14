import argparse
import logging
from dash_extensions import WebSocket
from dash_extensions.enrich import html, dcc, Output, Input, DashProxy
import dash

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(filename)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

DASH_HOST_DEFAULT = '0.0.0.0'
WEBSOCKET_HOST_DEFAULT = 'websocket-server'
WEBSOCKET_PORT_DEFAULT = 5000

# Parse command line arguments
parser = argparse.ArgumentParser(description="Dash WebSocket Client")
parser.add_argument('--dash-host', type=str, default=DASH_HOST_DEFAULT, help=f'Dash app host. Default: {DASH_HOST_DEFAULT}')
parser.add_argument('--host', type=str, default=WEBSOCKET_HOST_DEFAULT, help=f'WebSocket server host. Default: {WEBSOCKET_HOST_DEFAULT}')
parser.add_argument('--port', type=int, default=WEBSOCKET_PORT_DEFAULT, help=f'WebSocket server port. Default: {WEBSOCKET_PORT_DEFAULT}')
args = parser.parse_args()

app = DashProxy(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    WebSocket(id="ws", url=f"ws://{args.host}:{args.port}/random_data"),
    dcc.Graph(id="graph"),
    html.Div(id="connection-status"),
    html.Div(id="data-received")
])

@app.callback(Output("connection-status", "children"), Input("ws", "state"))
def update_connection_state(state):
    logger.debug(f"WebSocket connection state: {state}")
    return f"WebSocket connection state: {state}"

@app.callback(Output("data-received", "children"), Input("ws", "message"))
def display_message(message):
    logger.debug(f"Received WebSocket message: {message}")
    return f"Last received data: {message}"

update_graph = """
function(msg) {
    console.log("update_graph called with message:", msg);
    if(!msg){
        console.log("No message received");
        return {};
    }
    console.log("Received message:", msg.data);
    const data = JSON.parse(msg.data);
    return {data: [{y: data, type: "scatter"}]};
}
"""

app.clientside_callback(update_graph, Output("graph", "figure"), Input("ws", "message"))

if __name__ == "__main__":
    logger.info("Starting Dash app")
    logger.info(f"Connecting to WebSocket server at ws://{args.host}:{args.port}/random_data")
    app.run_server(host=args.dash_host, port=8050, debug=True)