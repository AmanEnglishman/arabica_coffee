from django.db import models
from apps.order.models.code import Order


class PrintJob(models.Model):
    STATUS_PENDING    = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_PRINTED    = "printed"
    STATUS_FAILED     = "failed"

    STATUS_CHOICES = [
        (STATUS_PENDING,    "Ожидает"),
        (STATUS_PROCESSING, "Печатается"),
        (STATUS_PRINTED,    "Напечатан"),
        (STATUS_FAILED,     "Ошибка"),
    ]

    order              = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="print_jobs")
    receipt_text       = models.TextField()
    status             = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    error_message      = models.TextField(blank=True, null=True)
    printer_identifier = models.CharField(max_length=100, default="default")
    created_at         = models.DateTimeField(auto_now_add=True)
    processed_at       = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "printing"
        ordering = ["-created_at"]

    def __str__(self):
        return f"PrintJob #{self.id} order={self.order_id} [{self.status}]"
