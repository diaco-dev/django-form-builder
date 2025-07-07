from django.db import models
from django.contrib.auth.models import User
from core.models import GenericModel
from core.type import QuestionType, FormType
from django.contrib.auth import get_user_model

User = get_user_model()

#------------------------------------------------------------------------------------------------------------#
class Form(GenericModel):
    title = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    type = models.CharField(
        max_length=255,
        choices=FormType.choices,
        null=True,
        blank=True
    )
    is_active = models.BooleanField(
        default=True
    )
    class Meta:
        verbose_name_plural = "forms"
        verbose_name = "form"
        db_table = 'form'
        indexes = (
            models.Index(fields=['title'], name='form_title_idx'),

        )

    def __str__(self):
        return self.title


#------------------------------------------------------------------------------------------------------------#
class Question(GenericModel):
    form = models.ForeignKey(
        Form,
        related_name='questions',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    text = models.TextField(
        null=True,
        blank=True
    )
    placeholder = models.TextField(
        null=True,
        blank=True
    )
    description = models.TextField(
        null=True,
        blank=True
    )
    question_type = models.CharField(
        max_length=50,
        choices=QuestionType.choices,
        null=True,
        blank=True
    )
    category = models.CharField(
        max_length=400,
        null=True,
        blank=True
    )
    name = models.CharField(
        max_length=400,
        null=True,
        blank=True
    )
    is_required = models.BooleanField(
        default=False,
        null=True,
        blank=True
    )
    order = models.PositiveIntegerField(
        default=0
    )
    max = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    min = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    class Meta:
        verbose_name_plural = "questions"
        verbose_name = "question"
        db_table = 'question'
        ordering = ('order', 'category')

    def __str__(self):
        return self.text

#------------------------------------------------------------------------------------------------------------#
class Option(GenericModel):
    question = models.ForeignKey(
        Question,
        related_name='options',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    text = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name_plural = "options"
        verbose_name = "option"
        db_table = 'option'


    def __str__(self):
        return self.text

#------------------------------------------------------------------------------------------------------------#
class Response(GenericModel):
    form = models.ForeignKey(
        Form,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    day = models.ForeignKey(
        to='course.Day',
        on_delete=models.CASCADE,
        related_name='responses'
        , null=True,
        blank=True)
    class Meta:
        verbose_name_plural = "responses"
        verbose_name = "response"
        db_table = 'response'

    def __str__(self):
        return self.form.title


#------------------------------------------------------------------------------------------------------------#
class Answer(GenericModel):
    response = models.ForeignKey(
        Response,
        related_name='answers',
        on_delete=models.CASCADE
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers_question',
        null=True,
        blank=True
    )
    value = models.TextField(
        null=True,
        blank=True
    )
    option = models.ForeignKey(
        Option,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name_plural = "answers"
        verbose_name = "answer"
        db_table = 'answers'
        indexes = (
            models.Index(fields=['value'], name='answer_value_idx'),

        )

    def __str__(self):
        return self.value or self.option.text


#------------------------------------------------------------------------------------------------------------#
class Guest(GenericModel):

    first_name = models.CharField(
        verbose_name=("first_name"),
        max_length=150,
        null=True,
        blank=True
    )
    last_name = models.CharField(
        verbose_name=("last_name"),
        max_length=150,
        null=True,
        blank=True
    )
    mobile = models.CharField(
        verbose_name=("last_name"),
        max_length=15,
        null=True,
        blank=True
    )
    support_name = models.CharField(
        verbose_name=("support_name"),
        max_length=150,
        null=True,
        blank=True
    )
    class Meta:
        verbose_name_plural = "guest"
        verbose_name = "gust"
        db_table = 'gust'


    def __str__(self):
        return f"{self.first_name} - {self.last_name}"


class Attendance(GenericModel):
    day = models.ForeignKey(
        to='course.Day',
        on_delete=models.CASCADE,
        related_name='day_attendance',
        null=True,
        blank=True
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'user'},
        null=True,
        blank=True
    )
    form = models.ForeignKey(
        Form,
        on_delete=models.CASCADE,
        limit_choices_to={'type': 'DAILY_CHECK'},
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=10,
        choices=[('present', 'Present'),
                 ('absent', 'Absent')],
        null=True,
        blank=True
    )
    guest = models.ForeignKey(
        Guest,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    class Meta:
        verbose_name_plural = "attendance"
        verbose_name = "attendance"
        db_table = 'attendance'


    def __str__(self):
        return f"{self.student} - {self.status}"