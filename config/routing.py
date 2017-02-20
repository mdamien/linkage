from channels.routing import route, include

from core.consumers import ws_add, ws_disconnect

result_routing = [
    route("websocket.connect", ws_add, path=r"^/(?P<graph_pk>\d+)/$"),
    route("websocket.disconnect", ws_disconnect),
]

routing = [
    include(result_routing, path=r"^/result"),
]