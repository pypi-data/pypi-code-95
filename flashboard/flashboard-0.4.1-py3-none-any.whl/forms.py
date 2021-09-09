from django import forms
from tournamentcontrol.competition.forms import ConfigurationForm


class FlashConfigurationForm(ConfigurationForm):
    def __init__(self, *args, **kwargs):
        super(FlashConfigurationForm, self).__init__(*args, **kwargs)

        self.fields["delay"] = forms.IntegerField(
            required=False,
            help_text="Number of seconds to wait before moving to the next division.",
        )
