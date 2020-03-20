import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import TimeSlot
import datetime

class UpdateConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        print(self.room_name)
        self.user = self.scope["user"]
        self.room_group_name = 'update_%s' % self.room_name
        print(self.channel_layer)
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        _, date, slotnum = text_data_json['id'].split('+')
        ts = TimeSlot(date=datetime.datetime.strptime(date, "%Y-%m-%d").date(),
                      slotnum=slotnum,
                      changedby=self.user.id,
                      entry=text_data_json['value'])
        ts.save()

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'update_message',
                'message': text_data
            }
        )

    async def update_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=message)
