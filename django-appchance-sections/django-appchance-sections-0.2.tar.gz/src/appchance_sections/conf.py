from django.conf import settings

SECTION_MODEL = getattr(settings, "SECTION_MODEL")
SECTION_CONTENT_MODEL = getattr(settings, "SECTION_CONTENT_MODEL", "appchance_sections.models.Content")
SECTION_CONTENTS_CACHE_ALIAS = getattr(settings, "SECTION_CONTENTS_CACHE_ALIAS", "default")
SECTION_CONTENTS_CACHE_KEY = getattr(settings, "SECTION_CONTENTS_CACHE_KEY", "section_content_cache_key")
SECTION_CONTENTS_CACHE_TIMEOUT = getattr(settings, "SECTION_CONTENTS_CACHE_TIMEOUT", 30)
