# users/views.py

import json

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST
from rest_framework.exceptions import ValidationError

from .serializers import RegisterSerializer, UserSerializer


@require_GET
@ensure_csrf_cookie # Sends a cookie
def csrf(request):
    return JsonResponse({"csrfToken": get_token(request)})


@require_POST
@csrf_protect # Blocks fake website requests.
def register_view(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"detail": "Invalid JSON."},
            status=400,
        )

    serializer = RegisterSerializer(data=data)
    if not serializer.is_valid():
        return JsonResponse(serializer.errors, status=400)
    user = serializer.save()
    login(request, user)
    return JsonResponse(
        {
            "detail": "Registered successfully.",
            "user": UserSerializer(user).data,
        },
        status=201,
    )

@require_POST
@csrf_protect
def login_view(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"detail": "Invalid JSON."},
            status=400,
        )

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return JsonResponse(
            {"detail": "Username and password are required."},
            status=400,
        )

    user = authenticate(
        request,
        username=username,
        password=password,
    )

    if user is None:
        return JsonResponse(
            {"detail": "Invalid username or password."},
            status=400,
        )

    login(request, user)

    return JsonResponse({
        "detail": "Logged in successfully.",
        "user": UserSerializer(user).data,
    })


@require_POST
@csrf_protect
def logout_view(request):
    logout(request)

    return JsonResponse({
        "detail": "Logged out successfully.",
    })


@require_GET
def me_view(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {
                "is_authenticated": False,
                "user": None,
            },
            status=200,
        )

    return JsonResponse({
        "is_authenticated": True,
        "user": UserSerializer(request.user).data,
    })