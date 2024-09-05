from django import forms
from .models import Location
from dal import autocomplete


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = [
            'organization', 'name', 'ihs_id'
        ]
        exclude = ['created_at', 'created_by', 'updated_at', 'updated_by', 'deleted_on']
        widgets = {
            'organization': autocomplete.ModelSelect2(url='organization-filter-organization')
        }
