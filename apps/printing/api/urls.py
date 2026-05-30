from django.urls import path
from apps.printing.api.views import pending_jobs, update_job_status, reprint_order

urlpatterns = [
    path("pending/",                  pending_jobs,       name="printer-pending"),
    path("jobs/<int:job_id>/status/", update_job_status,  name="printer-job-status"),
    path("reprint/<int:order_id>/",   reprint_order,      name="printer-reprint"),
]
