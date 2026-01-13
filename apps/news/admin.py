from django.contrib import admin
from apps.news.models import News


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ["title", "published_at", "is_active", "created_at"]
    list_filter = ["is_active", "published_at"]
    search_fields = ["title", "short_description"]
    date_hierarchy = "published_at"
    ordering = ["-published_at"]

    fieldsets = (
        ("Основная информация", {
            "fields": ("title", "image", "short_description")
        }),
        ("Содержание", {
            "fields": ("content",)
        }),
        ("Публикация", {
            "fields": ("published_at", "is_active")
        }),
    )