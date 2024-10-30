from django import forms
from .models import Organization


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = [
            'name', 'ihs_id'
        ]
        exclude = ['created_at', 'created_by', 'updated_at', 'updated_by', 'deleted_on']
