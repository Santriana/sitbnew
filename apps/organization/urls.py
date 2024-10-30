from django.urls import path
from .views import FilterOrganizationAutocomplete


urlpatterns = [
    path('filter-organization', FilterOrganizationAutocomplete.as_view(), name='organization-filter-organization')
]
