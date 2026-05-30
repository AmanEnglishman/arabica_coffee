from django.contrib import admin
from apps.printing.models import PrintJob


@admin.register(PrintJob)
class PrintJobAdmin(admin.ModelAdmin):
    list_display  = ("id", "order_id", "status", "printer_identifier", "created_at", "processed_at")
    list_filter   = ("status", "printer_identifier")
    search_fields = ("order__id",)
    readonly_fields = ("receipt_text", "created_at", "processed_at")
