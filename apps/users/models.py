from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from usaid.models import AbstractModel
from django.conf import settings
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth.hashers import make_password

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, is_admin=False, is_staff=False, is_active=True):
        if not email:
            raise ValueError("User must have an email")
        user = self.model(
            email=self.normalize_email(email.lower())
        )
        if password is not None:
            user.set_password(password)

        user.is_superuser = is_admin
        user.is_staff = is_staff
        user.is_active = is_active
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("User must have an email")
        if not password:
            raise ValueError("User must have a password")
        user = self.model(
            email=self.normalize_email(email.lower()),
        )
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save(using=self._db)
        return user


class User(AbstractModel, AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=255, blank=False, null=True)
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True, db_index=True)
    organization_id = models.CharField(max_length=255, blank=True, verbose_name='organization id', null=True)

    client_id = models.CharField(max_length=255, blank=True, null=True)
    client_secret = models.CharField(max_length=255, blank=True, null=True)

    code_fasyankes = models.CharField(max_length=255, blank=True, null=True)
    province = models.ForeignKey('Province', on_delete=models.CASCADE, blank=True, null=True)
    district = models.ForeignKey('District', on_delete=models.CASCADE, blank=True, null=True)
    sitb_rs_id = models.CharField(max_length=255, blank=True, null=True)
    sitb_rs_pass = models.CharField(max_length=255, blank=True, null=True)
    is_satusehat = models.BooleanField(default=True, verbose_name='Active')

    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin site.'), )
    is_active = models.BooleanField(_('active'), default=True, help_text=_(
        'Designates whether this user should be treated as active. ''Unselect this instead of deleting accounts.'), )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def get_username(self):
        return self.email

    def __str__(self):
        return str(self.email)
        
class Province(AbstractModel):
    id = models.IntegerField(primary_key=True)
    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    dagri_code = models.CharField(max_length=255)
    def __str__(self):
        return str(self.name)
    
class District(AbstractModel):
    id = models.IntegerField(primary_key=True)
    province = models.ForeignKey(Province, on_delete=models.CASCADE)
    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    dagri_code = models.CharField(max_length=255)
    def __str__(self):
        return str(self.name)