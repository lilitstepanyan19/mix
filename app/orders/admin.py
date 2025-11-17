from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from orders.models import Order, OrderItem


class OrderItemTabulareAdmin(admin.TabularInline):
    model = OrderItem
    fields = ("product", "name", "price", "quantity")
    search_fields = ("product", "name")
    extra = 0
    verbose_name = _("Проданный товар")
    verbose_name_plural = _("Проданные товары")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["order", "product", "name", "price", "quantity"]
    search_fields = ("order", "product", "name")
    verbose_name = _("Проданный товар")
    verbose_name_plural = _("Проданные товары")

    def order_display(self, obj):
        return f"Заказ №{obj.order.id}"

    order_display.short_description = _("Заказ")


class OrderTabulareAdmin(admin.TabularInline):
    model = Order
    fields = (
        "requires_delivery",
        "status",
        "payment_on_get",
        "is_paid",
        "created_timestamp",
    )
    search_fields = (
        "requires_delivery",
        "payment_on_get",
        "is_paid",
        "created_timestamp",
    )
    readonly_fields = ("created_timestamp",)
    extra = 0
    verbose_name = _("Заказ")
    verbose_name_plural = _("Заказы")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "requires_delivery",
        "status",
        "payment_on_get",
        "is_paid",
        "created_timestamp",
    )
    search_fields = ("id",)
    readonly_fields = ("created_timestamp",)
    list_filter = (
        "requires_delivery",
        "status",
        "payment_on_get",
        "is_paid",
    )
    inlines = (OrderItemTabulareAdmin,)

    def user_display(self, obj):
        if obj.user:
            return str(obj.user)
        return _("Анонимный пользователь")

    user_display.short_description = _("Пользователь")
