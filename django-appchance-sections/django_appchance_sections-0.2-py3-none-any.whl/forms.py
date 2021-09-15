from django.forms import ChoiceField, ModelForm

from appchance_sections.utils import get_section_model

Section = get_section_model()


class SectionAdminForm(ModelForm):
    content_slug = ChoiceField(choices=[])
    widget = ChoiceField(choices=[])
    placement = ChoiceField(choices=[])

    class Meta:
        model = Section
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.get("content_slug").choices = self._get_content_slug_choices()
        self.fields.get("widget").choices = self._get_widgets()
        self.fields.get("placement").choices = [(p, p) for p in Section.get_placements()]

    @staticmethod
    def _get_content_slug_choices():
        choices = set()
        for key, value in Section.get_contents().items():
            if value.prefix:
                label = f"[{value.prefix}] {value.name}"
            else:
                label = value.name
            choices.add((key, label))
        return sorted(list(choices), key=lambda x: x[1])

    @staticmethod
    def _get_widgets():
        choices = set()
        for content in Section.get_contents().values():
            for widget in content.widgets:
                if content.prefix:
                    label = f"[{content.prefix}] {widget}"
                else:
                    label = widget
                choices.add((widget, label))
        return sorted(list(choices), key=lambda x: x[1])
