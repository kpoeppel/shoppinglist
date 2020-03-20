from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from . import consumers
from django.urls import re_path

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            [
                re_path(r'ws/update/(?P<room_name>\w+)/$', consumers.UpdateConsumer),
            ]
        )
    ),
})
