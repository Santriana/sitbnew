from django.urls import path
from .views import TransactionSitbCreateApiView, TransactionSitbDetailApiView

urlpatterns = [
    path('data/<int:pk>/detail/', TransactionSitbDetailApiView.as_view(), name='transaction-data-detail-sitb'),
    path('data', TransactionSitbCreateApiView.as_view(), name='transaction-data-sitb'),
]
