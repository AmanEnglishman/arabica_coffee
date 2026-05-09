from celery import shared_task

from apps.users.utils.twilio import send_verification_code


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=3,
)
def send_verification_code_task(self, phone_number: str):
    return send_verification_code(phone_number)
