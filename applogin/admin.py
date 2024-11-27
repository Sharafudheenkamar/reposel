from django.contrib import admin
from .models import (
    Userprofile,
    Token,
    Journals,
)
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = Userprofile
        fields = ("username",)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = Userprofile
        exclude = []


class CustomUserAdmin(UserAdmin):

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "email",
                    "first_name",
                    "name",
                    "stream",
                    "year",
                    "phone_number",
                    "profile_image",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "user_type",
                    "is_active",
                    "is_superuser",
                    "status"
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {"classes": ("wide",), "fields": ("username", "password1", "password2")},
        ),
    )
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    list_display = ("pk","username", "first_name", "user_type")
    search_fields = ("username", "first_name")
    ordering = ("username",)


admin.site.register(Userprofile, CustomUserAdmin)
admin.site.register(Token)
admin.site.register(Journals)