from channels.routing import route, include

from core.consumers import ws_add, ws_disconnect

job_routing = [
    route("websocket.connect", ws_add),
    route("websocket.disconnect", ws_disconnect),
]

routing = [
    include(job_routing, path=r"^/jobs/"),
]
