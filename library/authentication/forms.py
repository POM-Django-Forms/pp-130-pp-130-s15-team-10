from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser


class BaseUserForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('first_name'):
            raise forms.ValidationError("First name is required.")
        if not cleaned_data.get('last_name'):
            raise forms.ValidationError("Last name is required.")
        return cleaned_data


class CustomUserCreationForm(BaseUserForm, UserCreationForm):
    class Meta:
        model = CustomUser
        fields = (
            "email", "first_name", "middle_name", "last_name", "role",
            "password1", "password2", "is_staff", "is_active", "groups", "user_permissions"
        )


class CustomUserChangeForm(BaseUserForm, UserChangeForm):
    class Meta:
        model = CustomUser
        fields = (
            "email", "first_name", "middle_name", "last_name", "role",
            "is_staff", "is_active", "groups", "user_permissions"
        )
