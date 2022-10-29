from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path(
        'logout/',
        LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    path(
        'login/',
        LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),

    path(
        'password_reset/done/',
        views.password_reset_done,
        name='password_reset_done'
    ),
    path(
        'password_reset/<uidb64>/<token>/',
        views.password_reset_confirm,
        name='password_reset_confirm'
    ),
    path(
        'password_reset/complete/',
        views.password_reset_complete,
        name='password_reset_complete'
    ),
    path(
        'password_change/',
        views.password_change,
        name='password_change'
    ),
    path(
        'password_change/done/',
        views.password_change_done,
        name='password_change_done'
    ),
    path(
        'password_reset/',
        views.password_reset,
        name='password_reset'
    ),
    path('contact/', views.ContactView.as_view(), name='contact')
]
