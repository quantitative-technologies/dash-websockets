# `dash-websockets` with `docker`

These examples demonstrate using the `dash-websockets` dash extension with dockers. 

In all the examples, the servers are run by the docker via `uvicorn` and the clients are run via `gunicorn`. 

The dockers can be started with

```console
docker compose up --build
```

Then the dash app can be viewed by pointing a brower `<ip_address>:8050` where `ip_address=localhost` when run locally, 
or else it could be a server adddress.

## `dash-example-real-time_streaming_data`

This is a dockerized version of the [original code](https://www.dash-extensions.com/components/websocket) from the `Real-time data streaming` example in the 
 `dash-extensions` documentation, of a graph that updates in real-time. The websocket is served by the `Quart` framework (which the docker exposes with `uvicorn`).

## `dash-example-low_latency_communication`

This is a dockerized version of the [Low latency communication](https://www.dash-extensions.com/components/websocket#:~:text=will%20work%20too.-,Low%20latency%20communication,-As%20the%20websocket) example from the `dash-extensions` documentation, demonstrating two-way communication with the `dash-websockets` extension.

## `dash-example-simple`

This is a simple dash app whith two-way communication as well as a `DataTable` showing real-time updates. 
The server uses the `FastAPI` framework.
