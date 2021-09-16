from django.utils import timezone
from drf_renderer_xlsx.mixins import XLSXFileMixin
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework.fields import CharField
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ReadOnlyModelViewSet

from NEMO_billing.rates.models import Rate, RateType

date_time_format_export = "%m_%d_%Y-%H_%M_%S"


class RateTypeSerializer(ModelSerializer):
    class Meta:
        model = RateType
        fields = "__all__"


class RateSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Rate
        fields = "__all__"
        expandable_fields = {
            "type": "NEMO_billing.rates.api.RateTypeSerializer",
            "tool": "NEMO.serializers.ToolSerializer",
            "area": "NEMO.serializers.AreaSerializer",
            "consumable": "NEMO.serializers.ConsumableSerializer",
        }

    type_name = CharField(source="type.get_type_display")
    category_name = CharField(source="category.name", default=None)
    tool_name = CharField(source="tool.name", default=None)
    area_name = CharField(source="area.name", default=None)
    consumable_name = CharField(source="consumable.name", default=None)


class RateTypeViewSet(XLSXFileMixin, ReadOnlyModelViewSet):
    queryset = RateType.objects.all()
    serializer_class = RateTypeSerializer

    def get_filename(self):
        return f"rate_types-{timezone.localtime().strftime(date_time_format_export)}.xlsx"


class RateViewSet(XLSXFileMixin, ReadOnlyModelViewSet):
    queryset = Rate.objects.all()
    serializer_class = RateSerializer
    filterset_fields = {
        "type": ["exact", "in"],
        "category": ["exact", "in"],
        "id": ["exact", "in"],
        "tool": ["exact", "in"],
        "area": ["exact", "in"],
        "consumable": ["exact", "in"],
    }

    def get_filename(self):
        return f"rates-{timezone.localtime().strftime(date_time_format_export)}.xlsx"
