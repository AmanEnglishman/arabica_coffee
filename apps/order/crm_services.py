from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Count, Sum
from django.utils import timezone

from apps.order.models import CafeMembership, Order


ACTIVE_ORDER_STATUSES = ("accepted", "ready", "on_the_way")


# ── Auth helpers ───────────────────────────────────────────────────────────────

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


# ── Couriers ───────────────────────────────────────────────────────────────────

def get_cafe_couriers(cafe):
    return (
        CafeMembership.objects.select_related("user")
        .filter(cafe=cafe, role=CafeMembership.Role.COURIER)
        .order_by("user__first_name", "user__phone_number")
    )


def get_couriers_with_status(cafe):
    today = timezone.now().date()
    couriers = get_cafe_couriers(cafe)
    result = []
    for m in couriers:
        active = (
            Order.objects.filter(courier=m.user, cafe=cafe, status="on_the_way")
            .select_related("user")
            .first()
        )
        delivered_today = Order.objects.filter(
            courier=m.user, cafe=cafe, status="delivered", delivered_at__date=today
        ).count()
        name = (
            " ".join(p for p in [m.user.first_name, m.user.last_name] if p)
            or m.user.phone_number
        )
        result.append({
            "id": m.user_id,
            "name": name,
            "phone_number": m.user.phone_number,
            "is_busy": active is not None,
            "active_order": {
                "id": active.id,
                "customer": " ".join(
                    p for p in [active.user.first_name, active.user.last_name] if p
                ) or active.user.phone_number,
                "address": active.address or "",
                "created_at": active.created_at.strftime("%H:%M"),
            } if active else None,
            "delivered_today": delivered_today,
        })
    return result


# ── Active orders ──────────────────────────────────────────────────────────────

def get_active_orders(cafe):
    return (
        Order.objects.select_related("user", "cafe", "courier")
        .prefetch_related("items__product")
        .filter(cafe=cafe, status__in=ACTIVE_ORDER_STATUSES)
        .order_by("created_at")
    )


def serialize_order(order):
    courier_name = ""
    if order.courier:
        courier_name = (
            " ".join(p for p in [order.courier.first_name, order.courier.last_name] if p)
            or order.courier.phone_number
        )
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
        "customer": {"phone_number": order.user.phone_number, "name": customer_name},
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
    return [serialize_order(o) for o in get_active_orders(cafe)]


# ── History ────────────────────────────────────────────────────────────────────

def get_completed_orders_today(cafe):
    today = timezone.now().date()
    return (
        Order.objects.select_related("user", "courier")
        .prefetch_related("items__product")
        .filter(cafe=cafe, status="delivered", delivered_at__date=today)
        .order_by("-delivered_at")
    )


def serialize_completed_order(order):
    courier_name = ""
    if order.courier:
        courier_name = (
            " ".join(p for p in [order.courier.first_name, order.courier.last_name] if p)
            or order.courier.phone_number
        )
    customer_name = (
        " ".join(p for p in [order.user.first_name, order.user.last_name] if p)
        or order.user.phone_number
    )
    return {
        "id": order.id,
        "delivery_type": order.delivery_type,
        "delivery_type_label": order.get_delivery_type_display(),
        "total_price": str(order.total_price),
        "delivered_at": order.delivered_at.strftime("%H:%M") if order.delivered_at else "",
        "created_at": order.created_at.strftime("%H:%M"),
        "customer": {"name": customer_name, "phone_number": order.user.phone_number},
        "courier_name": courier_name,
        "items": [
            {
                "product_title": item.product.title,
                "quantity": item.quantity,
                "options": item.product_options.get("options", []),
                "final_price": str(item.final_price),
            }
            for item in order.items.all()
        ],
    }


# ── Stats ──────────────────────────────────────────────────────────────────────

def get_today_stats(cafe):
    today = timezone.now().date()
    delivered_qs = Order.objects.filter(
        cafe=cafe, status="delivered", delivered_at__date=today
    )
    revenue = delivered_qs.aggregate(total=Sum("total_price"))["total"] or 0
    return {
        "delivered_count": delivered_qs.count(),
        "revenue_today": int(revenue),
    }


# ── WebSocket broadcast ────────────────────────────────────────────────────────

def broadcast_cafe_orders(cafe_id):
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    async_to_sync(channel_layer.group_send)(
        f"cafe_orders_{cafe_id}",
        {"type": "orders.changed"},
    )
