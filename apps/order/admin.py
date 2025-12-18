from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("final_price",)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "delivery_type", "total_price", "created_at")
    list_filter = ("status", "delivery_type", "created_at")
    search_fields = ("user__username", "user__phone_number", "id")
    inlines = [OrderItemInline]
    readonly_fields = ("total_price", "created_at", "updated_at")
