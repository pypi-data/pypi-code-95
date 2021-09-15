import uuid

from django.db.models.signals import post_delete
from django.dispatch import receiver

from appchance_sections.models import DynamicContentAbstract
from appchance_sections.utils import get_section_model

Section = get_section_model()


@receiver(post_delete, dispatch_uid=uuid.uuid4())
def do_after_delete_dynamic_content(sender, instance, **kwargs):  # pylint: disable=W0613
    if isinstance(instance, DynamicContentAbstract):
        Section.objects.filter(content_slug=instance.content_slug).delete()
