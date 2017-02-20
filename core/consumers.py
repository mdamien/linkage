from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http

from core.models import Graph

# Connected to websocket.connect
@channel_session_user_from_http
def ws_add(message, graph_pk):
    print('adding user', message.user, message.user.pk, 'to graph', graph_pk)
    graph = Graph.objects.get(pk=int(graph_pk))
    if graph.user.pk != message.user.pk:
        message.reply_channel.send({"accept": False})
        return
    print('user added')
    message.reply_channel.send({"accept": True})
    message.channel_session['graph_pk'] = graph_pk
    Group("result-%s" % graph_pk).add(message.reply_channel)

@channel_session_user
def ws_disconnect(message):
    if 'graph_pk' in message.channel_session:
        Group("result-%s" % message.channel_session['graph_pk']).discard(message.reply_channel)
