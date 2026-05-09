from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.order.crm_services import (
    get_active_orders,
    get_cafe_couriers,
    get_completed_orders_today,
    get_couriers_with_status,
    get_staff_membership,
    get_today_stats,
    serialize_active_orders,
    serialize_completed_order,
)
from apps.order.models import CafeMembership, Order


# ── Helpers ────────────────────────────────────────────────────────────────────

def _get_membership(request):
    membership = get_staff_membership(request.user)
    if membership is None:
        return None, JsonResponse({"detail": "Нет доступа."}, status=403)
    return membership, None


def _orders_payload(cafe):
    return JsonResponse({
        "ok": True,
        "orders": serialize_active_orders(cafe),
        "active_count": get_active_orders(cafe).count(),
    })


# ── Page view ──────────────────────────────────────────────────────────────────

@login_required(login_url="/admin/login/")
def crm_orders_view(request):
    membership = get_staff_membership(request.user)
    if membership is None:
        return render(request, "crm/forbidden.html", status=403)

    cafe = membership.cafe
    stats = get_today_stats(cafe)
    staff_name = (
        " ".join(p for p in [request.user.first_name, request.user.last_name] if p)
        or request.user.phone_number
    )

    return render(request, "crm/orders.html", {
        "cafe": cafe,
        "orders": serialize_active_orders(cafe),
        "couriers": [
            {
                "id": c.user_id,
                "name": " ".join(p for p in [c.user.first_name, c.user.last_name] if p)
                        or c.user.phone_number,
                "phone_number": c.user.phone_number,
            }
            for c in get_cafe_couriers(cafe)
        ],
        "active_count": get_active_orders(cafe).count(),
        "delivered_today": stats["delivered_count"],
        "revenue_today": stats["revenue_today"],
        "staff_name": staff_name,
    })


# ── API: history ───────────────────────────────────────────────────────────────

@login_required(login_url="/admin/login/")
def crm_history_api(request):
    membership, error = _get_membership(request)
    if error:
        return error

    qs = get_completed_orders_today(membership.cafe)
    revenue = qs.aggregate(total=Sum("total_price"))["total"] or 0

    return JsonResponse({
        "ok": True,
        "orders": [serialize_completed_order(o) for o in qs],
        "count": qs.count(),
        "revenue": int(revenue),
    })


# ── API: couriers status ───────────────────────────────────────────────────────

@login_required(login_url="/admin/login/")
def crm_couriers_api(request):
    membership, error = _get_membership(request)
    if error:
        return error

    return JsonResponse({
        "ok": True,
        "couriers": get_couriers_with_status(membership.cafe),
    })


# ── Order actions ──────────────────────────────────────────────────────────────

@login_required(login_url="/admin/login/")
@require_POST
def crm_order_action_view(request, order_id, action):
    membership, error = _get_membership(request)
    if error:
        return error

    order = get_object_or_404(Order, id=order_id, cafe=membership.cafe)

    # accepted → ready
    if action == "mark-ready":
        if order.status == "ready":
            return _orders_payload(membership.cafe)
        if order.status != "accepted":
            return JsonResponse(
                {"detail": f"Нельзя отметить готовым. Статус: {order.get_status_display()}."},
                status=400,
            )
        order.status = "ready"
        order.ready_at = timezone.now()
        order.save(update_fields=["status", "ready_at", "updated_at"])
        return _orders_payload(membership.cafe)

    # ready + pickup → delivered
    if action == "mark-delivered":
        if order.status == "delivered":
            return _orders_payload(membership.cafe)
        if order.status != "ready" or order.delivery_type != "pickup":
            return JsonResponse(
                {
                    "detail": (
                        f"Нельзя выдать. "
                        f"Статус: {order.get_status_display()}, "
                        f"тип: {order.get_delivery_type_display()}."
                    )
                },
                status=400,
            )
        order.status = "delivered"
        order.delivered_at = timezone.now()
        order.save(update_fields=["status", "delivered_at", "updated_at"])
        return _orders_payload(membership.cafe)

    # ready + delivery → on_the_way (assign courier)
    if action == "assign-courier":
        if order.status != "ready" or order.delivery_type != "delivery":
            return JsonResponse(
                {
                    "detail": (
                        f"Нельзя назначить курьера. "
                        f"Статус: {order.get_status_display()}, "
                        f"тип: {order.get_delivery_type_display()}."
                    )
                },
                status=400,
            )
        courier_id = request.POST.get("courier_id")
        if not courier_id:
            return JsonResponse({"detail": "Выберите курьера."}, status=400)
        courier_membership = get_object_or_404(
            CafeMembership,
            user_id=courier_id,
            role=CafeMembership.Role.COURIER,
            cafe=membership.cafe,
        )
        order.courier = courier_membership.user
        order.status = "on_the_way"
        order.on_the_way_at = timezone.now()
        order.save(update_fields=["courier", "status", "on_the_way_at", "updated_at"])
        return _orders_payload(membership.cafe)

    # on_the_way + delivery → delivered (staff closes delivery)
    if action == "mark-delivery-delivered":
        if order.status == "delivered":
            return _orders_payload(membership.cafe)
        if order.status != "on_the_way" or order.delivery_type != "delivery":
            return JsonResponse(
                {
                    "detail": (
                        f"Нельзя закрыть доставку. "
                        f"Статус: {order.get_status_display()}, "
                        f"тип: {order.get_delivery_type_display()}."
                    )
                },
                status=400,
            )
        order.status = "delivered"
        order.delivered_at = timezone.now()
        order.save(update_fields=["status", "delivered_at", "updated_at"])
        return _orders_payload(membership.cafe)

    return JsonResponse({"detail": "Неизвестное действие."}, status=404)
