import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    """ Консьюмер для уведомлений администраторам """
    async def connect(self):

        self.admin_id = self.scope['url_route']['kwargs']['room_name'].split('_')[1]
        self.room_admin_name = "admin_"+str(self.admin_id)

        print(self.room_admin_name)

        await self.channel_layer.group_add(
            self.room_admin_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.room_admin_name,
            self.channel_name
        )

    async def admin_notice(self, event):
        """ Кастомная функция для отправки уведомления """
        data = event['data']
        await self.send(text_data=json.dumps({
            'data': data
        }))
