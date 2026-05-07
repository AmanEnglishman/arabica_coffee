from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from apps.order.crm_services import get_staff_membership, serialize_active_orders


class CafeOrdersConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.membership = await database_sync_to_async(get_staff_membership)(
            self.scope["user"]
        )
        if self.membership is None:
            await self.close(code=4403)
            return

        self.group_name = f"cafe_orders_{self.membership.cafe_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send_orders()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def orders_changed(self, event):
        await self.send_orders()

    async def send_orders(self):
        orders = await database_sync_to_async(serialize_active_orders)(
            self.membership.cafe
        )
        await self.send_json(
            {
                "type": "orders.snapshot",
                "orders": orders,
            }
        )
