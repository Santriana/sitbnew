from django.contrib import admin
from .models import Organization
from autocompletefilter.admin import AutocompleteFilterMixin
from autocompletefilter.filters import AutocompleteListFilter
from rangefilter.filters import DateRangeFilter
from .forms import OrganizationForm


# Register your models here.


class OrganizationAdmin(AutocompleteFilterMixin, admin.ModelAdmin):
    model = Organization
    form = OrganizationForm
    list_display = [
        'id', 'name', 'ihs_id', 'created_at'
    ]
    search_fields = ['name', 'ihs_id']

    list_filter = [
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


admin.site.register(Organization, OrganizationAdmin)
