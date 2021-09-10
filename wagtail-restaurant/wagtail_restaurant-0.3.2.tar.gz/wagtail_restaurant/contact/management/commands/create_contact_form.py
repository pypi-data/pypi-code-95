from django.core.management.base import BaseCommand, CommandError
from django.contrib.contenttypes.models import ContentType

from wagtail.core.models import Page
from ...models import FormFields, ContactPage

class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            # Get content type
            contact_content_type = ContentType.objects.get_for_model(ContactPage)

            # Find page equals to content type
            parent_page = Page.objects.get(content_type_id=contact_content_type.id).specific
            
            # Get contanct page id
            contact_page_id = parent_page.id

            # Add fields
            name = FormFields.objects.create(sort_order= 0, clean_name='name', label='Name', field_type='singleline', required=True,page_id=contact_page_id)
            email = FormFields.objects.create(sort_order= 1, clean_name='email',label='E-mail',field_type='email',required=True,page_id=contact_page_id)
            phone = FormFields.objects.create(sort_order= 2, clean_name='phone', label='Telefonnummer', field_type='singleline',required=False, page_id=contact_page_id)
            comment = FormFields.objects.create(sort_order= 3, clean_name='comment',label='Kommentar',field_type='multiline',required=True, page_id=contact_page_id)

            # self.stdout.write(self.style.SUCCESS('Success'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))
            return
        self.stdout.write(self.style.SUCCESS('  ✓  ') + 'Successfully Form Fields created')
        return