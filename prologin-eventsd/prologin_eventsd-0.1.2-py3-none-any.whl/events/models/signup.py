from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.validators import ValidationError
from django import forms


class SelectionStatus(models.IntegerChoices):
    ABANDONED = -1, _("Abandonné")
    ENROLLED = 0, _("Inscrit")
    NOT_SELECTED = 1, _("Non sélectionné")
    ACCEPTED = 2, _("Accepté")
    CONFIRMED = 3, _("Confirmé")


class Attendee(models.Model):
    owner = models.ForeignKey(
        to=get_user_model(),
        verbose_name=_("Utilisateur"),
        on_delete=models.CASCADE,
    )

    first_name = models.CharField(
        max_length=256,
        verbose_name=_("Prénom"),
    )

    last_name = models.CharField(
        max_length=256,
        verbose_name=_("Nom"),
    )

    dob = models.DateField(
        verbose_name=_("Date de naissance"),
    )

    event = models.ForeignKey(
        to="eventsd_events.Event",
        verbose_name=_("Évènement"),
        on_delete=models.CASCADE,
    )

    status = models.SmallIntegerField(
        choices=SelectionStatus.choices,
        verbose_name=_("Statut de la candidature"),
    )

    labels = models.ManyToManyField(
        to="eventsd_events.AttendeeLabel",
        blank=True,
        verbose_name=_("Labels"),
    )

    class Meta:
        verbose_name = _("participant")
        verbose_name_plural = _("participants")

    def __str__(self):
        return f"{self.first_name} {self.last_name}@{self.event}"


class Form(models.Model):
    name = models.CharField(verbose_name=_("Nom"), max_length=120)

    class Meta:
        verbose_name = _("formulaire")
        verbose_name_plural = _("formulaires")

    def __str__(self):
        return self.name

    def get_form_fields(self):
        return {
            f[0]: f[1]
            for f in [q.get_field_tuple() for q in self.questions.all()]
        }


class QuestionType(models.TextChoices):
    TITLE = "TITLE", _("Titre")
    TEXT = "TEXT", _("Texte")
    LONG_TEXT = "LONG_TEXT", _("Texte long")
    CHOICE = "CHOICE", _("Choix")
    MULTIPLE_CHOICES = "MULTIPLE_CHOICES", _("Choix multiple")


class Question(models.Model):
    form = models.ForeignKey(
        to="eventsd_events.Form",
        related_name="questions",
        on_delete=models.CASCADE,
        verbose_name=_("Formulaire"),
    )
    text = models.CharField(
        verbose_name=_("Texte de la question"), max_length=1000
    )
    type = models.CharField(
        verbose_name=_("Type"),
        choices=QuestionType.choices,
        max_length=32,
    )
    mandatory = models.BooleanField(verbose_name=_("Obligatoire"))
    answers = models.TextField(
        verbose_name=_("Réponses possibles"),
        blank=True,
        null=True,
        max_length=500,
        help_text=_("Une réponse par ligne"),
    )
    order = models.PositiveSmallIntegerField(verbose_name=_("Ordre"))

    class Meta:
        verbose_name = _("question")
        verbose_name_plural = _("questions")
        ordering = ("order",)

    def clean(self):
        if (
            self.type
            in (
                QuestionType.CHOICE.value,
                QuestionType.MULTIPLE_CHOICES.value,
            )
            and (self.answers is None or self.answers == "")
        ):
            raise ValidationError(
                _(
                    "Pour une question de ce type, "
                    "vous devez préciser les choix possibles"
                )
            )

    def get_form_field_kwargs(self):
        return {
            "label": str(self),
            "label_suffix": None,
            "required": self.mandatory,
        }

    def get_form_field(self):
        if self.type == QuestionType.TEXT.value:
            return forms.fields.CharField(
                max_length=400, **self.get_form_field_kwargs()
            )

        if self.type == QuestionType.LONG_TEXT.value:
            return forms.fields.CharField(
                max_length=1_000,
                widget=forms.widgets.Textarea(),
                **self.get_form_field_kwargs(),
            )

        if self.type == QuestionType.CHOICE.value:
            return forms.fields.ChoiceField(
                choices=self.get_field_choices(),
                widget=forms.widgets.RadioSelect(),
                **self.get_form_field_kwargs(),
            )

        if self.type == QuestionType.MULTIPLE_CHOICES.value:
            return forms.fields.MultipleChoiceField(
                choices=self.get_field_choices(),
                widget=forms.widgets.CheckboxSelectMultiple(),
                **self.get_form_field_kwargs(),
            )

        raise NotImplementedError(
            "No form field implemented for this question type."
        )

    def get_field_tuple(self):
        return (str(self.id), self.get_form_field())

    def __str__(self):
        if self.mandatory:
            return self.text + " (*)"
        return self.text

    @property
    def possible_answers(self):
        return self.answers.splitlines()

    def get_field_choices(self):
        return [(answer, answer) for answer in self.possible_answers]


class FormAnswer(models.Model):
    attendee = models.ForeignKey(
        to="eventsd_events.Attendee",
        related_name="form_answers",
        verbose_name=_("Participant"),
        on_delete=models.CASCADE,
    )

    question = models.ForeignKey(
        to="eventsd_events.Question",
        related_name="form_answers",
        verbose_name=_("Question"),
        on_delete=models.CASCADE,
    )

    answer = models.TextField(
        verbose_name=_("Réponse"),
        max_length=10_000,
    )

    class Meta:
        verbose_name = _("réponse formulaire")
        verbose_name_plural = _("réponses formulaire")
        unique_together = (("attendee", "question"),)
        ordering = ("question__order",)

    def __str__(self):
        return self.answer


class AttendeeLabel(models.Model):
    title = models.CharField(max_length=120, verbose_name=_("Titre"))

    class Meta:
        verbose_name = _("label participant")
        verbose_name_plural = _("labels participant")
        ordering = ("title",)

    def __str__(self):
        return self.title
