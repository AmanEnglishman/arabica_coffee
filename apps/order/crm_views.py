import json

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from django.db.models import Count
from django.db.models.functions import ExtractHour

from apps.order.crm_services import (
    broadcast_cafe_orders,
    get_active_orders,
    get_cafe_couriers,
    get_completed_orders_today,
    get_couriers_with_status,
    get_or_create_guest_user,
    get_staff_membership,
    get_today_stats,
    serialize_active_orders,
    serialize_completed_order,
)
from apps.order.models import CafeMembership, Order
from apps.order.models.code import OrderItem
from apps.menu.models.product import Product


# ── Helpers ────────────────────────────────────────────────────────────────────

def _get_membership(request):
    """Returns (membership, None) or (None, error_response)."""
    if not request.user.is_authenticated:
        return None, JsonResponse({"detail": "Требуется авторизация."}, status=403)
    membership = get_staff_membership(request.user)
    if membership is None:
        return None, JsonResponse({"detail": "Нет доступа. Нужна роль сотрудника кафе."}, status=403)
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
                "id": c.id,
                "name": " ".join(p for p in [c.first_name, c.last_name] if p) or c.phone_number,
                "phone_number": c.phone_number,
            }
            for c in get_cafe_couriers(cafe)
        ],
        "active_count": get_active_orders(cafe).count(),
        "delivered_today": stats["delivered_count"],
        "revenue_today": stats["revenue_today"],
        "staff_name": staff_name,
    })


# ── API: history ───────────────────────────────────────────────────────────────

