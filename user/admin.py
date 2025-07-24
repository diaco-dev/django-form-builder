from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from django.contrib.auth import get_user_model

from core.forms import CustomUserCreationForm, CustomUserChangeForm
from core.models import CustomUser

User = get_user_model()

class UserResource(resources.ModelResource):
    # mobile = fields.Field(attribute='mobile', column_name='mobile')

    class Meta:
        model = User
    #     fields = ('mobile',)
    #     import_id_fields = ['mobile']
    #
    # def before_import_row(self, row, **kwargs):
    #     mobile = row.get('mobile')
    #     if mobile and User.objects.filter(mobile=mobile).exists():
    #         User.objects.filter(mobile=mobile).update(is_active=True)
    #

@admin.register(CustomUser)
class CustomUserAdmin(ImportExportModelAdmin, BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    model = CustomUser
    resource_class = UserResource

    # Define fields to display in the admin list view
    list_display = ('full_name', 'mobile', 'role', 'is_active', 'is_verified', 'created_at')
    list_editable = ('is_active', 'mobile', 'role')
    search_fields = ('email', 'first_name', 'last_name','mobile')
    list_filter = ('role', 'is_active', 'is_verified', '_created_at')
    ordering = ('-_created_at',)

    # Override fieldsets to remove username and include CustomUser fields
    fieldsets = (
        (None, {'fields': ('mobile', 'email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_verified', 'is_staff', 'is_superuser',
                                    # 'groups', 'user_permissions'
                                    )}),
        ('Important Dates', {'fields': ('_created_at',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('mobile', 'email', 'password1', 'password2', 'first_name', 'last_name', 'role', 'is_active', 'is_verified'),
        }),
    )
