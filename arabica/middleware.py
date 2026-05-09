from django.utils import translation

SUPPORTED_LANGUAGES = {"ru", "ky"}


class LanguageQueryParamMiddleware:
    """
    Активирует язык из query-параметра ?lang=ru|ky.
    Имеет приоритет над Accept-Language и cookie.
    Пример: GET /api/v1/menu/?lang=ky
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang = request.GET.get("lang")
        if lang in SUPPORTED_LANGUAGES:
            translation.activate(lang)
            request.LANGUAGE_CODE = lang
        return self.get_response(request)
