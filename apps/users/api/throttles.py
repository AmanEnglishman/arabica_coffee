from rest_framework.throttling import AnonRateThrottle


class SendCodeThrottle(AnonRateThrottle):
    """3 запроса на отправку SMS-кода за 10 минут с одного IP."""
    scope = "send_code"

    def __init__(self):
        self.num_requests = 3
        self.duration = 600  # 10 минут


class VerifyCodeThrottle(AnonRateThrottle):
    """5 попыток ввода кода за 10 минут с одного IP."""
    scope = "verify_code"

    def __init__(self):
        self.num_requests = 5
        self.duration = 600  # 10 минут
