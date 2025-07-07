from django.contrib import admin
from .models import Form, Question, Option, Attendance, Answer, Response, Guest
from import_export.admin import ImportExportModelAdmin
from import_export import resources

class OptionResource(resources.ModelResource):
    class Meta:
        model = Option

@admin.register(Option)
class OptionResourceAdmin(ImportExportModelAdmin):
    resource_class = OptionResource


class OptionInline(admin.TabularInline):
    model = Option
    extra = 2
    min_num = 0
    max_num = 10

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ['text', 'question_type', 'is_required', 'order','category']
    show_change_link = True

@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', '_created_at','_created_by']
    list_filter = ['is_active', '_created_at']
    search_fields = ['title']
    inlines = [QuestionInline]


class AttendanceResource(resources.ModelResource):
    class Meta:
        model = Attendance


@admin.register(Attendance)
class AttendanceResourceAdmin(ImportExportModelAdmin):
    resource_class = AttendanceResource
    # list_display = ['student__first_name', 'student__last_name', 'status', ]
    search_fields = ['student__first_name', 'student__last_name']

class AnswerResource(resources.ModelResource):
    class Meta:
        model = Answer

@admin.register(Answer)
class AnswerResourceAdmin(ImportExportModelAdmin):
    resource_class = AnswerResource



class QuestionResource(resources.ModelResource):
    class Meta:
        model = Question

@admin.register(Question)
class QuestionResourceAdmin(ImportExportModelAdmin):
    resource_class = QuestionResource
    list_display = ['form__title', 'text','category', 'name','_created_by','form','is_required','order']
    list_editable = ('form','is_required','category','name','order')
    search_fields = ['text','category']
    # ordering = ('category','order')

class ResponseResource(resources.ModelResource):
    class Meta:
        model = Response

@admin.register(Response)
class ResponseResourceAdmin(ImportExportModelAdmin):
    resource_class = ResponseResource
    list_display = ['form__title', 'user__first_name','user__last_name','_created_by','_created_at']
    ordering = ('-_created_at',)
    search_fields = ['form__title','user__first_name','user__last_name']
    list_filter = ['form__title',]

class GuestResource(resources.ModelResource):
    class Meta:
        model = Guest

@admin.register(Guest)
class GuestResourceAdmin(ImportExportModelAdmin):
    resource_class = GuestResource
