from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Categories(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name=_("Название"))
    slug = models.SlugField(
        max_length=200, unique=True, blank=True, null=True, verbose_name=_("URL")
    )

    class Meta:
        db_table = "category"
        verbose_name = _("Категорию")
        verbose_name_plural = _("Категории")
        ordering = ("-id",)

    def __str__(self):
        return self.name


class Products(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name=_("Название"))
    slug = models.SlugField(
        max_length=200, unique=True, blank=True, null=True, verbose_name=_("URL")
    )
    description = models.TextField(blank=True, null=True, verbose_name=_("Описание"))
    image = models.ImageField(
        upload_to="goods_images", blank=True, null=True, verbose_name=_("Изображение")
    )
    price = models.DecimalField(
        default=0.00, max_digits=7, decimal_places=2, verbose_name=_("Цена")
    )
    discount = models.DecimalField(
        default=0.00, max_digits=4, decimal_places=2, verbose_name=_("Скидка в %")
    )
    quantity = models.PositiveIntegerField(default=0, verbose_name=_("Количество"))
    category = models.ForeignKey(
        to=Categories, on_delete=models.CASCADE, verbose_name=_("Категория")
    )

    class Meta:
        db_table = "product"
        verbose_name = _("Продукт")
        verbose_name_plural = _("Продукты")
        ordering = ("-id",)

    def __str__(self):
        return f'{self.name or _("Без названия")} — {_("Количество")}: {self.quantity}'

    def get_absolute_url(self):
        return reverse("catalog:product", kwargs={"product_slug": self.slug})

    def display_id(self):
        return f"{self.id:05}"

    def sell_price(self):
        if self.discount:
            return round(self.price - self.price * self.discount / 100, 2)
        return self.price


class ProductImage(models.Model):
    product = models.ForeignKey(
        Products,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("Товар"),
    )
    image = models.ImageField(upload_to="goods_images", verbose_name=_("Изображение"))

    class Meta:
        db_table = "product_images"
        verbose_name = _("Изображение товара")
        verbose_name_plural = _("Изображения товаров")

    def __str__(self):
        return _("Изображение для {product}").format(product=self.product.name)
