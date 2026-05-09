from rest_framework.throttling import AnonRateThrottle


class SendCodeThrottle(AnonRateThrottle):
    rate = "3/10min"
    scope = "send_code"


class VerifyCodeThrottle(AnonRateThrottle):
    rate = "5/10min"
    scope = "verify_code"
