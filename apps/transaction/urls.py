from django.urls import path
from .views import TransactionCreateApiView, TransactionFhirCreateApiView, TransactionDetailApiView

urlpatterns = [
    path('data/<int:pk>/detail/', TransactionDetailApiView.as_view(), name='transaction-data-detail'),
    path('data/fhir', TransactionFhirCreateApiView.as_view(), name='transaction-data-fhir'),
    path('data', TransactionCreateApiView.as_view(), name='transaction-data'),
]
