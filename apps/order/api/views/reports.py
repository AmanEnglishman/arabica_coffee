from django.db.models import Count, Sum
from django.db.models.functions import ExtractHour
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.order.models.code import Order, OrderItem


@extend_schema(
    summary="Отчёт по заказам за день",
    tags=["Admin / Reports"],
    parameters=[
        OpenApiParameter("date", str, description="Дата в формате YYYY-MM-DD (по умолчанию сегодня)"),
        OpenApiParameter("cafe_id", int, description="ID кафе (опционально)"),
    ],
    responses={200: OpenApiResponse(description="Отчёт по заказам")},
    description="Доступно только администраторам. Возвращает топ продуктов, выручку по часам и статистику курьеров.",
)
class OrderReportsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        date_str = request.query_params.get("date")
        cafe_id  = request.query_params.get("cafe_id")

        try:
            report_date = (
                timezone.datetime.strptime(date_str, "%Y-%m-%d").date()
                if date_str else timezone.now().date()
            )
        except ValueError:
            report_date = timezone.now().date()

        base_qs = Order.objects.filter(status="delivered", delivered_at__date=report_date)
        if cafe_id:
            base_qs = base_qs.filter(cafe_id=cafe_id)

        # ── Summary ────────────────────────────────────────────
        all_qs = Order.objects.filter(created_at__date=report_date)
        if cafe_id:
            all_qs = all_qs.filter(cafe_id=cafe_id)

        revenue = base_qs.aggregate(total=Sum("total_price"))["total"] or 0

        summary = {
            "date":             str(report_date),
            "total_orders":     all_qs.count(),
            "delivered_orders": base_qs.count(),
            "cancelled_orders": all_qs.filter(status="cancelled").count(),
            "pickup_orders":    base_qs.filter(delivery_type="pickup").count(),
            "delivery_orders":  base_qs.filter(delivery_type="delivery").count(),
            "total_revenue":    float(revenue),
        }

        # ── Top products ───────────────────────────────────────
        top_products = list(
            OrderItem.objects.filter(
                order__in=base_qs
            ).values("product__title").annotate(
                total_qty=Sum("quantity"),
                total_revenue=Sum("final_price"),
            ).order_by("-total_revenue")[:15]
        )

        # ── Revenue by hour ────────────────────────────────────
        revenue_by_hour = list(
            base_qs.annotate(hour=ExtractHour("delivered_at"))
            .values("hour")
            .annotate(revenue=Sum("total_price"), orders=Count("id"))
            .order_by("hour")
        )

        # ── Courier stats ──────────────────────────────────────
        courier_stats = list(
            base_qs.filter(delivery_type="delivery", courier__isnull=False)
            .values(
                "courier__id",
                "courier__first_name",
                "courier__last_name",
                "courier__phone_number",
            )
            .annotate(deliveries=Count("id"), revenue=Sum("total_price"))
            .order_by("-deliveries")
        )

        # ── Orders timeline (accepted by hour) ─────────────────
        accepted_by_hour = list(
            all_qs.annotate(hour=ExtractHour("created_at"))
            .values("hour")
            .annotate(orders=Count("id"))
            .order_by("hour")
        )

        return Response({
            "summary":          summary,
            "top_products":     top_products,
            "revenue_by_hour":  revenue_by_hour,
            "accepted_by_hour": accepted_by_hour,
            "courier_stats":    courier_stats,
        })
