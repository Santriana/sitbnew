from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from .forms import UserChangeForm, UserAddForm
from rangefilter.filters import DateRangeFilter
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from django.contrib.auth.models import Group
from django.urls import path
from import_export.admin import ImportExportModelAdmin
from import_export.formats import base_formats
from .resource import UserResource

admin.site.unregister(OutstandingToken)
admin.site.unregister(BlacklistedToken)
admin.site.unregister(Group)


class UserAdmin(ImportExportModelAdmin, BaseUserAdmin):
    resource_class = UserResource
    import_template_name = "users/useradmin_import.html"
    form = UserChangeForm
    add_form = UserAddForm
    model = User
    list_display = [
        'id',
        'name',
        'email',
        'organization_id',
        'is_active',
        'is_staff',
        'is_superuser'
    ]

    list_filter = [
        'is_active',
        'is_superuser',
        'is_staff',
        ['date_joined', DateRangeFilter],
    ]

    fieldsets = [
        [None, {'fields': ['name', 'email', 'password', ]}],
        ['SITB', {'fields': [
            'code_fasyankes', 'sitb_rs_id', 'sitb_rs_pass', 'province', 'district',
        ]}],
        ['Satu Sehat', {'fields': [
            'organization_id', 'client_id', 'client_secret', 'is_satusehat'
        ]}],
        ['Permissions', {'fields': ['is_staff', 'is_superuser', 'is_active']}],
    ]

    add_fieldsets = [
        [None, {'fields': ['name', 'email', 'password', ]}],
        ['SITB', {'fields': [
            'code_fasyankes', 'sitb_rs_id', 'sitb_rs_pass', 'province', 'district',
        ]}],
        ['Satu Sehat', {'fields': [
            'organization_id', 'client_id', 'client_secret', 'is_satusehat'
        ]}],
        ['Permissions', {'fields': ['is_staff', 'is_superuser', 'is_active']}],
    ]

    readonly_fields = []

    search_fields = [
        'email', 'organization_id', 'location_id'
    ]
    ordering = ['-date_joined', ]
    date_hierarchy = 'created_at'

    def get_export_formats(self):
        """
        Returns available export formats.
        """
        formats = (
            base_formats.JSON,
        )
        return [fmt for fmt in formats if fmt().can_export()]
    
    def get_import_formats(self):
        """
        Returns available import formats.
        """
        formats = (
            base_formats.JSON,
        )
        return [fmt for fmt in formats if fmt().can_import()]

    def get_rangefilter_date_joined_title(self, request, field_path):
        return 'By date joined'

    def has_delete_permission(self, request, obj=None):
        return False
    
    def response_add(self, request, obj, post_url_continue=None):
        return super().response_add(request, obj, post_url_continue='/admin/users/user/')


admin.AdminSite.site_header = "Usaid"
admin.AdminSite.enable_nav_sidebar = False
admin.site.register(User, UserAdmin)