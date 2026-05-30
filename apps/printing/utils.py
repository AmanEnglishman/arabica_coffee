from apps.printing.models import PrintJob
from apps.printing.services.receipt_formatter import format_receipt
from apps.printing.services.broadcast import broadcast_print_job


def create_and_broadcast_print_job(order, printer_identifier="default"):
    receipt = format_receipt(order)
    job = PrintJob.objects.create(
        order=order,
        receipt_text=receipt,
        printer_identifier=printer_identifier,
    )
    broadcast_print_job(job)
    return job
