from django.db import models
from django.contrib.auth.models import User


class Studienabschnitt(models.Model):
    """
    z.B. "1. Semester", "2. Semester", "Physikum", "STEX", "PJ", ...
    """
    bezeichnung = models.CharField(max_length=100)
    sortierung = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.bezeichnung

    class Meta:
        verbose_name = 'Studienabschnitt/Semester'
        verbose_name_plural = 'Studienabschnitte/Semester'
        ordering = ['sortierung']


class Studiengang(models.Model):
    """
    z.B. "Humanmedizin", "Zahnmedizin", ...
    """
    bezeichnung = models.CharField(max_length=100, unique=True)
    studienabschnitt = models.ManyToManyField(
        Studienabschnitt,
        blank=True,
        related_name='studiengang'
    )

    def __str__(self):
        return self.bezeichnung

    class Meta:
        verbose_name = 'Studiengang'
        verbose_name_plural = 'Studiengänge'
        ordering = ['bezeichnung']


class Gender(models.Model):
    bezeichnung = models.CharField(max_length=100)
    # z.B. "in" für "weiblich" -> "Studentin"
    endung = models.CharField(
        max_length=8,
        blank=True,
    )

    def __str__(self):
        return self.bezeichnung

    class Meta:
        verbose_name = 'Gender/Geschlecht'
        verbose_name_plural = 'Gender/Geschlechter'
        ordering = ['bezeichnung']


class FachschaftUser(models.Model):
    """
    Extends django.contrib.auth.models.User
    FachschaftUser = "StudentInnen allgemein"
    """
    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        related_name='fachschaftuser',
    )
    gender = models.ForeignKey(Gender, on_delete=models.PROTECT)
    studienabschnitt = models.ForeignKey(
        Studienabschnitt,
        on_delete=models.PROTECT,
    )
    studiengang = models.ForeignKey(
        Studiengang,
        on_delete=models.PROTECT,
    )
    nickname = models.CharField(
        max_length=100,
        unique=True,
    )

    def __str__(self):
        """
        returns "[Vorname] [Nachname]"
        """
        return self.user.get_full_name()

    class Meta:
        verbose_name = 'StudentIn'
        verbose_name_plural = 'StudentInnen'
        ordering = ['nickname']
