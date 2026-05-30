from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

PRINTER_GROUP = "printers"


def broadcast_print_job(job):
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    async_to_sync(channel_layer.group_send)(
        PRINTER_GROUP,
        {
            "type": "print.job",
            "job_id": job.id,
            "order_id": job.order_id,
            "receipt_text": job.receipt_text,
            "created_at": job.created_at.isoformat(),
        },
    )
