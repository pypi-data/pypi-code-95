from django.core.management.base import BaseCommand, CommandError
from django.contrib.contenttypes.models import ContentType

from apps.home.models import HomePage
from ...models import MenuPage

class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            home_page = HomePage.objects.first()
            menu_content_type = ContentType.objects.get_for_model(MenuPage)
            menu_page= MenuPage(  title="SPEISEKARTE",
                                        draft_title="SPEISEKARTE",
                                        slug='speisekarte',
                                        content_type=menu_content_type,
                                        show_in_menus=True,
                                     )

            home_page.add_child(instance=menu_page)
            # self.stdout.write(self.style.SUCCESS(menu_content_type.app_label))
        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))
            return
        self.stdout.write(self.style.SUCCESS('  ✓  ') + 'Successfully Menu Page created')
        return