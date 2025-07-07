from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.TextChoices):
    OTH = 'OTH', _("سایر")
    Finance = 'M', _("مالی")
    CRM = 'C', _("CRM")
    Club = 'CU', _("باشگاه مشتریان")
    INConnect = 'IN', _("ارتباط داخلی")
    BulkSMS = 'SMS', _("ارسال پیامک انبوه")
    HRM = 'HR', _("مدریت منابع انسانی")
    OUTConnect = 'OUT', _("ارتباط خارجی")
    TaskManagement = 'TS', _("مدریت تسک ها")
    Information = 'INFO', _("جمع‌آوری اطلاعات")
    ProcessManager = 'FR', _("مدیریت فرآیندها")
    ExitEnter = 'INO', _("ورود و خروج")


#------ Model ticket -----#

class TicketCategory(models.TextChoices):
    TECHNICAL = "T", "Technical"
    ORDER = "O", "Order"
    QUESTION = "Q", "Question"
    OTHERS = "OT", "Others"


class TicketType(models.TextChoices):
    USER = "U", "User"
    SYSTEM = "S", "System"
    ADMIN = "A", "Admin"


class TicketStatus(models.TextChoices):
    OPEN = "O", "Open"
    Close = "C", "Close"

class StatusWork(models.TextChoices):
    OPEN = "O", "Open"
    DONE = "D", "Done"
    IN_PROGRESS = "P", "InProgress"
    MISSED = "M", "Missed"


class QuestionType(models.TextChoices):
    TEXT = 'TEXT', 'Text'
    MULTIPLE_CHOICE = 'MULTIPLE_CHOICE', 'Multiple Choice'
    CHECKBOX = 'CHECKBOX', 'Checkbox'
    NUMBER = 'NUMBER', 'Number'
    TEXTAREA = 'TEXTAREA', 'TextAres'
    RANGE = 'RANGE', 'Range'
    DESCRIPTION = 'DESCRIPTION', 'Description'
    BOOL = 'BOOL', 'Boolean'
    RADIO = 'RADIO', 'Radio'

class TaskStatus(models.TextChoices):
    PENDING = 'P', 'pending'
    IN_PROGRES = 'IP', 'In Progress'
    COMPLETED = 'C', 'Completed'

class ActionType(models.TextChoices):
    TEXT = 'TEXT', 'Text',
    FILE= 'FILE', 'File',
    QUIZ= 'QUIZ', 'Quiz',
    FORM=   'FORM', 'Form',
    ROUTE= 'ROUTE', 'Route'

class TargetRole(models.TextChoices):
    STUDENT = 'STUDENT', 'Student'
    BUSINESS_COACH = 'BUSINESS_COACH', 'Business Coach'
    ALL = 'ALL', 'All'


class FormType(models.TextChoices):
    FORM = 'FORM', 'Form'
    CHECKLIST = 'CHECKLIST', 'Checklist'
    DAILY_CHECK= 'DAILY_CHECK', 'Daily Check'


class VideoType(models.TextChoices):
    SOFTWARE = 'SOFTWARE', 'Software'
    SOURCE = 'SOURCE', 'Source'
    GENERAL = 'GENERAL', 'General'