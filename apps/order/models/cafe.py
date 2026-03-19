from django.db import models
from django.utils.translation import gettext_lazy as _

from django.contrib.auth import get_user_model


User = get_user_model()


class Cafe(models.Model):
    """
    Филиал/кафе. Заказы прикрепляются к конкретному кафе, выбранному клиентом.
    """

    name = models.CharField(_("Название"), max_length=200)
    address = models.TextField(_("Адрес"), blank=True)
    phone = models.CharField(_("Телефон"), max_length=20, blank=True)
    is_active = models.BooleanField(_("Активно"), default=True)

    class Meta:
        verbose_name = _("Кафе")
        verbose_name_plural = _("Кафе")

    def __str__(self) -> str:
        return self.name


class CafeMembership(models.Model):
    """
    Привязка пользователя к конкретному кафе и роли.

    Курьер отделён по кафе: курьер может обслуживать только заказы своего кафе.
    """

    class Role(models.TextChoices):
        STAFF = "staff", _("Сотрудник кафе")
        COURIER = "courier", _("Курьер")

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="cafe_membership",
    )
    cafe = models.ForeignKey(Cafe, on_delete=models.CASCADE, related_name="members")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STAFF)

    class Meta:
        unique_together = [
            ("user", "role"),
        ]
        indexes = [
            models.Index(fields=["cafe", "role"]),
        ]

    def __str__(self) -> str:
        return f"{self.user.phone_number} -> {self.cafe_id} ({self.role})"

