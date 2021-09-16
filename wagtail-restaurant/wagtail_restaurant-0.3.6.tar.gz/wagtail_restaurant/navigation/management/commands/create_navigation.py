from django.core.management.base import BaseCommand, CommandError
from django.contrib.contenttypes.models import ContentType

# Get Models
from wagtail.core.models import Page
from ...models import Navigation, NavigationItem

class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            # Create new navigations
            Navigation.objects.create(title="Header Navigation", slug="header_navigation")
            Navigation.objects.create(title="Footer Navigation", slug="footer_navigation")
            
            # Exclude corepages root, home and some simple pages like uber-uns, impressum
            slug ='root','home','impressum'
            exclude_slug = [s for s in slug] 
            pages = Page.objects.exclude(slug__in=exclude_slug)

            # Create header navigation items
            for iteration, item in enumerate(pages):
                NavigationItem.objects.create(
                        sort_order=iteration, 
                        title=item.title, 
                        url=None, 
                        target_new=False, 
                        page_id=item.id, 
                        navigation_id=1)

            # Exclude corepages root and home
            slug ='root','home'
            exclude_slug = [s for s in slug] 
            pages = Page.objects.exclude(slug__in=exclude_slug)

            # Create footer navigation items
            for iteration, item in enumerate(pages):
                NavigationItem.objects.create(
                        sort_order=iteration, 
                        title=item.title, 
                        url=None, 
                        target_new=False, 
                        page_id=item.id, 
                        navigation_id=2)

            #self.stdout.write(self.style.SUCCESS('Navigation'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))
            return
        self.stdout.write(self.style.SUCCESS('  ✓  ') + 'Successfully Navigation created')
        return

