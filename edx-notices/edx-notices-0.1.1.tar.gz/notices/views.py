"""
Rendered views for the notices app.
"""

import logging
from urllib.parse import unquote, urlsplit

from django.conf import settings
from django.utils.translation import get_language_from_request
from django.views.generic import DetailView

from notices.models import Notice


logger = logging.getLogger(__name__)


class RenderNotice(DetailView):
    """Notice rendering view."""

    # This base template will include a separate template housing the requested credential body.
    # This allows us to use this one view to render credentials for any number of content types
    # (e.g., courses, programs).
    template_name = "notice.html"
    model = Notice

    def get_context_data(self, **kwargs):
        """
        Add the context for the rendering templates.
        """
        context = super().get_context_data(**kwargs)
        user_language = get_language_from_request(self.request)
        body_content = self.object.translated_notice_content.get(language_code=user_language).html_content
        forwarding_url = unquote(self.request.GET.get("next", ""))
        (_, forwarding_url_domain, _, _, _) = urlsplit(forwarding_url)
        if forwarding_url_domain not in settings.FEATURES["NOTICES_REDIRECT_ALLOWLIST"]:
            forwarding_url = settings.FEATURES["NOTICES_DEFAULT_REDIRECT_URL"]

        context.update(
            {
                "head_content": self.object.head_content,
                "html_content": body_content,
                "forwarding_url": forwarding_url,
            }
        )
        return context
