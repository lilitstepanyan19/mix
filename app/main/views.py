from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from goods.models import Products


class IndexView(TemplateView):
    template_name = "main/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Home - Главная")
        context["products"] = Products.objects.all()
        return context


class AboutView(TemplateView):
    template_name = "main/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Home - О нас")
        context["content"] = _("О нас")
        context["text_on_page"] = _(
            "Текст о том почему этот магазин такой классный, и какой хороший товар."
        )
        return context


class ContactView(TemplateView):
    template_name = "main/contact.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Contact - Контакты")
        context["content"] = _("Our contacts")
        context["text_on_page"] = _("Email: , Phone: , Address: ")
        return context


class DeliveryView(TemplateView):
    template_name = "main/delivery.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Delivery - Доставка и оплата")
        context["content"] = _("Delivery and payment")
        context["text_on_page"] = _("For delivery call 0000...")
        return context
