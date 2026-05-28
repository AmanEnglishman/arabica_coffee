from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.order.crm_services import broadcast_cafe_orders
from apps.order.models import Order

User = get_user_model()

GUEST_PHONE_PREFIX = "+00000"
COFFEE_CUP_THRESHOLD = 6


@receiver(post_save, sender=Order)
def notify_cafe_order_saved(sender, instance, **kwargs):
    if instance.cafe_id:
        broadcast_cafe_orders(instance.cafe_id)


@receiver(post_delete, sender=Order)
def notify_cafe_order_deleted(sender, instance, **kwargs):
    if instance.cafe_id:
        broadcast_cafe_orders(instance.cafe_id)


@receiver(post_save, sender=Order)
def handle_order_delivered(sender, instance, **kwargs):
    if instance.status != "delivered" or instance.bonus_awarded:
        return

    with transaction.atomic():
        order = Order.objects.select_for_update().get(pk=instance.pk)
        if order.bonus_awarded:
            return

        user = User.objects.select_for_update().get(pk=order.user_id)

        if user.phone_number.startswith(GUEST_PHONE_PREFIX):
            return

        if order.bonus_earned > 0:
            user.loyalty_points += order.bonus_earned

        user.coffee_cups += 1
        if user.coffee_cups >= COFFEE_CUP_THRESHOLD:
            user.coffee_cups = 0

        user.save(update_fields=["loyalty_points", "coffee_cups"])

        order.bonus_awarded = True
        order.save(update_fields=["bonus_awarded"])
