from django import forms
from .models import Transaction
from dal import autocomplete


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            'location', 'status', 'error_messages',
            'last_retry', 'count_retry',
        ]
        exclude = ['created_at', 'created_by', 'updated_at', 'updated_by', 'deleted_on', 'response_data', 'raw_data']
        widgets = {
            'location': autocomplete.ModelSelect2(url='location-filter-location')
        }
