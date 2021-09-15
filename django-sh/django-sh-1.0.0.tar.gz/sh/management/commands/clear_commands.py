from django.core.management.base import BaseCommand, CommandError
from sh.models import Command as ShellCommand
from django.utils import timezone
import datetime

class Command(BaseCommand):
    help = 'Delete commands olders than "n" days'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=10)

    def handle(self, *args, **options):
        days = options.get('days')
        date = timezone.now() - datetime.timedelta(days=days)
        total_deleted = ShellCommand.objects.filter(created_at__lte=date).delete()
        self.stdout.write(f"{total_deleted} comandos han sido eliminados")