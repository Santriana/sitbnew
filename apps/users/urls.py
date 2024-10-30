from django.urls import path
from .views import UserTokenApiView, UserTokenRefreshApiView, change_profile_staff_view

urlpatterns = [
    path('token', UserTokenApiView.as_view(), name='users-token'),
    path('token/refresh', UserTokenRefreshApiView.as_view(), name='users-token-refresh'),
    path('change-profile', change_profile_staff_view, name='change-profile')
]