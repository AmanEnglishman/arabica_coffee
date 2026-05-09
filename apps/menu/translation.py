from modeltranslation.translator import TranslationOptions, translator

from apps.menu.models.category import Category, Subcategory
from apps.menu.models.product import Product


class CategoryTranslationOptions(TranslationOptions):
    fields = ("title",)


class SubcategoryTranslationOptions(TranslationOptions):
    fields = ("title",)


class ProductTranslationOptions(TranslationOptions):
    fields = ("title", "description")


translator.register(Category, CategoryTranslationOptions)
translator.register(Subcategory, SubcategoryTranslationOptions)
translator.register(Product, ProductTranslationOptions)
