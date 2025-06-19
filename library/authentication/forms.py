import re
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import authenticate
from .models import ROLE_CHOICES, CustomUser
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.forms import PasswordResetForm

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


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=255, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your email'
    }))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your password'
    }))

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        user = authenticate(username=email, password=password)
        if not user:
            raise forms.ValidationError('Invalid email or password')
        if not user.is_active:
            raise forms.ValidationError('Account disabled')

        cleaned_data['user'] = user
        return cleaned_data


class RegisterForm(forms.Form):
    login = forms.EmailField(label="Email", max_length=255, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter email'
    }))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter password'
    }))
    confirm_password = forms.CharField(label="Confirm Password", widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Repeat password'
    }))
    firstname = forms.CharField(label="First Name", max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'enter your first name'
    }))
    middle_name = forms.CharField(label="Middle Name", max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'enter your middle name'
    }))
    lastname = forms.CharField(label="Last Name", max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'enter your last name'
    }))
    role = forms.ChoiceField(label='Role', choices=ROLE_CHOICES)
    role.widget.attrs.update({'class': 'form-select'})

    def clean_login(self):
        email = self.cleaned_data.get('login')
        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError("Enter a valid email address.")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean_password(self):
        pwd = self.cleaned_data.get('password')
        if len(pwd) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        if not re.search(r"\d", pwd):
            raise forms.ValidationError("Password must contain at least one digit.")
        if not re.search(r"[A-Z]", pwd):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', pwd):
            raise forms.ValidationError("Password must contain at least one special character.")
        return pwd

    def clean(self):
        cleaned_data = super().clean()
        pwd1 = cleaned_data.get('password')
        pwd2 = cleaned_data.get('confirm_password')
        if pwd1 and pwd2 and pwd1 != pwd2:
            raise forms.ValidationError("Passwords do not match.")

        password_pattern = re.compile(r'^([A-Za-z]{2,}|[A-Za-z]\.)$')
        for field_name, label in [
            ('firstname', 'First Name'),
            ('middle_name', 'Middle Name'),
            ('lastname', 'Last Name'),
        ]:
            val = cleaned_data.get(field_name)
            if not val:
                raise forms.ValidationError(f"{label} is required.")
            elif not password_pattern.match(val):
                raise forms.ValidationError(
                    f"{label} must be at least 2 letters, "
                    "or a single letter followed by a dot (e.g. 'A.')."
                )

        return cleaned_data

class StyledPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'you@example.com'
        })

