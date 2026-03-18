from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Información extra", {"fields": ("rol", "creado_en")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Información extra", {"fields": ("rol",)}),
    )
    readonly_fields = ("creado_en",)
    list_display = ("username", "email", "rol", "is_staff", "is_active")