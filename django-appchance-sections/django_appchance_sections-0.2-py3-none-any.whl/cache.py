from django.conf import settings
from django.core.cache import caches
from django.core.exceptions import ImproperlyConfigured

from appchance_sections.conf import (
    SECTION_CONTENTS_CACHE_ALIAS,
    SECTION_CONTENTS_CACHE_KEY,
    SECTION_CONTENTS_CACHE_TIMEOUT,
)


def get_contents_cache():
    if SECTION_CONTENTS_CACHE_ALIAS != "default" and SECTION_CONTENTS_CACHE_ALIAS not in settings.CACHES:
        raise ImproperlyConfigured(
            "Cache alias '%s' not set in settings.CACHES" % SECTION_CONTENTS_CACHE_ALIAS
        ) from None
    return caches[SECTION_CONTENTS_CACHE_ALIAS]


def get_contents_cache_key():
    return SECTION_CONTENTS_CACHE_KEY


def get_contents_cache_timeout():
    return int(SECTION_CONTENTS_CACHE_TIMEOUT)
