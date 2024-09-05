from django.urls import path
from .views import UserTokenApiView, UserTokenRefreshApiView

urlpatterns = [
    path('token', UserTokenApiView.as_view(), name='users-token'),
    path('token/refresh', UserTokenRefreshApiView.as_view(), name='users-token-refresh')
]