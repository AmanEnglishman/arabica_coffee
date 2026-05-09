from modeltranslation.translator import TranslationOptions, translator

from apps.news.models.models import News


class NewsTranslationOptions(TranslationOptions):
    fields = ("title", "short_description", "content")


translator.register(News, NewsTranslationOptions)
