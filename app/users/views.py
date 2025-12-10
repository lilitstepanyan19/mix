from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import auth, messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.db.models import Prefetch
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.utils.translation import gettext_lazy as _

from carts.models import Cart
from common.mixins import CacheMixin
from orders.models import Order, OrderItem
from users.forms import ProfileForm, UserLoginForm, UserRegistrationForm


class UserLoginView(LoginView):
    template_name = "users/login.html"
    form_class = UserLoginForm

    def get_success_url(self):
        redirect_page = self.request.POST.get("next", None)
        if redirect_page and redirect_page != reverse("user:logout"):
            return redirect_page
        return reverse_lazy("main:index")

    def form_valid(self, form):
        session_key = self.request.session.session_key
        user = form.get_user()

        if user:
            auth.login(self.request, user)

            if session_key:
                # удалить старые корзины авторизованного пользователя
                Cart.objects.filter(user=user).delete()
                # добавить корзины из анонимной сессии
                Cart.objects.filter(session_key=session_key).update(user=user)

            # Сообщение о входе с переводом
            messages.success(
                self.request,
                _("%(username)s, you are logged in") % {"username": user.username},
            )

            return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Home - Login")
        return context


class UserRegistrationView(CreateView):
    template_name = "users/registration.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("users:profile")

    def form_valid(self, form):
        session_key = self.request.session.session_key
        user = form.instance

        if user:
            form.save()
            auth.login(self.request, user)

        if session_key:
            Cart.objects.filter(session_key=session_key).update(user=user)

        # Сообщение о регистрации с переводом
        messages.success(
            self.request,
            _("%(username)s, you have successfully registered and logged in")
            % {"username": user.username},
        )

        return HttpResponseRedirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Home - Registration")
        return context


class UserProfileView(LoginRequiredMixin, CacheMixin, UpdateView):
    template_name = "users/profile.html"
    form_class = ProfileForm
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, _("Profile successfully updated"))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("An error occurred"))
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Home - Profile")

        orders = (
            Order.objects.filter(user=self.request.user)
            .prefetch_related(
                Prefetch(
                    "items",
                    queryset=OrderItem.objects.select_related("product"),
                )
            )
            .order_by("-id")
        )

        context["orders"] = self.set_get_cache(
            orders, f"user_{self.request.user.id}_orders", 60
        )
        return context


class UserCartView(TemplateView):
    template_name = "users/users_cart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Home - Cart")
        return context

class UserPasswordChangeView(LoginRequiredMixin, TemplateView):
    template_name = "users/password_change.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Home - Password Change")
        return context


class UserPasswordResetView(PasswordResetView):
    # Страница запроса сброса пароля

    template_name = "users/registration/password_reset.html"
    email_template_name = "users/registration/password_reset_email.html"
    subject_template_name = "users/registration/password_reset_email.txt"
    success_url = reverse_lazy("users:password_reset_done")
    extra_context = {"title": _("Восстановление пароля")}

    def get_email_context(self):
        context = super().get_email_context()
        context['protocol'] = 'https' if self.request.is_secure() else 'http'
        context['domain'] = self.request.get_host()
        context["request"] = self.request
        return context


class UserPasswordResetDoneView(PasswordResetDoneView):
    # Страница подтверждения отправки email

    template_name = "registration/password_reset_done.html"
    extra_context = {"title": _("Письмо отправлено")}


class UserPasswordResetConfirmView(PasswordResetConfirmView):
    # Страница, где пользователь вводит новый пароль

    template_name = "registration/password_reset_confirm.html"
    success_url = reverse_lazy("users:password_reset_complete")
    extra_context = {"title": _("Сброс пароля")}


class UserPasswordResetCompleteView(PasswordResetCompleteView):
    # Страница подтверждения успешного сброса

    template_name = "registration/password_reset_complete.html"
    extra_context = {"title": _("Пароль успешно изменён")}


# class UserPasswordResetView(PasswordResetView):
#     template_name = "registration/password_reset.html"
#     email_template_name = "registration/password_reset_email.html"
#     subject_template_name = "registration/password_reset_subject.txt"


@login_required
def logout(request):
    messages.success(
        request,
        _("%(username)s, you have logged out") % {"username": request.user.username},
    )
    auth.logout(request)
    return redirect(reverse("main:index"))
