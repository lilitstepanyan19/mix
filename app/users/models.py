from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    image = models.ImageField(
        upload_to="users_images", blank=True, null=True, verbose_name=_("Аватар")
    )
    phone_number = models.CharField(
        max_length=10, blank=True, null=True, verbose_name=_("Номер телефона")
    )

    class Meta:
        db_table = "user"
        verbose_name = _("Пользователя")
        verbose_name_plural = _("Пользователи")

    def __str__(self):
        return self.username
