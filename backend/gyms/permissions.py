from rest_framework.permissions import BasePermission


# solo pueden pasar usuarios con el gym aprobado por el admin, o superusers
class IsGymApprovedOrSuperuser(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        # tiene que tener rol GIMNASIO y estado APROBADO, las dos cosas
        return (
            getattr(user, "rol", None) == "GIMNASIO"
            and getattr(user, "estado_gym", None) == "APROBADO"
        )


# comprueba que el usuario es el dueño del gym que quiere tocar
class CanManageGym(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        # solo el dueño del gym puede modificarlo
        return (
            getattr(user, "rol", None) == "GIMNASIO"
            and getattr(user, "estado_gym", None) == "APROBADO"
            and obj.owner_id == user.id
        )