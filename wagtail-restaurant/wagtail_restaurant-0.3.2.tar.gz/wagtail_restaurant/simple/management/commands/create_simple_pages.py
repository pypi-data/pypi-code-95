from django.core.management.base import BaseCommand, CommandError
from django.contrib.contenttypes.models import ContentType

from apps.home.models import HomePage
from ...models import SimplePage

class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            home_page = HomePage.objects.first()
            simple_content_type = ContentType.objects.get_for_model(SimplePage)
            uber_uns= SimplePage  (
                                  title="ÜBER UNS",
                                  draft_title="ÜBER UNS",
                                  slug='uber-uns',
                                  content_type=simple_content_type,
                                  show_in_menus=True,
                                )

            home_page.add_child(instance=uber_uns)

            # self.stdout.write(self.style.SUCCESS('Success'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))
            return
        self.stdout.write(self.style.SUCCESS('  ✓  ') + 'Successful! Simple Pages created')
        return