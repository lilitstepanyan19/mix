from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from carts.admin import CartTabAdmin
from orders.admin import OrderTabulareAdmin
from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["username", "first_name", "last_name", "email"]
    search_fields = ["username", "first_name", "last_name", "email"]
    inlines = [CartTabAdmin, OrderTabulareAdmin]

    def username_display(self, obj):
        return obj.username

    username_display.short_description = _("Имя пользователя")

    def first_name_display(self, obj):
        return obj.first_name

    first_name_display.short_description = _("Имя")

    def last_name_display(self, obj):
        return obj.last_name

    last_name_display.short_description = _("Фамилия")

    def email_display(self, obj):
        return obj.email

    email_display.short_description = _("Email")
