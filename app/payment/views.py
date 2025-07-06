from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal
from django.urls import reverse
from django.conf import settings
from orders.models import Order
import stripe

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION


def payment_process(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        success_url = request.build_absolute_uri(reverse('payment:completed'))
        cancel_url = request.build_absolute_uri(reverse('payment:canceled'))

        session_data = {
            'mode': 'payment',
            'client_reference_id': order.id,
            'success_url': success_url,
            'cancel_url': cancel_url,
            'line_items': [],
        }

        for item in order.items.all():
            discounted_price = item.product.sell_price()
            session_data['line_items'].append({
                'price_data': {
                    'unit_amount': int(discounted_price * Decimal('100')),
                    'currency': 'usd',
                    'product_data': {
                        'name': item.product.name,
                    },
                },
                'quantity': item.quantity,
            })

        session = stripe.checkout.Session.create(**session_data)
        request.session['order_id'] = order.id  # 💡 Сохраняем для последующей обработки

        return redirect(session.url, code=303)

    return render(request, 'payment/process.html', {
        'order': order,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    })


def payment_completed(request):
    order_id = request.session.get('order_id')
    order = None

    if order_id:
        order = get_object_or_404(Order, id=order_id)
        order.paid = True
        send_order_emails(order)
        order.save()
        del request.session['order_id']

    return render(request, 'payment/completed.html', {'order': order})


def payment_canceled(request):
    request.session.pop('order_id', None)
    return render(request, 'payment/canceled.html')


@csrf_exempt  # Stripe не отправляет CSRF токен
@require_POST
def create_checkout_session(request):
    import json
    data = json.loads(request.body)
    order_id = data.get("order_id")

    try:
        order = Order.objects.get(id=order_id)

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'Заказ №{order.id}',
                    },
                    'unit_amount': int(order.get_total_cost() * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('payment:completed')),
            cancel_url=request.build_absolute_uri(reverse('payment:canceled')),
            client_reference_id=str(order.id)
        )

        return JsonResponse({'id': session.id})
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)

def send_order_emails(order):
    subject_user = f"Ваш заказ №{order.id} успешно оплачен"
    subject_admin = f"Новый заказ №{order.id} оформлен"

    # Покупателю
    message_user = render_to_string('emails/order_user.html', {'order': order})
    send_mail(subject_user, message_user, settings.DEFAULT_FROM_EMAIL, [order.email])

    # Администратору
    message_admin = render_to_string('emails/order_admin.html', {'order': order})
    send_mail(subject_admin, message_admin, settings.DEFAULT_FROM_EMAIL, [settings.ADMIN_EMAIL])

# @csrf_exempt
# def stripe_webhook(request):
#     payload = request.body
#     sig_header = request.META['HTTP_STRIPE_SIGNATURE']
#     endpoint_secret = settings.STRIPE_WEBHOOK_SECRET  # нужно задать

#     try:
#         event = stripe.Webhook.construct_event(
#             payload, sig_header, endpoint_secret
#         )
#     except ValueError as e:
#         return HttpResponse(status=400)
#     except stripe.error.SignatureVerificationError as e:
#         return HttpResponse(status=400)

#     if event['type'] == 'checkout.session.completed':
#         session = event['data']['object']
#         order_id = session.get('client_reference_id')
#         if order_id:
#             try:
#                 order = Order.objects.get(id=order_id)
#                 order.paid = True
#                 order.save()
#             except Order.DoesNotExist:
#                 pass

#     return HttpResponse(status=200)