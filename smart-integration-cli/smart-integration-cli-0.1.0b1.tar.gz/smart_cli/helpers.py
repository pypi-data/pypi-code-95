import os
from pathlib import Path


def find_django_manager():
    for file_path in Path('.').glob('**/*manage.py'):
        if 'boto' not in str(file_path):
            return str(file_path)
