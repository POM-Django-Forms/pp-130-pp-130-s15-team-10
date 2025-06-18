from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser


def validate_names(cleaned_data):
    if not cleaned_data.get('first_name'):
        raise forms.ValidationError("First name is required.")
    if not cleaned_data.get('last_name'):
        raise forms.ValidationError("Last name is required.")


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = (
            "email", "first_name", "middle_name", "last_name", "role",
            "password1", "password2", "is_staff", "is_active", "groups", "user_permissions"
        )

    def clean(self):
        cleaned_data = super().clean()
        validate_names(cleaned_data)
        return cleaned_data


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = (
            "email", "first_name", "middle_name", "last_name", "role",
            "is_staff", "is_active", "groups", "user_permissions"
        )

    def clean(self):
        cleaned_data = super().clean()
        validate_names(cleaned_data)
        return cleaned_data
