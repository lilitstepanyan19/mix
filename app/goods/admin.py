from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TranslationAdmin
from goods.models import Categories, Products, ProductImage


@admin.register(Categories)
class CategoriesAdmin(TranslationAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ["name"]
    # Названия колонок в админке
    list_display_links = ["name"]
    # Можно добавить verbose_name переводы, если нужно
    # list_display[0].short_description = _("Название категории")


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    verbose_name = _("Изображение товара")
    verbose_name_plural = _("Изображения товаров")


@admin.register(Products)
class ProductsAdmin(TranslationAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ["name", "quantity", "price", "discount"]
    list_editable = ["discount", "quantity", "price"]
    search_fields = ["name", "description"]
    list_filter = ["discount", "quantity", "category"]
    fields = [
        "name",
        "category",
        "slug",
        "description",
        "image",
        ("price", "discount"),
        "quantity",
    ]
    inlines = [ProductImageInline]

    # Переводимые заголовки колонок
    def name_display(self, obj):
        return obj.name

    name_display.short_description = _("Название")

    def quantity_display(self, obj):
        return obj.quantity

    quantity_display.short_description = _("Количество")

    def price_display(self, obj):
        return obj.price

    price_display.short_description = _("Цена")

    def discount_display(self, obj):
        return obj.discount

    discount_display.short_description = _("Скидка")
