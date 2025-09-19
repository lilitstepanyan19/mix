from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    # Stripe
    path('process/<int:order_id>/', views.payment_process, name='process'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),

    # Idram
    path('idram/start/<int:order_id>/', views.idram_start, name='idram_start'),
    path('idram/return/success/', views.idram_return_success, name='idram_return_success'),
    path('idram/return/fail/', views.idram_return_fail, name='idram_return_fail'),
    path('idram/callback/', views.idram_callback, name='idram_callback'),

    # UnitPay
    path('unitpay/start/<int:order_id>/', views.unitpay_start, name='unitpay_start'),
    path('unitpay/callback/', views.unitpay_callback, name='unitpay_callback'),

    # Общие
    path('completed/', views.payment_completed, name='completed'),
    path('canceled/', views.payment_canceled, name='canceled'),
]
