from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
<<<<<<< HEAD
    path('process/<int:order_id>/', views.payment_process, name='process'),
=======
    path('process/', views.payment_process, name='process'),        
>>>>>>> f1e1a7313c7dfd7c49c7f052a377d50f49b42579
    path('completed/', views.payment_completed, name='completed'),
    path('canceled/', views.payment_canceled, name='canceled'),
    # path('webhook/', views.payment_webhooks, name='webhooks'),
]