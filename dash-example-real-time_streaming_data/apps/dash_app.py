from dash_extensions import WebSocket
from dash_extensions.enrich import html, dcc, Output, Input, DashProxy
import dash


# Client-side function (for performance) that updates the graph.
update_graph = """function(msg) {
    if(!msg){return {};}  // no data, just return
    const data = JSON.parse(msg.data);  // read the data
    return {data: [{y: data, type: "scatter"}]}};  // plot the data
"""
# Create small example app.
app = DashProxy(__name__)
app.layout = html.Div(
    [
        WebSocket(id="ws", url="ws://localhost:5000/random_data"),
        dcc.Graph(id="graph"),
    ]
)
app.clientside_callback(
    update_graph, Output("graph", "figure"), Input("ws", "message")
)
# Object called by gunicorn
server = app.server

if __name__ == "__main__":
    app.run_server()
