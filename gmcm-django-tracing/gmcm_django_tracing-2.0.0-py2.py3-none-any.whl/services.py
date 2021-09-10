# Django
from django.conf import settings

# Other libraries
import httpagentparser

# Local
from .models import Rule


class TraceService:
    @classmethod
    def load_rules(cls):
        try:
            object_list = Rule.objects.filter(is_active=True).values(
                "content_type__model", "check_create", "check_edit", "check_delete"
            )
            rules = {
                obj.get("content_type__model"): {
                    "check_create": obj.get("check_create"),
                    "check_edit": obj.get("check_edit"),
                    "check_delete": obj.get("check_delete"),
                }
                for obj in object_list
            }
        except:
            rules = {}

        if settings.DEBUG:
            print(f"Se cargaron {len(rules)} reglas.")
        return rules

    @classmethod
    def get_ip(cls, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    @classmethod
    def get_os(cls, request):
        user_agent = request.META["HTTP_USER_AGENT"]
        os = httpagentparser.simple_detect(user_agent)[0]
        return os
