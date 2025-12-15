from django.contrib import admin
from .models import Category, Subcategory, Product, OptionType, OptionValue, ProductOptionType

class ProductOptionTypeInline(admin.TabularInline):
    model = ProductOptionType
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'title']
    search_fields = ['title']


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'category']
    list_filter = ['category']
    search_fields = ['title']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'subcategory', 'price']
    list_filter = ['subcategory']
    search_fields = ['title']
    inlines = [ProductOptionTypeInline]


@admin.register(OptionType)
class OptionTypeAdmin(admin.ModelAdmin):
    list_display = ('title',)


@admin.register(OptionValue)
class OptionValueAdmin(admin.ModelAdmin):
    list_display = ('type', 'value')
