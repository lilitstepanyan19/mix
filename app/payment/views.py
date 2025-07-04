<<<<<<< HEAD
from django.http import HttpResponse
=======
>>>>>>> f1e1a7313c7dfd7c49c7f052a377d50f49b42579
from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal
from django.urls import reverse
from django.conf import settings
from orders.models import Order
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION

<<<<<<< HEAD
def payment_process(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if not order_id:
        return HttpResponse("No order_id in session", status=400)
=======
def payment_process(request):
    order_id = request.session.get('order_id', None)
    order = get_object_or_404(Order, id=order_id)
>>>>>>> f1e1a7313c7dfd7c49c7f052a377d50f49b42579
    
    if request.method == 'POST':
        success_url = request.build_absolute_url(reverse('payment:completed'))
        cancel_url = request.build_absolute_url(reverse('payment:canceled'))
<<<<<<< HEAD

        session_data = {
            'mode': 'payment',
=======
        session_data = {
            'mode' : 'payment',
>>>>>>> f1e1a7313c7dfd7c49c7f052a377d50f49b42579
            'client_reference_id': order.id,
            'success_url': success_url,
            'cancel_url': cancel_url,
            'line_items': [],
        }
<<<<<<< HEAD

=======
>>>>>>> f1e1a7313c7dfd7c49c7f052a377d50f49b42579
        for item in order.items.all():
            discounted_price = item.product.sell_price()
            session_data['line_items'].append({
                'price_data': {
<<<<<<< HEAD
                    'unit_amount': int(discounted_price * Decimal('100')),
                    'currency': 'usd',
=======
                    'unit_amount' : int(discounted_price * Decimal('100')), 
                    'currency': 'usd',  # Change to your desired currency
>>>>>>> f1e1a7313c7dfd7c49c7f052a377d50f49b42579
                    'product_data': {
                        'name': item.product.name,
                    },
                },
                'quantity': item.quantity,
            })
<<<<<<< HEAD

        session = stripe.checkout.Session.create(**session_data)
        return redirect(session.url, code=303)

    return render(request, 'payment/process.html', {'order': order})

=======
        session = stripe.checkout.Session.create(**session_data)
        return redirect(session.url, code=303)
    else:
        return render(request, 'payment:process.html', locals())
>>>>>>> f1e1a7313c7dfd7c49c7f052a377d50f49b42579
    

def payment_completed(request):
    # order_id = request.session.get('order_id', None)
    # if order_id:
    #     order = get_object_or_404(Order, id=order_id)
    #     order.paid = True
    #     order.save()
    #     del request.session['order_id']
    return render(request, 'payment/completed.html', locals())

def payment_canceled(request):
    # order_id = request.session.get('order_id', None)
    # if order_id:
    #     del request.session['order_id']
    return render(request, 'payment/canceled.html', locals())