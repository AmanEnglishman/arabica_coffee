from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Sum
from django.utils import timezone

from apps.order.models import CafeMembership, Order


ACTIVE_ORDER_STATUSES = ("accepted", "ready", "on_the_way")


def get_staff_membership(user):
    if not user.is_authenticated:
        return None

    try:
        membership = CafeMembership.objects.select_related("cafe").get(user=user)
    except CafeMembership.DoesNotExist:
        return None

    if membership.role != CafeMembership.Role.STAFF:
        return None

    return membership


def get_cafe_couriers(cafe):
    return (
        CafeMembership.objects.select_related("user")
        .filter(cafe=cafe, role=CafeMembership.Role.COURIER)
        .order_by("user__first_name", "user__phone_number")
    )


def get_active_orders(cafe):
    return (
        Order.objects.select_related("user", "cafe", "courier")
        .prefetch_related("items__product")
        .filter(cafe=cafe, status__in=ACTIVE_ORDER_STATUSES)
        .order_by("created_at")
    )


def get_today_stats(cafe):
    today = timezone.now().date()
    delivered_qs = Order.objects.filter(
        cafe=cafe,
        status="delivered",
        delivered_at__date=today,
    )
    revenue = delivered_qs.aggregate(total=Sum("total_price"))["total"] or 0
    return {
        "delivered_count": delivered_qs.count(),
        "revenue_today": int(revenue),
    }


def serialize_order(order):
    courier_name = ""
    if order.courier:
        parts = [order.courier.first_name, order.courier.last_name]
        courier_name = " ".join(p for p in parts if p) or order.courier.phone_number

    customer_name = " ".join(
        p for p in [order.user.first_name, order.user.last_name] if p
    )

    return {
        "id": order.id,
        "status": order.status,
        "status_label": order.get_status_display(),
        "delivery_type": order.delivery_type,
        "delivery_type_label": order.get_delivery_type_display(),
        "address": order.address or "",
        "delivery_time": order.delivery_time.strftime("%H:%M") if order.delivery_time else "",
        "total_price": str(order.total_price),
        "created_at": order.created_at.strftime("%H:%M"),
        "created_at_iso": order.created_at.isoformat(),
        "ready_at_iso": order.ready_at.isoformat() if order.ready_at else None,
        "on_the_way_at_iso": order.on_the_way_at.isoformat() if order.on_the_way_at else None,
        "customer": {
            "phone_number": order.user.phone_number,
            "name": customer_name,
        },
        "courier": {
            "id": order.courier_id,
            "phone_number": order.courier.phone_number if order.courier else "",
            "name": courier_name,
        },
        "items": [
            {
                "id": item.id,
                "product_title": item.product.title,
                "quantity": item.quantity,
                "options": item.product_options.get("options", []),
                "final_price": str(item.final_price),
            }
            for item in order.items.all()
        ],
    }


def serialize_active_orders(cafe):
    return [serialize_order(order) for order in get_active_orders(cafe)]


def broadcast_cafe_orders(cafe_id):
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    async_to_sync(channel_layer.group_send)(
        f"cafe_orders_{cafe_id}",
        {"type": "orders.changed"},
    )
