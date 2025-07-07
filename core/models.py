from uuid import uuid4
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django_currentuser.db.models import CurrentUserField
from utils.format import common_datetime_str
from django.contrib.auth.base_user import BaseUserManager
from utils.format import upload_to_by_date
from auditlog.registry import auditlog
from django.db.models.base import ModelBase



#-----------------------meta class ----------------------------
class AuditLogModelBase(ModelBase):
    def __new__(cls, name, bases, attrs, **kwargs):
        new_class = super().__new__(cls, name, bases, attrs, **kwargs)

        if not new_class._meta.abstract:
            auditlog.register(new_class)

        return new_class
#---------------------------------------------------
class GenericModel(models.Model, metaclass=AuditLogModelBase):
    id = models.UUIDField(
        verbose_name=_("unique id"),
        primary_key=True,
        unique=True,
        null=False,
        default=uuid4,
        editable=False
    )
    _created_by = CurrentUserField(
        related_name="%(app_label)s_%(class)s_created_by",
        verbose_name=_("created by"),
    )
    _updated_by = CurrentUserField(
        related_name="%(app_label)s_%(class)s_updated_by",
        verbose_name=_("updated by"),
        on_update=True
    )
    _created_at = models.DateTimeField(
        verbose_name=_('created at'),
        default=timezone.now
    )
    _updated_at = models.DateTimeField(
        verbose_name=_('updated at'),
        auto_now=True
    )

    class Meta:
        abstract = True
        indexes = (
            models.Index(fields=['id'], name='%(class)s_id_idx'),
        )
    @property
    def created_by(self):
        if self._created_by:
            return f"{self._created_by.first_name} {self._created_by.last_name}".strip() or self._created_by.email
        return None

    @property
    def updated_by(self):
        if self._updated_by:
            return f"{self._updated_by.first_name} {self._updated_by.last_name}".strip() or self._updated_by.email
        return None

    @property
    def created_at(self):
        return common_datetime_str(self._created_at)

    @property
    def updated_at(self):
        return common_datetime_str(self._updated_at)

    @cached_property
    def can_delete(self):
        for field in self._meta.related_objects:
            try:
                if getattr(self, field.related_name).all().exists():
                    return False
            except Exception as e:
                pass
        return True


    class Meta:
        abstract = True

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MODEL: User
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class CustomUserManager(BaseUserManager):
    def create_superuser(self, mobile=None,password=None):
        if not mobile:
            raise ValueError('Superuser must have a mobile.')
        if not password:
            raise ValueError('Superuser must have a password.')

        user = self.create_user(
            mobile=mobile,
            password=password)
        user.is_admin = True
        user.is_staff = True
        user.is_verified = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def create_user(self, mobile=None, password=None,**extra_fields):
        if not mobile :
            raise ValueError('User must have a mobile.')
        if not password:
            raise ValueError('User must have a password.')

        user = self.model(
            mobile=mobile,
            **extra_fields
        )
        user.set_password(password)
        user.is_admin = False
        user.is_staff = False
        user.is_superuser = False
        user.save(using=self._db)
        return user

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('superuser', 'Superuser'),
        ('operator', 'Operator'),
        ('user', 'User'),
    ]
    GENDER = [
        ('man', 'Man'),
        ('woman', 'Woman'),
    ]
    username = None

    id = models.UUIDField(
        "unique id",
        primary_key=True,
        unique=True,
        null=False,
        default=uuid4,
        editable=False
    )
    role = models.CharField(
        max_length=13,
        choices=ROLE_CHOICES,
        default='user'
    )
    first_name = models.CharField(
        verbose_name=("first name"),
        max_length=150
    )
    last_name = models.CharField(
        verbose_name=("last name"),
        max_length=150
    )
    is_verified = models.BooleanField(
        default=False
    )
    gender = models.CharField(
        max_length=5,
        choices=GENDER,
        blank=True,
        null=True
    )
    email = models.EmailField(
        blank=True,
        null=True,
    )
    mobile = models.CharField(
        max_length=11,
        unique=True,
        null=True,
        blank=True
    )
    avatar = models.ImageField(
        verbose_name='image avatar',
        upload_to=upload_to_by_date,
        null=True,
        blank=True
    )
    _created_at = models.DateTimeField(
        verbose_name=('created at'),
        default=timezone.now
    )
    objects = CustomUserManager()

    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = ("user")
        verbose_name_plural = ("users")
        db_table = 'core_user'
        indexes = (
            models.Index(fields=['id'], name='user_id_idx'),
            models.Index(fields=['mobile'], name='user_mobile_idx'),
        )

    @property
    def full_name(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.email

    def __str__(self):
        return self.full_name or self.mobile or "Unsuccessful register"


    @property
    def created_at(self):
        return common_datetime_str(self._created_at)
