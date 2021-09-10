from django.core.management.base import BaseCommand, CommandError
from django.contrib.contenttypes.models import ContentType

from ...models import OpeningHours

class Command(BaseCommand):
    help = 'Prints all book titles in the database'

    def handle(self, *args, **options):
        try:

            OpeningHours.objects.create(weekday="0", from_hour='09:00:00', to_hour='18:00:00')
            OpeningHours.objects.create(weekday="1", from_hour='09:00:00', to_hour='18:00:00')
            OpeningHours.objects.create(weekday="2", from_hour='09:00:00', to_hour='18:00:00')
            OpeningHours.objects.create(weekday="3", from_hour='09:00:00', to_hour='18:00:00')
            OpeningHours.objects.create(weekday="4", from_hour='09:00:00', to_hour='18:00:00')
            OpeningHours.objects.create(weekday="5", from_hour='09:00:00', to_hour='18:00:00')
            OpeningHours.objects.create(weekday="6", from_hour=None, to_hour=None)

            # self.stdout.write(self.style.SUCCESS('Success'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))
            return

        self.stdout.write(self.style.SUCCESS('  ✓  ') + 'Successfully Opening Hours objects created')
        return