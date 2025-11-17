from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
    UserChangeForm,
)
from django.utils.translation import gettext_lazy as _

from users.models import User


class UserLoginForm(AuthenticationForm):

    class Meta:
        model = User
        fields = ["username", "password"]

    username = forms.CharField(label=_("Имя пользователя"))
    password = forms.CharField(label=_("Пароль"))


class UserRegistrationForm(UserCreationForm):

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "password1",
            "password2",
        )

    first_name = forms.CharField(label=_("Имя"))
    last_name = forms.CharField(label=_("Фамилия"))
    username = forms.CharField(label=_("Имя пользователя"))
    email = forms.CharField(label=_("Email"))
    password1 = forms.CharField(label=_("Пароль"))
    password2 = forms.CharField(label=_("Подтверждение пароля"))


class ProfileForm(UserChangeForm):
    class Meta:
        model = User
        fields = (
            "image",
            "first_name",
            "last_name",
            "username",
            "email",
        )

    image = forms.ImageField(required=False, label=_("Аватар"))
    first_name = forms.CharField(label=_("Имя"))
    last_name = forms.CharField(label=_("Фамилия"))
    username = forms.CharField(label=_("Имя пользователя"))
    email = forms.CharField(label=_("Email"))
