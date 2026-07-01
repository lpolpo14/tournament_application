# users/serializers.py

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import ASCIIUsernameValidator
from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError

from .models import UserDetails

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    """
    Serializer for registering a new user.
    Safely validates the user.
    """
    username_validator = ASCIIUsernameValidator()
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    role = serializers.ChoiceField(
        choices=UserDetails.Role.choices,
        default=UserDetails.Role.TEAM_MANAGER,
    )

    # Is the username unique?
    def validate_username(self, value):

        try:
            self.username_validator(value)
        except DjangoValidationError:
            raise serializers.ValidationError(
                "Username may contain only English letters, numbers, and @/./+/-/_."
            )
        
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    # Is the email unique?
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already used.")
        return value

    # Did the user input the same passwords during registration?
    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })

        # Uses django's configured password validators.
        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        """
        Creates new user and usreDetails objects.
        """
        role = validated_data.pop("role") # The user can register as any role for showcase reasons.
        validated_data.pop("confirm_password")

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        # create_user hashes password using the PBKDF2 (SHA256) algorithm

        UserDetails.objects.create(
            user=user,
            role=role,
        )

        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Safe serializer that exposes safe data regarding a user object.
    Does not expose sensitive data like passwords.
    """
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "role"]

    def get_role(self, obj):
        profile = getattr(obj, "details", None)
        return profile.role if profile else None