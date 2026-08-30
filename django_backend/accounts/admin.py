from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("email", "username", "role", "phone", "is_staff", "created_at")
    list_filter = ("role", "is_staff", "is_active")
    fieldsets = UserAdmin.fieldsets + (("Railway profile", {"fields": ("role", "phone", "address", "avatar_url", "frequent_journeys")}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Railway profile", {"fields": ("email", "role", "phone", "avatar_url")}),)
