import logging
from dash_extensions import WebSocket
from dash_extensions.enrich import html, dcc, Output, Input, DashProxy
import dash

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = DashProxy(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    WebSocket(id="ws", url="ws://127.0.0.1:5000/random_data"),
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
    app.run_server(host="0.0.0.0", port=8050, debug=True)