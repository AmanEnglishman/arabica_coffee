import json
import urllib.parse

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings

from apps.printing.models import PrintJob
from apps.printing.services.broadcast import PRINTER_GROUP


class PrinterConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        if not self._is_authenticated():
            await self.close(code=4403)
            return

        await self.channel_layer.group_add(PRINTER_GROUP, self.channel_name)
        await self.accept()
        await self._send_pending_jobs()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(PRINTER_GROUP, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data or "{}")
        except json.JSONDecodeError:
            return

        if data.get("type") == "print_status":
            await self._handle_status_update(data)

    # ── Channel layer event ────────────────────────────────────────────────────

    async def print_job(self, event):
        await self.send(text_data=json.dumps({
            "type": "print_job",
            "job_id": event["job_id"],
            "order_id": event["order_id"],
            "receipt_text": event["receipt_text"],
            "created_at": event["created_at"],
        }))

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _is_authenticated(self):
        qs = self.scope.get("query_string", b"").decode()
        params = urllib.parse.parse_qs(qs)
        token = params.get("token", [None])[0]
        expected = getattr(settings, "PRINTER_WS_TOKEN", None)
        return bool(expected and token == expected)

    async def _send_pending_jobs(self):
        jobs = await database_sync_to_async(
            lambda: list(
                PrintJob.objects.filter(status=PrintJob.STATUS_PENDING)
                .order_by("created_at")
            )
        )()
        for job in jobs:
            await self.send(text_data=json.dumps({
                "type": "print_job",
                "job_id": job.id,
                "order_id": job.order_id,
                "receipt_text": job.receipt_text,
                "created_at": job.created_at.isoformat(),
            }))

    @database_sync_to_async
    def _handle_status_update(self, data):
        from django.utils import timezone
        job_id = data.get("job_id")
        new_status = data.get("status")
        error = data.get("error", "")

        if not job_id or new_status not in (
            PrintJob.STATUS_PROCESSING,
            PrintJob.STATUS_PRINTED,
            PrintJob.STATUS_FAILED,
        ):
            return

        PrintJob.objects.filter(id=job_id).update(
            status=new_status,
            error_message=error or None,
            processed_at=timezone.now(),
        )
