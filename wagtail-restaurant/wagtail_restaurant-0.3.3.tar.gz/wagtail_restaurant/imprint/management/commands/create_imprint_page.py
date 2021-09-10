from django.core.management.base import BaseCommand, CommandError
from django.contrib.contenttypes.models import ContentType

from apps.home.models import HomePage
from ...models import ImprintPage

class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            home_page = HomePage.objects.first()
            imprint_content_type = ContentType.objects.get_for_model(ImprintPage)
            impressum= ImprintPage  (
                                  title="IMPRESSUM",
                                  draft_title="IMPRESSUM",
                                  slug='impressum',
                                  content_type=imprint_content_type,
                                  show_in_menus=True,
                                )

            home_page.add_child(instance=impressum)

            # self.stdout.write(self.style.SUCCESS('Success'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))
            return
        self.stdout.write(self.style.SUCCESS('  ✓  ') + 'Successful! Impressum Page created')
        return