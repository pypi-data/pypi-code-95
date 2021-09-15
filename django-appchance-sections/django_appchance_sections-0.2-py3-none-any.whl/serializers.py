from rest_framework import serializers

from appchance_sections.utils import get_section_model

Section = get_section_model()


class SectionSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(method_name="get_name")
    content_url = serializers.SerializerMethodField(method_name="get_content_url")

    class Meta:
        model = Section
        fields = ("id", "name", "widget", "placement", "order", "content_url")
        ref_name = "MainSectionSerializer"

    def get_content_url(self, instance):
        request = self.context.get("request")
        kwargs = {"pk": request.query_params.get("pk")}
        return request.build_absolute_uri(instance.content.get_url(section=instance, **kwargs))

    @staticmethod
    def get_name(instance):
        return instance.name if instance.name else instance.content.name
