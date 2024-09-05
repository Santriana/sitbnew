from django.db import models
from usaid.models import AbstractModel


# Create your models here.

class Organization(AbstractModel):
    name = models.CharField(max_length=255, blank=True, null=True)
    ihs_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)

    def __str__(self):
        return '{}'.format(self.name)
