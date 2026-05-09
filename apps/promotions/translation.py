from modeltranslation.translator import TranslationOptions, translator

from apps.promotions.models.models import Promotion


class PromotionTranslationOptions(TranslationOptions):
    fields = ("title", "short_description", "content")


translator.register(Promotion, PromotionTranslationOptions)
