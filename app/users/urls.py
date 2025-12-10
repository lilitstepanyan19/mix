from django.urls import path

from users import views

app_name = 'users'

urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('registration/', views.UserRegistrationView.as_view(), name='registration'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('users-cart/', views.UserCartView.as_view(), name='users_cart'),
    path('registration/password-reset/', views.UserPasswordResetView.as_view(), name='password_reset'),
    path('registration/password-reset-done/', views.UserPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('registration/password-reset-confirm/<uidb64>/<token>/', views.UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('registration/password-reset-complete/', views.UserPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('logout/', views.logout, name='logout'),
]