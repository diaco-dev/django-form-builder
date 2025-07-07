from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from django import forms

class CustomUserCreationForm(UserCreationForm):
    password = forms.CharField(label="password", widget=forms.PasswordInput)
    re_password = forms.CharField(label="re_password", widget=forms.PasswordInput)
    class Meta:
        model = CustomUser
        fields = ('mobile', 'email', 'role')


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('mobile', 'email', 'role', 'is_active', 'is_verified')
