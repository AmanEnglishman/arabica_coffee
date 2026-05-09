from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.order.crm_services import (
    get_active_orders,
    get_cafe_couriers,
    get_staff_membership,
    get_today_stats,
    serialize_active_orders,
)
from apps.order.models import CafeMembership, Order


def _staff_membership_or_error(request):
    membership = get_staff_membership(request.user)
    if membership is None:
        return None, JsonResponse({"detail": "Нет доступа."}, status=403)
    return membership, None


def _orders_payload(cafe):
    return JsonResponse(
        {
            "ok": True,
            "orders": serialize_active_orders(cafe),
            "active_count": get_active_orders(cafe).count(),
        }
    )


@login_required(login_url="/admin/login/")
def crm_orders_view(request):
    membership = get_staff_membership(request.user)
    if membership is None:
        return render(request, "crm/forbidden.html", status=403)

    cafe = membership.cafe
    couriers = get_cafe_couriers(cafe)
    stats = get_today_stats(cafe)
    staff_name = " ".join(
        p for p in [request.user.first_name, request.user.last_name] if p
    ) or request.user.phone_number

    return render(
        request,
        "crm/orders.html",
        {
            "cafe": cafe,
            "orders": serialize_active_orders(cafe),
            "couriers": [
                {
                    "id": c.user_id,
                    "phone_number": c.user.phone_number,
                    "name": " ".join(
                        p for p in [c.user.first_name, c.user.last_name] if p
                    ) or c.user.phone_number,
                }
                for c in couriers
            ],
            "active_count": get_active_orders(cafe).count(),
            "delivered_today": stats["delivered_count"],
            "revenue_today": stats["revenue_today"],
            "staff_name": staff_name,
        },
    )


@login_required(login_url="/admin/login/")
@require_POST
def crm_order_action_view(request, order_id, action):
    membership, error = _staff_membership_or_error(request)
    if error:
        return error

    order = get_object_or_404(Order, id=order_id, cafe=membership.cafe)

    if action == "mark-ready":
        if order.status == "ready":
            return _orders_payload(membership.cafe)
        if order.status != "accepted":
            return JsonResponse(
                {
                    "detail": (
                        "Заказ нельзя отметить готовым. "
                        f"Текущий статус: {order.get_status_display()}."
                    )
                },
                status=400,
            )
        order.status = "ready"
        order.ready_at = timezone.now()
        order.save(update_fields=["status", "ready_at", "updated_at"])
        return _orders_payload(membership.cafe)

    if action == "mark-delivered":
        if order.status == "delivered":
            return _orders_payload(membership.cafe)
        if order.status != "ready" or order.delivery_type != "pickup":
            return JsonResponse(
                {
                    "detail": (
                        "Заказ нельзя выдать. "
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

    if action == "assign-courier":
        if order.status != "ready" or order.delivery_type != "delivery":
            return JsonResponse(
                {
                    "detail": (
                        "Курьера нельзя назначить. "
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

    if action == "mark-delivery-delivered":
        if order.status == "delivered":
            return _orders_payload(membership.cafe)
        if order.status != "on_the_way" or order.delivery_type != "delivery":
            return JsonResponse(
                {
                    "detail": (
                        "Нельзя закрыть доставку. "
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
