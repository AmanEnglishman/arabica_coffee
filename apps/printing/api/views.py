from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt

from apps.printing.models import PrintJob
from apps.printing.utils import create_and_broadcast_print_job
from apps.order.models.code import Order


def _check_printer_token(request):
    token = request.headers.get("X-Printer-Token") or request.GET.get("token")
    expected = getattr(settings, "PRINTER_WS_TOKEN", None)
    return bool(expected and token == expected)


@require_GET
def pending_jobs(request):
    if not _check_printer_token(request):
        return JsonResponse({"detail": "Unauthorized"}, status=401)

    jobs = PrintJob.objects.filter(status=PrintJob.STATUS_PENDING).order_by("created_at")
    return JsonResponse([
        {
            "job_id": j.id,
            "order_id": j.order_id,
            "receipt_text": j.receipt_text,
            "created_at": j.created_at.isoformat(),
        }
        for j in jobs
    ], safe=False)


@csrf_exempt
@require_POST
def update_job_status(request, job_id):
    if not _check_printer_token(request):
        return JsonResponse({"detail": "Unauthorized"}, status=401)

    import json
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"detail": "Invalid JSON"}, status=400)

    job = get_object_or_404(PrintJob, id=job_id)
    new_status = data.get("status")

    if new_status not in (PrintJob.STATUS_PROCESSING, PrintJob.STATUS_PRINTED, PrintJob.STATUS_FAILED):
        return JsonResponse({"detail": "Invalid status"}, status=400)

    job.status = new_status
    job.error_message = data.get("error") or None
    job.processed_at = timezone.now()
    job.save(update_fields=["status", "error_message", "processed_at"])

    return JsonResponse({"ok": True})


@csrf_exempt
@require_POST
def reprint_order(request, order_id):
    """CRM retry: create new PrintJob for existing order."""
    from apps.order.crm_services import get_staff_membership
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Unauthorized"}, status=403)
    membership = get_staff_membership(request.user)
    if not membership:
        return JsonResponse({"detail": "Нет доступа"}, status=403)

    order = get_object_or_404(Order, id=order_id, cafe=membership.cafe)
    job = create_and_broadcast_print_job(order)
    return JsonResponse({"ok": True, "job_id": job.id})
