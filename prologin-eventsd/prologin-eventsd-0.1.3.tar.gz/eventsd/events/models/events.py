from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.validators import ValidationError
from django.conf import settings
from django.core.files.storage import default_storage
from pathlib import Path
from django.utils import timezone
from .signup import SelectionStatus


class Center(models.Model):
    name = models.CharField(verbose_name=_("Nom"), max_length=120)
    address = models.TextField(verbose_name=_("Adresse"), max_length=1000)
    lng = models.DecimalField(
        verbose_name=_("Longitude"),
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )
    lat = models.DecimalField(
        verbose_name=_("Latitude"),
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )
    private_notes = models.TextField(
        verbose_name=("Notes privées"), max_length=2000, blank=True, null=True
    )

    class Meta:
        verbose_name = _("centre")
        verbose_name_plural = _("centres")

    def __str__(self):
        return self.name


class EventManager(models.Manager):
    def get_open_events(self):
        return self.filter(
            signup_start_date__lte=timezone.now(),
            signup_end_date__gt=timezone.now(),
        )

    def get_visible_events(self):
        return self.filter(
            signup_start_date__lte=timezone.now(),
        )


class Event(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name=_("Nom de l'évènement"),
    )

    center = models.ForeignKey(
        to="eventsd_events.Center",
        verbose_name=_("Centre"),
        on_delete=models.CASCADE,
    )

    signup_start_date = models.DateTimeField(
        verbose_name=_("Date de début d'inscription")
    )
    signup_end_date = models.DateTimeField(
        verbose_name=_("Date de fin d'inscription")
    )

    start_date = models.DateTimeField(verbose_name=_("Date de début"))
    end_date = models.DateTimeField(verbose_name=_("Date de fin"))

    form = models.ForeignKey(
        to="eventsd_events.Form",
        verbose_name=_("Formulaire"),
        on_delete=models.SET_DEFAULT,
        default=1,
    )

    documents = models.ManyToManyField(
        to="eventsd_events.Document",
        related_name="events",
        verbose_name=_("Documents"),
        through="eventsd_events.EventDocument",
        blank=True,
    )

    notes = models.TextField(
        verbose_name=_("Notes"),
        help_text=_(
            "Ce texte, si défini est affiché "
            "lors de l'inscription à l'évènement "
            "(il peut éventuellement contenir des liens)"
        ),
        blank=True,
        null=True,
    )

    description = models.TextField(
        verbose_name=_("Description de l'évènement"),
        help_text=_(
            "Si ce champ n'est pas spécifié, "
            "la description du projet sera utilisée."
        ),
    )

    objects = EventManager()

    class Meta:
        verbose_name = _("évènement")
        verbose_name_plural = _("évènements")

    def clean(self):
        errors = {}

        if self.signup_start_date > self.signup_end_date:
            errors["signup_start_date"] = _(
                "La date début d'inscription doit être avant la date de "
                "fin d'inscription."
            )

        if self.signup_end_date > self.start_date:
            errors["signup_end_date"] = _(
                "La date de fin d'inscription doit être avant "
                "la date de début d'évènement."
            )

        if self.start_date > self.end_date:
            errors["end_date"] = _(
                "La date de fin d'évènement doit être après "
                "la date de début d'évènement."
            )

        if errors:
            raise ValidationError(errors)

        return self.form.questions.all()

    def __str__(self):
        return self.name

    def get_my_documents(self, attendee):
        if attendee.status == SelectionStatus.CONFIRMED.value:
            return self.documents.all()
        if attendee.status == SelectionStatus.ACCEPTED.value:
            return self.documents.filter(
                eventdocument__visibility__in=(
                    DocumentType.ACCEPTED_OR_CONFIRMED.value,
                    DocumentType.PUBLIC,
                )
            )
        else:
            return self.documents.filter(
                eventdocument__visibility=DocumentType.PUBLIC.value
            )


class DocumentType(models.IntegerChoices):
    PUBLIC = 1, _("Public")
    ACCEPTED_OR_CONFIRMED = 2, _("Accepté ou confirmé")
    CONFIRMED = 3, _("Confirmé seulement")


class EventDocument(models.Model):
    document = models.ForeignKey(
        to="eventsd_events.Document",
        verbose_name=_("Document"),
        on_delete=models.CASCADE,
    )

    event = models.ForeignKey(
        to="eventsd_events.Event",
        verbose_name=_("Évènement"),
        on_delete=models.CASCADE,
    )

    display_name = models.CharField(
        max_length=260,
        verbose_name=_("Nom public du document"),
        help_text=_(
            "Le nom public du document qui sera affiché aux participants"
        ),
    )

    visibility = models.IntegerField(
        verbose_name=_("Visibilité"),
        choices=DocumentType.choices,
    )

    class Meta:
        verbose_name = _("document lié à l'évènement")
        verbose_name_plural = _("documents lié à l'évènement")

    def __str__(self):
        return self.display_name


class Document(models.Model):
    admin_name = models.CharField(
        max_length=260,
        unique=True,
        verbose_name=_("Nom du document"),
        help_text=_("Ce nom est uniquement utilisé pour l'admin django"),
    )

    file = models.FileField(
        verbose_name=_("Fichier"),
        storage=getattr(settings, "EVENTSD_STORAGE_BACKEND", default_storage),
        upload_to=Path("eventsd") / "documents",
    )

    class Meta:
        verbose_name = _("document")
        verbose_name_plural = _("documents")

    def __str__(self):
        return self.admin_name
