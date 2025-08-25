from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from contact.models import Contact, ContactCorrespondent
from core.models import GenericModel
from core.types import EmailHistoryType

User = get_user_model()


