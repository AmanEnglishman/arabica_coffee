from twilio.rest import Client
from django.conf import settings

# TEMPORARY STUB: Twilio calls are disabled.
# Use code "111111" to always pass verification.
# Remove this stub logic and restore original when Twilio access is restored.
_STUB_CODE = "111111"


def send_verification_code(phone_number: str):
    return True


def check_verification_code(phone_number: str, code: str):
    if code == _STUB_CODE:
        return True
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    result = client.verify.v2.services(settings.TWILIO_VERIFY_SERVICE_SID).verification_checks.create(
        to=phone_number,
        code=code
    )
    return result.status == "approved"
