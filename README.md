# dash-websockets

Demonstrate issue with the extension.

## `dash-example-1-original`

This is the [original code](https://www.dash-extensions.com/components/websocket) from the `Real-time data streaming` example in the 
 `dash-extensions` documentation.

 ## `dash-example-1`

 This is a dockerized version of `dash-example-1-original`, with additional diagnostics in the client app (`dash_app.py`).

 ## `dash-example-1-no_dash_websockets`

 This is an unpleasant workaround where the websocket is run in a separate thread, and `dcc.Interval` is used to trigger callbacks. 

 ## `dash-example-simple` and `dash-example-simple-no_dash_websockets`

 Another simple client demonstrating these issues, that renders a `DataTable` rather than a graph.

