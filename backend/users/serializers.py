from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    rol = serializers.ChoiceField(
        choices=[User.Rol.NORMAL, User.Rol.GIMNASIO],
        required=False,
        default=User.Rol.NORMAL,
    )

    class Meta:
        model = User
        fields = ("username", "password", "email", "rol")
        extra_kwargs = {
            "email": {"required": False, "allow_blank": True},
        }

    def create(self, validated_data):
        requested_rol = validated_data.pop("rol", User.Rol.NORMAL)

        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            email=validated_data.get("email", ""),
        )

        if requested_rol == User.Rol.GIMNASIO:
            user.rol = User.Rol.NORMAL
            user.estado_gym = User.EstadoGym.PENDIENTE
        else:
            user.rol = User.Rol.NORMAL
            user.estado_gym = User.EstadoGym.NONE

        user.save()
        return user