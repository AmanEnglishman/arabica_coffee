from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.order.crm_services import (
    get_active_orders,
    get_cafe_couriers,
    get_staff_membership,
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

    return render(
        request,
        "crm/orders.html",
        {
            "cafe": membership.cafe,
            "orders": serialize_active_orders(membership.cafe),
            "couriers": [
                {
                    "id": courier.user_id,
                    "phone_number": courier.user.phone_number,
                }
                for courier in get_cafe_couriers(membership.cafe)
            ],
            "active_count": get_active_orders(membership.cafe).count(),
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
        if order.status != "accepted":
            return JsonResponse({"detail": "Заказ нельзя отметить готовым."}, status=400)
        order.status = "ready"
        order.ready_at = timezone.now()
        order.save(update_fields=["status", "ready_at", "updated_at"])
        return _orders_payload(membership.cafe)

    if action == "mark-delivered":
        if order.status != "ready" or order.delivery_type != "pickup":
            return JsonResponse({"detail": "Заказ нельзя выдать."}, status=400)
        order.status = "delivered"
        order.delivered_at = timezone.now()
        order.save(update_fields=["status", "delivered_at", "updated_at"])
        return _orders_payload(membership.cafe)

    if action == "assign-courier":
        courier_id = request.POST.get("courier_id")
        courier_membership = get_object_or_404(
            CafeMembership,
            user_id=courier_id,
            role=CafeMembership.Role.COURIER,
            cafe=membership.cafe,
        )
        if order.status != "ready" or order.delivery_type != "delivery":
            return JsonResponse({"detail": "Курьера нельзя назначить."}, status=400)
        order.courier = courier_membership.user
        order.status = "on_the_way"
        order.on_the_way_at = timezone.now()
        order.save(update_fields=["courier", "status", "on_the_way_at", "updated_at"])
        return _orders_payload(membership.cafe)

    return JsonResponse({"detail": "Неизвестное действие."}, status=404)
