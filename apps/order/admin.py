from django.contrib import admin
from .models import Cafe, CafeMembership, Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("final_price",)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "cafe",
        "courier",
        "status",
        "delivery_type",
        "total_price",
        "created_at",
    )
    list_filter = ("status", "delivery_type", "created_at")
    search_fields = ("user__username", "user__phone_number", "id")
    inlines = [OrderItemInline]
    readonly_fields = ("total_price", "created_at", "updated_at")


@admin.register(Cafe)
class CafeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_active")
    search_fields = ("name", "phone")
    list_filter = ("is_active",)


@admin.register(CafeMembership)
class CafeMembershipAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "cafe", "role")
    list_filter = ("role", "cafe")
    search_fields = ("user__phone_number", "cafe__name")
