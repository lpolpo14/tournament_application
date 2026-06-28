# users/urls.py

from django.urls import path

from .views import (
    csrf,
    register_view,
    login_view,
    logout_view,
    me_view,
)

urlpatterns = [
    path("csrf/", csrf, name="csrf"),
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("me/", me_view, name="me"),
]