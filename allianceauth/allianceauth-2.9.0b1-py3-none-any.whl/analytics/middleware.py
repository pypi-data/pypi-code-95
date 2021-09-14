from bs4 import BeautifulSoup

from django.utils.deprecation import MiddlewareMixin
from .models import AnalyticsTokens, AnalyticsIdentifier
from .tasks import send_ga_tracking_web_view


class AnalyticsMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        """Django Middleware: Process Page Views and creates Analytics Celery Tasks"""
        analyticstokens = AnalyticsTokens.objects.all()
        client_id = AnalyticsIdentifier.objects.get(id=1).identifier.hex
        try:
            title = BeautifulSoup(
                response.content, "html.parser").html.head.title.text
        except AttributeError:
            title = ''
        for token in analyticstokens:
            # Check if Page View Sending is Disabled
            if token.send_page_views is False:
                continue
            # Check Exclusions
            if request.path in token.ignore_paths.all():
                continue

            tracking_id = token.token
            locale = request.LANGUAGE_CODE
            path = request.path
            try:
                useragent = request.headers["User-Agent"]
            except KeyError:
                useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"

            send_ga_tracking_web_view.s(tracking_id=tracking_id,
                                        client_id=client_id,
                                        page=path,
                                        title=title,
                                        locale=locale,
                                        useragent=useragent).\
                apply_async(priority=9)
        return response
