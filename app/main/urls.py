from django.urls import path
# from django.views.decorators.cache import cache_page

from main import views

app_name = 'main'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('delivery/', views.DeliveryView.as_view(), name='delivery'),
]

# urlpatterns = [
#     path('', views.IndexView.as_view(), name='index'),
#     path('about/', cache_page(60)(views.AboutView.as_view()), name='about'),
# ]