from django.core.management.base import BaseCommand, CommandError
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth.models import User

class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            create_super = User.objects.create_superuser(username='zet',email='usezeta@gmail.com',password='ofelya2020',)
        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))
            return
        self.stdout.write(self.style.SUCCESS('  ✓  ') + 'Successfully Super User created')
        return