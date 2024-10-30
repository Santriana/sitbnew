from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import gettext_lazy as _
from .models import User, Province, District
from django_select2.forms import ModelSelect2Widget
from import_export.forms import ImportForm
from django.core.validators import FileExtensionValidator
import magic
from import_export.formats import base_formats
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(
        label=_("Password"),
        help_text=_(
            'Raw passwords are not stored, so there is no way to see this '
            'user’s password, but you can change the password using '
            '<a href="{}">this form</a>.'
        ),
    )

    code_fasyankes = forms.CharField(
        label=_('Kode Fasyankes'),
        widget=forms.TextInput(attrs={'class': 'vTextField'}),
        required=True,
    )

    province = forms.ModelChoiceField(
        label=_('Provinsi'),
        queryset=Province.objects.all(),
        widget=ModelSelect2Widget(
            model=Province,
            search_fields=['name__icontains'],
            attrs={'data-placeholder': 'Pilih Provinsi', 'data-allow-clear': 'true', 'data-minimum-input-length': '0'},
        ),
        required=True,
    )

    district = forms.ModelChoiceField(
        label=_('Kabupaten'),
        queryset=District.objects.all(),
        widget=ModelSelect2Widget(
            model=District,
            search_fields=['name__icontains'],
            attrs={'data-placeholder': 'Pilih Kabupaten', 'data-allow-clear': 'true', 'data-minimum-input-length': '0'},
            dependent_fields={'province': 'province'},
        ),
        required=True,
    )

    sitb_rs_id = forms.CharField(
        label=_('RS ID'),
        widget=forms.TextInput(attrs={'class': 'vTextField'}),
        required=True,
    )

    sitb_rs_pass = forms.CharField(
        label=_("RS Password"),
        widget=forms.TextInput(attrs={'class': 'vTextField'}),
        required=True,
    )

    is_satusehat = forms.BooleanField(
        label=_('Active'),
        widget=forms.CheckboxInput(attrs={'class': 'vCheckboxInput'}),
        required=False,
    )

    class Meta:
        model = User
        fields = '__all__'

    def clean_password(self):
        return self.initial["password"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        password = self.fields.get('password')
        if password:
            password.help_text = password.help_text.format('../password/')
        user_permissions = self.fields.get('user_permissions')
        if user_permissions:
            user_permissions.queryset = user_permissions.queryset.select_related('content_type')


class UserAddForm(UserCreationForm):
    code_fasyankes = forms.CharField(
        label=_('Kode Fasyankes'),
        widget=forms.TextInput(attrs={'class': 'vTextField'}),
        required=True,
    )

    province = forms.ModelChoiceField(
        label=_('Provinsi'),
        queryset=Province.objects.all(),
        widget=ModelSelect2Widget(
            model=Province,
            search_fields=['name__icontains'],
            attrs={'data-placeholder': 'Pilih Provinsi', 'data-allow-clear': 'true', 'data-minimum-input-length': '0'},
        ),
        required=True,
    )

    district = forms.ModelChoiceField(
        label=_('Kabupaten'),
        queryset=District.objects.all(),
        widget=ModelSelect2Widget(
            model=District,
            search_fields=['name__icontains'],
            attrs={'data-placeholder': 'Pilih Kabupaten', 'data-allow-clear': 'true', 'data-minimum-input-length': '0'},
            dependent_fields={'province': 'province'},
        ),
        required=True,
    )

    sitb_rs_id = forms.CharField(
        label=_('RS ID'),
        widget=forms.TextInput(attrs={'class': 'vTextField'}),
        required=True,
    )

    sitb_rs_pass = forms.CharField(
        label=_('RS Password'),
        widget=forms.TextInput(attrs={'class': 'vTextField'}),
        required=True,
    )

    is_satusehat = forms.BooleanField(
        label=_('Active'),
        widget=forms.CheckboxInput(attrs={'class': 'vCheckboxInput', 'checked': 'checked'}),
        required=False,
    )

    class Meta:
        model = User
        fields = [
            'name', 'email', 'organization_id', 'client_id', 
            'client_secret', 'code_fasyankes', 'province', 'district', 
            'sitb_rs_id', 'sitb_rs_pass','is_satusehat', 'is_staff', 
            'is_active', 'date_joined'
        ]


class UserImportForm(ImportForm):
    import_file = forms.FileField(allow_empty_file=False, validators=[FileExtensionValidator(allowed_extensions=['json'])], label="")
   
    def clean_import_file(self):
        uploaded_file = self.cleaned_data.get('import_file')
        file_mime = magic.Magic(mime=True)
        file_mime_type = file_mime.from_buffer(uploaded_file.read(2048))
        allowed_mime_types = [base_formats.JSON.CONTENT_TYPE]
        if file_mime_type not in allowed_mime_types:
            raise forms.ValidationError('Please upload a file in JSON format. Set the Content-Type to application/json')

        return uploaded_file
