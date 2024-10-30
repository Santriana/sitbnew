from django.db import models
from usaid.models import AbstractModel


# Create your models here.

class Location(AbstractModel):
    organization = models.ForeignKey('organization.Organization', on_delete=models.CASCADE,
                                     related_name="location_organization", blank=False, null=False)
    ihs_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return '{}'.format(self.name)
