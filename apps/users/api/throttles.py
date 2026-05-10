from rest_framework.throttling import AnonRateThrottle


class SendCodeThrottle(AnonRateThrottle):
    """3 запроса на отправку SMS-кода за 10 минут с одного IP."""
    scope = "send_code"

    def __init__(self):
        self.rate = "3/10m"       # нужен allow_request
        self.num_requests = 3
        self.duration = 600       # 10 минут в секундах


class VerifyCodeThrottle(AnonRateThrottle):
    """5 попыток ввода кода за 10 минут с одного IP."""
    scope = "verify_code"

    def __init__(self):
        self.rate = "5/10m"
        self.num_requests = 5
        self.duration = 600
