from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.serializers import TokenRefreshSerializer as BaseTokenRefreshSerializer
from django.utils.html import escape
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from rest_framework import serializers
from apps.transaction.data import is_valid
from usaid.settings import INVALID_INPUT


class UserTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super(UserTokenSerializer, cls).get_token(user)

        # Add custom claims
        token['organization_id'] = user.organization_id
        return token

    def validate_email(self, attrs):
        try:
            validate_email(attrs)
        except ValidationError:
            raise serializers.ValidationError({"email": "{}.".format(INVALID_INPUT)})
        return escape(attrs)

    def validate_password(self, attrs):
        return escape(attrs)

    def validate(self, data):
        password = data['password']

        if not is_valid(password):
            raise serializers.ValidationError({"password": "{}.".format(INVALID_INPUT)})

        return super().validate(data)


class TokenRefreshSerializer(BaseTokenRefreshSerializer):
    def validate_refresh(self, attrs):
        return escape(attrs)
