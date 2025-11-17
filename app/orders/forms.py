import re
from django import forms
from django.utils.translation import gettext_lazy as _


class CreateOrderForm(forms.Form):
    first_name = forms.CharField(
        label=_("Имя"),
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Введите ваше имя"),
            }
        ),
    )
    last_name = forms.CharField(
        label=_("Фамилия"),
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Введите вашу фамилию"),
            }
        ),
    )
    phone_number = forms.CharField(
        label=_("Номер телефона"),
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Номер телефона"),
            }
        ),
    )
    requires_delivery = forms.ChoiceField(
        label=_("Нужна доставка"),
        widget=forms.RadioSelect(),
        choices=[
            ("0", _("Нет")),
            ("1", _("Да")),
        ],
        initial="0",
    )
    delivery_address = forms.CharField(
        label=_("Адрес доставки"),
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": _("Введите адрес доставки"),
                "id": "delivery-address",
            }
        ),
        required=False,
    )
    payment_on_get = forms.ChoiceField(
        label=_("Способ оплаты"),
        widget=forms.RadioSelect(),
        choices=[
            ("0", _("Оплата картой")),
            ("1", _("Наличными/картой при получении")),
        ],
        initial="0",
    )

    def clean_phone_number(self):
        data = self.cleaned_data["phone_number"]
        if not data.isdigit():
            raise forms.ValidationError(
                _("Номер телефона должен содержать только цифры")
            )

        pattern = re.compile(r"^\d{10}$")
        if not pattern.match(data):
            raise forms.ValidationError(_("Неверный формат номера"))

        return data
