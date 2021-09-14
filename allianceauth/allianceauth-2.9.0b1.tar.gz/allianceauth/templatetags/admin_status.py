import logging

import requests
import amqp.exceptions
from packaging.version import Version as Pep440Version, InvalidVersion
from celery.app import app_or_default

from django import template
from django.conf import settings
from django.core.cache import cache

from allianceauth import __version__


register = template.Library()

# cache timers
TAG_CACHE_TIME = 3600  # 1 hours
NOTIFICATION_CACHE_TIME = 300  # 5 minutes
# timeout for all requests
REQUESTS_TIMEOUT = 5    # 5 seconds
# max pages to be fetched from gitlab
MAX_PAGES = 50

GITLAB_AUTH_REPOSITORY_TAGS_URL = (
    'https://gitlab.com/api/v4/projects/allianceauth%2Fallianceauth/repository/tags'
)
GITLAB_AUTH_ANNOUNCEMENT_ISSUES_URL = (
    'https://gitlab.com/api/v4/projects/allianceauth%2Fallianceauth/issues'
    '?labels=announcement&state=opened'
)

logger = logging.getLogger(__name__)


@register.inclusion_tag('allianceauth/admin-status/overview.html')
def status_overview() -> dict:
    response = {
        'notifications': list(),
        'current_version': __version__,
        'task_queue_length': -1,
    }
    response.update(_current_notifications())
    response.update(_current_version_summary())
    response.update({'task_queue_length': _fetch_celery_queue_length()})
    return response


def _fetch_celery_queue_length() -> int:
    try:
        app = app_or_default(None)
        with app.connection_or_acquire() as conn:
            return conn.default_channel.queue_declare(
                queue=getattr(settings, 'CELERY_DEFAULT_QUEUE', 'celery'),
                passive=True
            ).message_count
    except amqp.exceptions.ChannelError:
        # Queue doesn't exist, probably empty
        return 0
    except Exception:
        logger.exception("Failed to get celery queue length")
    return -1


def _current_notifications() -> dict:
    """returns the newest 5 announcement issues"""
    try:
        notifications = cache.get_or_set(
            'gitlab_notification_issues',
            _fetch_notification_issues_from_gitlab,
            NOTIFICATION_CACHE_TIME
        )
    except requests.HTTPError:
        logger.warning('Error while getting gitlab notifications', exc_info=True)
        top_notifications = []
    else:
        if notifications:
            top_notifications = notifications[:5]
        else:
            top_notifications = []

    response = {
        'notifications': top_notifications,
    }
    return response


def _fetch_notification_issues_from_gitlab() -> list:
    return _fetch_list_from_gitlab(GITLAB_AUTH_ANNOUNCEMENT_ISSUES_URL, max_pages=10)


def _current_version_summary() -> dict:
    """returns the current version info"""
    try:
        tags = cache.get_or_set(
            'git_release_tags', _fetch_tags_from_gitlab, TAG_CACHE_TIME
        )
    except requests.HTTPError:
        logger.warning('Error while getting gitlab release tags', exc_info=True)
        return {}

    if not tags:
        return {}

    (
        latest_major_version,
        latest_minor_version,
        latest_patch_version,
        latest_beta_version
    ) = _latests_versions(tags)
    current_version = Pep440Version(__version__)

    has_latest_major = \
        current_version >= latest_major_version if latest_major_version else False
    has_latest_minor = \
        current_version >= latest_minor_version if latest_minor_version else False
    has_latest_patch = \
        current_version >= latest_patch_version if latest_patch_version else False
    has_current_beta = \
        current_version.base_version <= latest_beta_version.base_version \
        and latest_major_version.base_version <= latest_beta_version.base_version \
        if latest_beta_version else False

    response = {
        'latest_major': has_latest_major,
        'latest_minor': has_latest_minor,
        'latest_patch': has_latest_patch,
        'latest_beta': has_current_beta,
        'current_version': str(current_version),
        'latest_major_version': str(latest_major_version),
        'latest_minor_version': str(latest_minor_version),
        'latest_patch_version': str(latest_patch_version),
        'latest_beta_version': str(latest_beta_version)
    }
    return response


def _fetch_tags_from_gitlab():
    return _fetch_list_from_gitlab(GITLAB_AUTH_REPOSITORY_TAGS_URL)


def _latests_versions(tags: list) -> tuple:
    """returns latests version from given tags list

    Non-compliant tags will be ignored
    """
    versions = list()
    betas = list()
    for tag in tags:
        try:
            version = Pep440Version(tag.get('name'))
        except InvalidVersion:
            pass
        else:
            if version.is_prerelease or version.is_devrelease:
                betas.append(version)
            else:
                versions.append(version)

    latest_version = latest_patch_version = max(versions)
    latest_major_version = min([
        v for v in versions if v.major == latest_version.major
    ])
    latest_minor_version = min([
        v for v in versions
        if v.major == latest_version.major and v.minor == latest_version.minor
    ])
    latest_beta_version = max(betas)
    return (
        latest_major_version,
        latest_minor_version,
        latest_patch_version,
        latest_beta_version
    )


def _fetch_list_from_gitlab(url: str, max_pages: int = MAX_PAGES) -> list:
    """returns a list from the GitLab API. Supports pageing"""
    result = list()
    for page in range(1, max_pages + 1):
        request = requests.get(
            url, params={'page': page}, timeout=REQUESTS_TIMEOUT
        )
        request.raise_for_status()
        result += request.json()
        if 'x-total-pages' in request.headers:
            try:
                total_pages = int(request.headers['x-total-pages'])
            except ValueError:
                total_pages = None
        else:
            total_pages = None

        if not total_pages or page >= total_pages:
            break

    return result
