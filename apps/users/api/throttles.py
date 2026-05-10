from rest_framework.throttling import AnonRateThrottle


class SendCodeThrottle(AnonRateThrottle):
    """3 запроса на отправку кода за 10 минут."""
    scope = "send_code"

    def parse_rate(self, rate):
        return 3, 600  # (num_requests, duration_seconds)


class VerifyCodeThrottle(AnonRateThrottle):
    """5 попыток верификации за 10 минут."""
    scope = "verify_code"

    def parse_rate(self, rate):
        return 5, 600
