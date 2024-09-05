from django.db import models
from usaid.models import AbstractModel
from django.utils.translation import gettext_lazy as _


# Create your models here.

class TransactionStatus(models.IntegerChoices):
    SUCCESS = 0, _("Success")
    FAILED = 1, _("Failed")
    PENDING = 2, _("Pending")
    ERROR = 3, _("Error")


class Transaction(AbstractModel):
    location = models.ForeignKey('location.Location', on_delete=models.CASCADE,
                                 related_name="transaction_location", blank=True, null=True)
    status = models.PositiveSmallIntegerField(choices=TransactionStatus.choices, blank=True, null=True)
    raw_data = models.JSONField(blank=True, null=True)
    error_messages = models.TextField(blank=True, null=True)
    last_retry = models.DateTimeField(blank=True, null=True)
    count_retry = models.PositiveSmallIntegerField(default=0)
    response_data = models.TextField(blank=True, null=True)
    log = models.ForeignKey('transaction.Log', on_delete=models.CASCADE, related_name="transaction_log", blank=True, null=True)

    def __str__(self):
        return '{} - {}'.format(self.location, self.pk)

    class Meta:
        verbose_name = 'SatuSehat'
        verbose_name_plural = 'SatuSehat'

class TransactionSitb(AbstractModel):
    status = models.PositiveSmallIntegerField(choices=TransactionStatus.choices, blank=True, null=True)
    raw_data = models.JSONField(blank=True, null=True)
    error_messages = models.TextField(blank=True, null=True)
    last_retry = models.DateTimeField(blank=True, null=True)
    count_retry = models.PositiveSmallIntegerField(default=0)
    response_data = models.TextField(blank=True, null=True)
    log = models.ForeignKey('transaction.Log', on_delete=models.CASCADE, related_name="transaction_sitb_log", blank=True, null=True)

    class Meta:
        verbose_name = 'SITB'
        verbose_name_plural = 'SITB'

class Log(AbstractModel):
    id = models.AutoField(primary_key=True)
    satusehat_status = models.PositiveSmallIntegerField(choices=TransactionStatus.choices, blank=True, null=True)
    sitb_status = models.PositiveSmallIntegerField(choices=TransactionStatus.choices, blank=True, null=True)
    