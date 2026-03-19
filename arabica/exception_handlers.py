from rest_framework.exceptions import NotAuthenticated, PermissionDenied, ValidationError, NotFound
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status as drf_status


def api_exception_handler(exc, context):
    """
    Делает единый формат ошибок, чтобы Flutter одинаково обрабатывал любые 4xx/5xx.
    """
    response = drf_exception_handler(exc, context)
    if response is None:
        # Для неожиданных исключений оставляем DRF-стандарт (скорее всего 500).
        return response

    status_code = getattr(response, "status_code", None) or 500

    # DRF для ValidationError обычно возвращает dict: {field: [messages]}
    if isinstance(exc, ValidationError):
        return Response(
            {
                "success": False,
                "error": {
                    "code": "validation_error",
                    "message": "Ошибка валидации.",
                    "details": response.data,
                },
            },
            status=drf_status.HTTP_400_BAD_REQUEST,
        )

    if isinstance(exc, NotAuthenticated):
        return Response(
            {
                "success": False,
                "error": {"code": "unauthorized", "message": "Неавторизован."},
            },
            status=drf_status.HTTP_401_UNAUTHORIZED,
        )

    if isinstance(exc, PermissionDenied):
        return Response(
            {
                "success": False,
                "error": {"code": "forbidden", "message": "Нет прав."},
            },
            status=drf_status.HTTP_403_FORBIDDEN,
        )

    if isinstance(exc, NotFound):
        return Response(
            {
                "success": False,
                "error": {"code": "not_found", "message": "Ресурс не найден."},
            },
            status=drf_status.HTTP_404_NOT_FOUND,
        )

    # Универсальный fallback: пробуем вытащить detail из response.data
    detail = None
    if isinstance(response.data, dict):
        detail = response.data.get("detail")

    message = detail or str(exc) or "Ошибка."

    code_map = {
        400: "bad_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        429: "rate_limited",
        500: "server_error",
    }

    return Response(
        {
            "success": False,
            "error": {
                "code": code_map.get(status_code, "error"),
                "message": message,
            },
        },
        status=status_code,
    )

