from argparse import ArgumentParser

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.module_loading import import_string


class Command(BaseCommand):

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument('-n', '--name', type=str)
        parser.add_argument('-a', '--all', action='store_true', default=False)
        parser.add_argument('-l', '--list', action='store_true', default=False)

    def handle(self, *args, **options):

        if options.get('list') is True:
            print(' | '.join(settings.INITIAL_DATA.keys()))
            return

        if options.get('all') is True:
            for name, module_string in settings.INITIAL_DATA.items():
                if not name.startswith('extra'):
                    for m in module_string:
                        string_to_import = m
                        if not m.endswith('.run'):
                            string_to_import = f'{m}.run'
                        imported = import_string(string_to_import)
                        imported()
            return

        name = options.get('name')
        if name is not None:
            module_string = settings.INITIAL_DATA.get(name)
            for m in module_string:
                string_to_import = m
                if not m.endswith('.run'):
                    string_to_import = f'{m}.run'
                imported = import_string(string_to_import)
                imported()
            return
