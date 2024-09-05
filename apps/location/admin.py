from django.contrib import admin
from .models import Location
from autocompletefilter.admin import AutocompleteFilterMixin
from autocompletefilter.filters import AutocompleteListFilter
from rangefilter.filters import DateRangeFilter
from .forms import LocationForm
# Register your models here.


class LocationAdmin(AutocompleteFilterMixin, admin.ModelAdmin):
    model = Location
    form = LocationForm
    list_display = [
        'id', 'organization', 'name', 'ihs_id', 'created_at'
    ]
    search_fields = ['name', 'ihs_id']

    list_filter = [
        ['organization', AutocompleteListFilter],
        ['created_by', AutocompleteListFilter],
        ['created_at', DateRangeFilter]
    ]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_rangefilter_created_at_title(self, request, field_path):
        return 'By created at'


admin.site.register(Location, LocationAdmin)