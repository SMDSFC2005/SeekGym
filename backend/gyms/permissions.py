from rest_framework.permissions import BasePermission


class IsGymApprovedOrSuperuser(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        return (
            getattr(user, "rol", None) == "GIMNASIO"
            and getattr(user, "estado_gym", None) == "APROBADO"
        )


class CanManageGym(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        return (
            getattr(user, "rol", None) == "GIMNASIO"
            and getattr(user, "estado_gym", None) == "APROBADO"
            and obj.owner_id == user.id
        )