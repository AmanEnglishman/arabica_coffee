from django.db import models


class Promotion(models.Model):
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    image = models.ImageField(upload_to="promotions/", verbose_name="Изображение")
    short_description = models.TextField(verbose_name="Краткое описание")
    content = models.TextField(verbose_name="Содержание")
    published_at = models.DateField(verbose_name="Дата публикации")
    is_active = models.BooleanField(default=True, verbose_name="Активно")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Акция"
        verbose_name_plural = "Акции"
        ordering = ["-published_at"]
        indexes = [
            models.Index(fields=["-published_at"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.title