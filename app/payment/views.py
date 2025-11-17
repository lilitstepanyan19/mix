from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from urllib.parse import urljoin
from decimal import Decimal
import hashlib
import json

from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _

import stripe

from orders.models import Order
from .utils import idram_md5_signature, unitpay_build_redirect_url

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION


def payment_process(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        success_url = request.build_absolute_uri(reverse("payment:completed"))
        cancel_url = request.build_absolute_uri(reverse("payment:canceled"))

        session_data = {
            "mode": "payment",
            "client_reference_id": order.id,
            "success_url": success_url,
            "cancel_url": cancel_url,
            "line_items": [],
        }

        for item in order.items.all():
            discounted_price = item.product.sell_price()
            session_data["line_items"].append(
                {
                    "price_data": {
                        "unit_amount": int(discounted_price * Decimal("100")),
                        "currency": "usd",
                        "product_data": {
                            "name": _("Order #%(order_id)s") % {"order_id": order.id},
                        },
                    },
                    "quantity": item.quantity,
                }
            )

        session = stripe.checkout.Session.create(**session_data)
        request.session["order_id"] = order.id
        return redirect(session.url, code=303)

    return render(
        request,
        "payment/process.html",
        {"order": order, "stripe_public_key": settings.STRIPE_PUBLIC_KEY},
    )


def _idram_form_context(order: Order):
    edp_rec_account = settings.IDRAM_MERCHANT_ID
    edp_bill_no = str(order.id)
    edp_amount = str(order.get_total_cost())
    edp_currency = "AMD"
    edp_description = _("Order #%(order_id)s") % {"order_id": order.id}

    success_url = urljoin(
        settings.PAYMENT_CALLBACK_HOST, reverse("payment:idram_return_success")
    )
    fail_url = urljoin(
        settings.PAYMENT_CALLBACK_HOST, reverse("payment:idram_return_fail")
    )
    notify_url = urljoin(
        settings.PAYMENT_CALLBACK_HOST, reverse("payment:idram_callback")
    )

    edp_hash = idram_md5_signature(
        edp_rec_account,
        edp_bill_no,
        edp_amount,
        edp_currency,
        edp_description,
        settings.IDRAM_SECRET_KEY,
    )

    return {
        "action": settings.IDRAM_PAY_URL,
        "EDP_LANGUAGE": "ru",
        "EDP_REC_ACCOUNT": edp_rec_account,
        "EDP_BILL_NO": edp_bill_no,
        "EDP_AMOUNT": edp_amount,
        "EDP_CURRENCY": edp_currency,
        "EDP_DESCRIPTION": edp_description,
        "EDP_EMAIL": (
            getattr(order, "user", None).email if getattr(order, "user", None) else ""
        ),
        "EDP_NOTIFY_URL": notify_url,
        "EDP_SUCCESS_URL": success_url,
        "EDP_FAIL_URL": fail_url,
        "EDP_HASH": edp_hash,
    }


def idram_start(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = _idram_form_context(order)
    return render(request, "payment/idram_autopost.html", context)


@csrf_exempt
def idram_callback(request):
    data = request.POST or request.GET
    if not data:
        return HttpResponseBadRequest(_("No data"))

    try:
        bill_no = data.get("EDP_BILL_NO")
        amount = data.get("EDP_AMOUNT")
        currency = data.get("EDP_CURRENCY")
        description = data.get("EDP_DESCRIPTION", "")
        rec_account = data.get("EDP_REC_ACCOUNT")
        their_hash = data.get("EDP_HASH")

        my_hash = idram_md5_signature(
            rec_account,
            bill_no,
            amount,
            currency,
            description,
            settings.IDRAM_SECRET_KEY,
        )

        if my_hash.lower() != (their_hash or "").lower():
            return HttpResponseBadRequest(_("Bad signature"))

        order = get_object_or_404(Order, id=bill_no)
        if not order.paid:
            order.paid = True
            order.save()
            try:
                send_order_emails(order)
            except Exception:
                pass

        return HttpResponse("OK")
    except Exception as e:
        return HttpResponseBadRequest(str(e))


def idram_return_success(request):
    return redirect("payment:completed")


def idram_return_fail(request):
    return redirect("payment:canceled")


def unitpay_start(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    params = {
        "account": str(order.id),
        "desc": _("Order #%(order_id)s") % {"order_id": order.id},
    }
    pay_url = unitpay_build_redirect_url(
        settings.UNITPAY_PUBLIC_KEY, settings.UNITPAY_BASE_URL, **params
    )
    return redirect(pay_url)


@csrf_exempt
def unitpay_callback(request):
    method = request.GET.get("method") or request.POST.get("method")
    params = request.GET.dict()
    if not method:
        return JsonResponse({"error": {"message": _("No method")}}, status=400)

    up = params.get("params") if isinstance(params.get("params"), dict) else params

    try:
        secret = settings.UNITPAY_SECRET_KEY
        sign_client = up.get("signature") or up.get("sign") or ""
        sign_params = {k: v for k, v in up.items() if k not in ("signature", "sign")}
        pieces = (
            [method]
            + [str(sign_params[k]) for k in sorted(sign_params.keys())]
            + [secret]
        )
        check_string = "{up}".join(pieces)
        calc = hashlib.sha256(check_string.encode("utf-8")).hexdigest()

        if calc.lower() != sign_client.lower():
            return JsonResponse({"error": {"message": _("Bad signature")}}, status=400)

        account = up.get("account") or up.get("orderId")
        order = get_object_or_404(Order, id=account)

        if method == "check":
            return JsonResponse({"result": {"message": "OK"}})

        if method == "pay":
            if not order.paid:
                order.paid = True
                order.save()
                try:
                    send_order_emails(order)
                except Exception:
                    pass
            return JsonResponse({"result": {"message": "OK"}})

        if method == "error":
            return JsonResponse({"result": {"message": "OK"}})

        return JsonResponse({"error": {"message": _("Unknown method")}}, status=400)

    except Exception as e:
        return JsonResponse({"error": {"message": str(e)}}, status=400)


def payment_completed(request):
    order_id = request.session.get("order_id")
    order = None

    if order_id:
        order = get_object_or_404(Order, id=order_id)
        order.paid = True
        send_order_emails(order)
        order.save()
        del request.session["order_id"]

    return render(
        request,
        "payment/completed.html",
        {"order": order, "title": _("Payment completed")},
    )


def payment_canceled(request):
    request.session.pop("order_id", None)
    return render(request, "payment/canceled.html", {"title": _("Payment canceled")})


@csrf_exempt
@require_POST
def create_checkout_session(request):
    data = json.loads(request.body)
    order_id = data.get("order_id")

    try:
        order = Order.objects.get(id=order_id)

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": _("Order #%(order_id)s") % {"order_id": order.id},
                        },
                        "unit_amount": int(order.get_total_cost() * 100),
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=request.build_absolute_uri(reverse("payment:completed")),
            cancel_url=request.build_absolute_uri(reverse("payment:canceled")),
            client_reference_id=str(order.id),
        )

        return JsonResponse({"id": session.id})
    except Order.DoesNotExist:
        return JsonResponse({"error": _("Order not found")}, status=404)


def send_order_emails(order):
    subject_user = _("Order #%(order_id)s successfully paid") % {"order_id": order.id}
    subject_admin = _("New order #%(order_id)s created") % {"order_id": order.id}

    message_user = render_to_string("emails/order_user.html", {"order": order})
    send_mail(subject_user, message_user, settings.DEFAULT_FROM_EMAIL, [order.email])

    message_admin = render_to_string("emails/order_admin.html", {"order": order})
    send_mail(
        subject_admin,
        message_admin,
        settings.DEFAULT_FROM_EMAIL,
        [settings.ADMIN_EMAIL],
    )
