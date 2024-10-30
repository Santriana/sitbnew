from django.shortcuts import render
from django.db.models import Q
from .models import Location
from dal import autocomplete


# Create your views here.

class FilterLocationAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Location.objects.none()

        qs = Location.objects.all().order_by('id')

        if self.q:
            qs = qs.filter(
                Q(name__icontains=self.q) |
                Q(ihs_id__icontains=self.q)
            )
        return qs
