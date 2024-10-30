from django.shortcuts import redirect
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import AllowAny
from .serializers import UserTokenSerializer
from .serializers import TokenRefreshSerializer
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from django.urls import reverse


# Create your views here.

class UserTokenApiView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = UserTokenSerializer


class UserTokenRefreshApiView(TokenRefreshView):
    permission_classes = (AllowAny,)
    serializer_class = TokenRefreshSerializer

@require_http_methods(["GET"])
@staff_member_required
def change_profile_staff_view(request):
    current_user_id = str(request.user.id)
    if request.user.is_staff and not request.user.is_superuser:
       return redirect(reverse("admin:users_user_change", args=[current_user_id]))