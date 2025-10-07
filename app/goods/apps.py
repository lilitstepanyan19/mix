from django.apps import AppConfig


class GoodsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "goods"
    verbose_name = "Товары"

    def ready(self):
        import goods.translation  # импортировать переводы здесь
