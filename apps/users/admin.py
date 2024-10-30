from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from .forms import UserChangeForm, UserAddForm, UserImportForm
from rangefilter.filters import DateRangeFilter
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from django.contrib.auth.models import Group
from django.urls import path
from import_export.admin import ImportExportModelAdmin
from import_export.formats import base_formats
from .resource import UserResource
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings

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
        [settings.LABEL_SITB, {'fields': [
            'code_fasyankes', 'sitb_rs_id', 'sitb_rs_pass', 'province', 'district',
        ]}],
        [settings.LABEL_SATU_SEHAT, {'fields': [
            'organization_id', 'client_id', 'client_secret', 'is_satusehat'
        ]}],
        ['Permissions', {'fields': ['is_staff', 'is_superuser', 'is_active']}],
    ]

    fieldsets_staff = [
        [None, {'fields': ['password', ]}],
        [settings.LABEL_SITB, {'fields': [
            'code_fasyankes', 'sitb_rs_id', 'sitb_rs_pass', 'province', 'district',
        ]}],
        [settings.LABEL_SATU_SEHAT, {'fields': [
            'organization_id', 'client_id', 'client_secret', 'is_satusehat'
        ]}],
    ]

    add_fieldsets = [
        [None, {'fields': ['name', 'email', 'password1', 'password2', ]}],
        [settings.LABEL_SITB, {'fields': [
            'code_fasyankes', 'sitb_rs_id', 'sitb_rs_pass', 'province', 'district',
        ]}],
        [settings.LABEL_SATU_SEHAT, {'fields': [
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
    
    def get_import_form(self):
        """
        Get the form type used to read the import format and file.
        """
        return UserImportForm

    def get_rangefilter_date_joined_title(self, request, field_path):
        return 'By date joined'

    def has_delete_permission(self, request, obj=None):
        return False
    
    def response_add(self, request, obj, post_url_continue=None):
        return super().response_add(request, obj, post_url_continue=reverse("admin:users_user_changelist"))
    
    def response_change(self, request, obj):
        if request.user.is_superuser:
            return redirect(reverse("admin:users_user_changelist"))
        else :
            return redirect(reverse("admin:index"))

    def has_export_permission(self, request):
        return request.user.is_superuser
        
    def has_import_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if request.user.is_staff and obj != None:
            return True
        else :
            return False
    
    def get_queryset (self, request):
        if request.user.is_superuser:
            return User.objects
        else :
            return User.objects.filter(id = request.user.id)
    
    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            return super().get_fieldsets(request, obj)
        elif request.user.is_staff:
            return self.fieldsets_staff

admin.AdminSite.site_header = "Usaid"
admin.AdminSite.enable_nav_sidebar = False
admin.site.register(User, UserAdmin)