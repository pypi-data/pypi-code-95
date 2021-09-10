from django.core.management.base import BaseCommand, CommandError
from django.core import management
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            management.call_command('migrate')
            management.call_command('create_menu_page')
            management.call_command('create_opening_hours')
            management.call_command('create_imprint_page')
            management.call_command('create_simple_pages')
            management.call_command('create_contact_page')
            management.call_command('create_contact_form')
            management.call_command('create_navigation')
            management.call_command('createuser')
            management.call_command('collectstatic')

            # self.stdout.write(self.style.SUCCESS('Success'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))
            return
        self.stdout.write(self.style.SUCCESS('  ✓  ') + 'Createall Successfully Created All')
        return