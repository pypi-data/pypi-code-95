import os

from django.db import models, connection
from django.apps import apps
from django.conf import settings


def get_file_fields():
    for model in apps.get_models():
        for field in model._meta.fields:
            if isinstance(field, models.FileField):
                yield field


def get_all_media():
    media = set()
    for root, dirs, files in os.walk(settings.MEDIA_ROOT):
        for name in files:
            full_path = os.path.abspath(os.path.join(root, name))
            media.add(full_path)
    return media


def get_used_media():
    parts = []
    for field in get_file_fields():
        db_table = field.model._meta.db_table
        db_column = field.db_column or field.name

        parts.append(
            f"SELECT {db_column} FROM {db_table} WHERE {db_column} !='' AND {db_column} IS NOT NULL"
        )
    query = '\nUNION ALL\n'.join(parts)

    with connection.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
    return {os.path.join(settings.MEDIA_ROOT, r[0]) for r in rows}


def get_unused_media():
    return get_all_media() - get_used_media()

