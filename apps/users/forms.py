from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import gettext_lazy as _
from .models import User, Province, District
from django_select2.forms import ModelSelect2Widget


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


class UserAddForm(forms.ModelForm):
    password = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={'class': 'vTextField'})
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
        fields = '__all__'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.save()
        return user
