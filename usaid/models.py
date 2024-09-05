from django.db import models
from crum import get_current_user


class AbstractModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey('users.User', on_delete=models.DO_NOTHING, related_name='%(class)s_creator',
                                   null=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    updated_by = models.ForeignKey('users.User', on_delete=models.DO_NOTHING, related_name='%(class)s_updater',
                                   null=True, editable=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user:
            if user and not user.pk:
                user = None
            if not self.pk:
                self.created_by = user
            self.updated_by = user
        super(AbstractModel, self).save(*args, **kwargs)
