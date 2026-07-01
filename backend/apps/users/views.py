# users/views.py

import json

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie, csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from rest_framework.exceptions import ValidationError

from .serializers import RegisterSerializer, UserSerializer


@require_GET
@ensure_csrf_cookie # Sends a cookie
def csrf(request):
    """
    Sends a CSRF Cookie to the user.
    """
    return JsonResponse({"csrfToken": get_token(request)})


@require_POST
@csrf_protect
def register_view(request):
    """
    Handles authentication based on the provided json request.
    The user is logged in immediately after successful registration.
    """
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
    user = serializer.save() # Save the user.
    login(request, user)
    return JsonResponse(
        {
            "detail": "Registered successfully.",
            "user": UserSerializer(user).data,
        },
        status=201,
    )

@require_POST
@csrf_protect # Blocks fake website requests.
def login_view(request):
    """
    Authenticates the user based on the provided JSON request.
    """
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

    # Automatically hashes the password (Django's Auth Mechanism).
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

    login(request, user) # Stores the user's session ID in the session.

    return JsonResponse({
        "detail": "Logged in successfully.",
        "user": UserSerializer(user).data,
    })


@require_POST
@csrf_protect
def logout_view(request):
    logout(request) # Automatic logout using Django's Auth System.
    # This clears the active Django Session.

    return JsonResponse({
        "detail": "Logged out successfully.",
    })


@require_GET
def me_view(request):
    """
    Returns details whether the frontend user is logged in or not.
    """
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

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import UserDetails
from .serializers import UserSerializer
from .permissions import IsSportsAdmin
from django.contrib.auth import get_user_model

User = get_user_model()

@api_view(["GET"])
@permission_classes([IsAuthenticated, IsSportsAdmin])
def referees_view(request):
    """
    Returns all users that are referees.
    This endpoint can be used only by authenticated Sports Admins.
    """
    referees = (
        User.objects
        .filter(details__role=UserDetails.Role.REFEREE)
        .order_by("username")
    )

    return Response(UserSerializer(referees, many=True).data)