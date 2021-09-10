from django.core.management.base import BaseCommand, CommandError
from django.contrib.contenttypes.models import ContentType

from apps.home.models import HomePage
from ...models import ContactPage

class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            home_page = HomePage.objects.first()
            contact_content_type = ContentType.objects.get_for_model(ContactPage)
            contact_page= ContactPage(  title="KONTAKT",
                                        draft_title="KONTAKT",
                                        slug='kontakt',
                                        intro='<p>Schreiben Sie uns eine E-Mail.<br/>Wir freuen uns auf Ihre Kontaktaufnahme.</p>',
                                        thank_you_text='<p>Danke, dass sie uns kontaktiert haben! Wir werden uns in Kürze mit Ihnen in Verbindung setzen.</p>',
                                        content_type=contact_content_type,
                                        show_in_menus=True,
                                     )

            home_page.add_child(instance=contact_page)
            # self.stdout.write(self.style.SUCCESS(contact_content_type.app_label))
        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))
            return
        self.stdout.write(self.style.SUCCESS('  ✓  ') + 'Successfully Contact Page created')
        return