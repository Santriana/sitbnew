from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView

urlpatterns = [
    path('users/', include('apps.users.urls')),
    path('organization/', include('apps.organization.urls')),
    path('location/', include('apps.location.urls')),
    path('transaction/', include('apps.transaction.urls')),
    path('v2/transaction/', include('apps.transaction.urls_v2')),
    # OpenAPI 3 Schema
    path('schema/', SpectacularAPIView.as_view(), name='schema'),

]
