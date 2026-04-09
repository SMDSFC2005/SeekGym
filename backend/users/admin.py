from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario

    list_display = (
        "id",
        "username",
        "email",
        "rol",
        "estado_gym",
        "is_staff",
        "is_superuser",
    )

    list_filter = (
        "rol",
        "estado_gym",
        "is_staff",
        "is_superuser",
        "is_active",
    )

    fieldsets = UserAdmin.fieldsets + (
        ("Rol y estado gym", {
            "fields": ("rol", "estado_gym", "creado_en"),
        }),
    )

    readonly_fields = ("creado_en",)