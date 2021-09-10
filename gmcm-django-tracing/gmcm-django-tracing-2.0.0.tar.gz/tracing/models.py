""" Audit models. """

# Django
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth import get_user_model
from django.db import models

# Models
User = get_user_model()


class BaseModel(models.Model):
    """Audit base model which every models inherit."""

    created_date = models.DateTimeField(
        auto_now_add=True, verbose_name="fecha de creación"
    )
    created_user = models.CharField(
        max_length=128, editable=False, null=True, verbose_name="creado por"
    )
    modified_date = models.DateTimeField(
        auto_now=True, verbose_name="última fecha de modificación"
    )
    modified_user = models.CharField(
        max_length=128, editable=False, null=True, verbose_name="modificado por"
    )
    is_active = models.BooleanField(default=True, verbose_name="activo")

    def _get_user(self, username):
        """Get user by provide username"""
        try:
            user = User.objects.get(username=username)
            return user
        except User.DoesNotExist:
            return username

    @property
    def creation_user(self):
        """Get created user"""
        return self._get_user(self.created_user)

    @property
    def modification_user(self):
        """Get updated user"""
        return self._get_user(self.modified_user)

    class Meta:
        """Meta options."""

        abstract = True


class Trace(models.Model):
    """Model that stores audit logs according to the rules."""

    class ActionChoices(models.IntegerChoices):
        CREATE = 1, "Crear"
        EDIT = 2, "Editar"
        DELETE = 3, "Eliminar"

    id = models.BigAutoField(primary_key=True)
    name = models.TextField(verbose_name="nombre")
    action = models.PositiveSmallIntegerField(
        choices=ActionChoices.choices, verbose_name="acción"
    )
    message = models.TextField(verbose_name="detalle")
    ip = models.CharField(max_length=32, null=True, verbose_name="dirección IP")
    os = models.CharField(max_length=256, null=True, verbose_name="sistema operativo")
    content_type = models.ForeignKey(
        "contenttypes.ContentType", on_delete=models.CASCADE, verbose_name="contenido"
    )
    object_id = models.PositiveIntegerField(verbose_name="id del objecto")
    content_object = GenericForeignKey("content_type", "object_id")
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="usuario")
    date = models.DateTimeField(auto_now_add=True, verbose_name="fecha")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Rastro"


class Rule(BaseModel):
    """Modelo que almacena las reglas de auditoría."""

    content_type = models.OneToOneField(
        "contenttypes.ContentType", on_delete=models.CASCADE, verbose_name="Objeto"
    )
    check_create = models.BooleanField("rastrear creaciones")
    check_edit = models.BooleanField("rastrear modificaciones")
    check_delete = models.BooleanField("rastrear eliminaciones")

    def __str__(self):
        return f"Regla de {str(self.content_type).lower()}"

    class Meta:
        ordering = ("content_type",)
        verbose_name = "Regla"
