from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http

from core.models import Graph


@channel_session_user_from_http
def ws_add(message):
    message.reply_channel.send({"accept": True})
    Group("jobs-%d" % message.user.pk).add(message.reply_channel)


@channel_session_user
def ws_disconnect(message):
    Group("jobs-%d" % message.user.pk).discard(message.reply_channel)
