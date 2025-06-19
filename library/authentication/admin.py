from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ("email", "first_name", "last_name", "role", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active", "role")
    fieldsets = (
        (None, {"fields": ("email",)}),
        ("Personal Info", {"fields": ("first_name", "middle_name", "last_name", "role")}),
        ("Permissions", {"fields": (("is_staff", "is_active"), "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "first_name", "middle_name", "last_name", "role",
                "password1", "password2", ("is_staff", "is_active"), "groups", "user_permissions"
            ),
        }),
    )
    search_fields = ("email", "last_name")
    ordering = ("email", "last_name")

    def response_add(self, request, obj, post_url_continue=None):
        """Redirect to the user list after adding, except if 'Add another' pressed."""
        if "_addanother" in request.POST:
            return super().response_add(request, obj, post_url_continue)
        return HttpResponseRedirect(reverse("admin:authentication_customuser_changelist"))
