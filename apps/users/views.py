from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import AllowAny
from .serializers import UserTokenSerializer
from .serializers import TokenRefreshSerializer


# Create your views here.

class UserTokenApiView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = UserTokenSerializer


class UserTokenRefreshApiView(TokenRefreshView):
    permission_classes = (AllowAny,)
    serializer_class = TokenRefreshSerializer