def crm_history_api(request):
    membership, error = _get_membership(request)
    if error:
        return error

    qs = get_completed_orders_today(membership.cafe)
    total_count = qs.count()
    revenue = qs.aggregate(total=Sum("total_price"))["total"] or 0

    # Pagination
    try:
        page      = max(1, int(request.GET.get("page", 1)))
        page_size = min(50, max(5, int(request.GET.get("page_size", 20))))
    except (ValueError, TypeError):
        page, page_size = 1, 20

    offset = (page - 1) * page_size
    page_qs = qs[offset: offset + page_size]
    total_pages = max(1, -(-total_count // page_size))  # ceil division

    return JsonResponse({
        "ok": True,
        "orders": [serialize_completed_order(o) for o in page_qs],
        "count": total_count,
        "revenue": int(revenue),
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
    })


# ── API: couriers status ───────────────────────────────────────────────────────

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
                {"detail": f"Нельзя отметить готовым — текущий статус: «{order.get_status_display()}». Ожидается «Принят»."},
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
        if order.status != "ready":
            return JsonResponse(
                {"detail": f"Нельзя выдать — статус «{order.get_status_display()}», ожидается «Готов»."},
                status=400,
            )
        if order.delivery_type != "pickup":
            return JsonResponse(
                {"detail": "Это заказ на доставку. Используйте назначение курьера."},
                status=400,
            )
        order.status = "delivered"
        order.delivered_at = timezone.now()
        order.save(update_fields=["status", "delivered_at", "updated_at"])
        return _orders_payload(membership.cafe)

    # ready + delivery → on_the_way
    if action == "assign-courier":
        if order.status != "ready":
            return JsonResponse(
                {"detail": f"Нельзя назначить курьера — статус «{order.get_status_display()}», ожидается «Готов»."},
                status=400,
            )
        if order.delivery_type != "delivery":
            return JsonResponse(
                {"detail": "Это заказ-самовывоз. Курьер не нужен."},
                status=400,
            )
        courier_id = request.POST.get("courier_id")
        if not courier_id:
            return JsonResponse({"detail": "Выберите курьера из списка."}, status=400)
        courier_qs = get_cafe_couriers(membership.cafe)
        try:
            courier_user = courier_qs.get(id=courier_id)
        except courier_qs.model.DoesNotExist:
            return JsonResponse({"detail": "Курьер не найден или не относится к этому кафе."}, status=404)
        order.courier = courier_user
        order.status = "on_the_way"
        order.on_the_way_at = timezone.now()
        order.save(update_fields=["courier", "status", "on_the_way_at", "updated_at"])
        return _orders_payload(membership.cafe)

    # on_the_way + delivery → delivered (staff closes)
    if action == "mark-delivery-delivered":
        if order.status == "delivered":
            return _orders_payload(membership.cafe)
        if order.status != "on_the_way":
            return JsonResponse(
                {"detail": f"Нельзя закрыть — статус «{order.get_status_display()}», ожидается «В пути»."},
                status=400,
            )
        if order.delivery_type != "delivery":
            return JsonResponse({"detail": "Это заказ-самовывоз."}, status=400)
        order.status = "delivered"
        order.delivered_at = timezone.now()
        order.save(update_fields=["status", "delivered_at", "updated_at"])
        return _orders_payload(membership.cafe)

    return JsonResponse({"detail": f"Неизвестное действие: {action}."}, status=404)


# ── POS: page ──────────────────────────────────────────────────────────────────

@login_required(login_url="/admin/login/")
def crm_pos_view(request):
    membership = get_staff_membership(request.user)
    if membership is None:
        return render(request, "crm/forbidden.html", status=403)
    staff_name = (
        " ".join(p for p in [request.user.first_name, request.user.last_name] if p)
        or request.user.phone_number
    )
    return render(request, "crm/pos.html", {
        "cafe": membership.cafe,
        "staff_name": staff_name,
    })


# ── POS: menu API ──────────────────────────────────────────────────────────────

def crm_pos_menu_api(request):
    membership, error = _get_membership(request)
    if error:
        return error

    products = (
        Product.objects
        .filter(is_active=True)
        .select_related("subcategory__category")
        .prefetch_related("option_types__option_type__values")
        .order_by("subcategory__category__id", "subcategory__id", "title")
    )

    categories = {}
    for p in products:
        cat = p.subcategory.category
        sub = p.subcategory
        if cat.id not in categories:
            categories[cat.id] = {"id": cat.id, "title": cat.title, "subcategories": {}}
        if sub.id not in categories[cat.id]["subcategories"]:
            categories[cat.id]["subcategories"][sub.id] = {"id": sub.id, "title": sub.title, "products": []}

        option_types = []
        for pot in p.option_types.all():
            ot = pot.option_type
            option_types.append({
                "id": ot.id,
                "title": ot.title,
                "values": [
                    {"id": v.id, "value": v.value, "additional_cost": v.additional_cost}
                    for v in ot.values.all()
                ],
            })

        categories[cat.id]["subcategories"][sub.id]["products"].append({
            "id": p.id,
            "title": p.title,
            "price": p.price,
            "description": p.description,
            "image": p.image.url if p.image else None,
            "has_options": p.has_options,
            "option_types": option_types,
        })

    result = []
    for cat_data in categories.values():
        cat_data["subcategories"] = list(cat_data["subcategories"].values())
        result.append(cat_data)

    return JsonResponse({"ok": True, "categories": result})


# ── POS: create order ──────────────────────────────────────────────────────────

def crm_pos_order_api(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    membership, error = _get_membership(request)
    if error:
        return error

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"detail": "Неверный JSON"}, status=400)

    items_data = data.get("items", [])
    if not items_data:
        return JsonResponse({"detail": "Корзина пуста"}, status=400)

    complete_immediately = bool(data.get("complete_immediately", False))

    prepared_items = []
    total = 0

    for item_data in items_data:
        try:
            product = Product.objects.get(id=item_data["product_id"], is_active=True)
        except (Product.DoesNotExist, KeyError):
            return JsonResponse({"detail": f"Продукт не найден"}, status=400)

        try:
            quantity = max(1, int(item_data.get("quantity", 1)))
        except (ValueError, TypeError):
            return JsonResponse({"detail": "Неверное количество"}, status=400)

        options = item_data.get("options", [])
        options_cost = sum(int(o.get("additional_cost", 0)) for o in options)
        unit_price = product.price + options_cost
        final_price = unit_price * quantity
        total += final_price

        prepared_items.append({
            "product": product,
            "quantity": quantity,
            "final_price": final_price,
            "product_options": {
                "options": [{"type": o["type"], "value": o["value"]} for o in options],
                "comment": item_data.get("comment", ""),
            },
        })

    guest_user = get_or_create_guest_user(membership.cafe)

    now = timezone.now()
    status = "delivered" if complete_immediately else "accepted"
    order = Order.objects.create(
        user=guest_user,
        cafe=membership.cafe,
        status=status,
        delivery_type="pickup",
        total_price=total,
        delivered_at=now if complete_immediately else None,
    )

    for item in prepared_items:
        OrderItem.objects.create(
            order=order,
            product=item["product"],
            quantity=item["quantity"],
            final_price=item["final_price"],
            product_options=item["product_options"],
        )

    broadcast_cafe_orders(membership.cafe.id)

    try:
        from apps.printing.utils import create_and_broadcast_print_job
        create_and_broadcast_print_job(order)
    except Exception:
        pass

    return JsonResponse({"ok": True, "order_id": order.id, "total": total})


# ── API: reports ───────────────────────────────────────────────────────────────

def crm_reports_api(request):
    membership, error = _get_membership(request)
    if error:
        return error

    today = timezone.now().date()
    delivered_qs = get_completed_orders_today(membership.cafe)
    all_today = Order.objects.filter(cafe=membership.cafe, created_at__date=today)

    revenue = delivered_qs.aggregate(total=Sum("total_price"))["total"] or 0

    from apps.order.models.code import OrderItem
    top_products = list(
        OrderItem.objects.filter(order__in=delivered_qs)
        .values("product__title")
        .annotate(qty=Sum("quantity"), revenue=Sum("final_price"))
        .order_by("-revenue")[:10]
    )

    revenue_by_hour = list(
        delivered_qs
        .annotate(hour=ExtractHour("delivered_at"))
        .values("hour")
        .annotate(revenue=Sum("total_price"), orders=Count("id"))
        .order_by("hour")
    )

    accepted_by_hour = list(
        all_today
        .annotate(hour=ExtractHour("created_at"))
        .values("hour")
        .annotate(orders=Count("id"))
        .order_by("hour")
    )

    courier_stats = list(
        delivered_qs.filter(delivery_type="delivery", courier__isnull=False)
        .values("courier__id", "courier__first_name", "courier__last_name", "courier__phone_number")
        .annotate(deliveries=Count("id"), revenue=Sum("total_price"))
        .order_by("-deliveries")
    )

    return JsonResponse({
        "ok": True,
        "date": str(today),
        "summary": {
            "total_orders":     all_today.count(),
            "delivered_orders": delivered_qs.count(),
            "cancelled_orders": all_today.filter(status="cancelled").count(),
            "pickup_orders":    delivered_qs.filter(delivery_type="pickup").count(),
            "delivery_orders":  delivered_qs.filter(delivery_type="delivery").count(),
            "total_revenue":    float(revenue),
        },
        "top_products":     top_products,
        "revenue_by_hour":  revenue_by_hour,
        "accepted_by_hour": accepted_by_hour,
        "courier_stats":    courier_stats,
    })
