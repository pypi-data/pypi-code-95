# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def namespace_competition(apps, schema_editor):
    Placeholder = apps.get_model('content', 'Placeholder')
    Placeholder.objects.filter(path='flashboard.sites.FlashSite').update(namespace='competition')


def namespace_scoreboard(apps, schema_editor):
    Placeholder = apps.get_model('content', 'Placeholder')
    Placeholder.objects.filter(path='flashboard.sites.FlashSite').update(namespace='scoreboard')


class Migration(migrations.Migration):

    dependencies = [
        ('flashboard', '0001_initial'),
        ('content', '0003_auto_20160831_0608'),
    ]

    operations = [
        migrations.RunPython(namespace_scoreboard, namespace_competition),
    ]
