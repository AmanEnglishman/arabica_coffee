from rest_framework.response import Response


def api_error(*, code: str, message: str, status_code: int, details=None):
    """
    Унифицированный формат ошибок для Flutter.
    """
    payload = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
        },
    }
    if details is not None:
        payload["error"]["details"] = details
    return Response(payload, status=status_code)

