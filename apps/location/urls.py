from django.urls import path
from .views import FilterLocationAutocomplete

urlpatterns = [
    path('filter-location', FilterLocationAutocomplete.as_view(), name='location-filter-location')
]
