"""Visualization forms"""
from django import forms


class SelectPlotDropDown(forms.Form):
    """Form to select what chart to display

    """
    plots = forms.ChoiceField(label='Change plot ', required=True, widget=forms.Select())

    def __init__(self, *args):
        super(SelectPlotDropDown, self).__init__(*args)
        plots = [('Scatter', 'Scatter'), ('Line', 'Line'), ('Box', 'Box')]
        selected = plots[0]
        if plots:
            self.fields['plots'].choices = plots
        if selected:
            self.fields['plots'].initial = [selected]


class SelectTimeRangeDropDown(forms.Form):
    """Form to select a different time range for the charts

    """
    time_ranges = forms.ChoiceField(label='Select time range ', required=True, widget=forms.Select())

    def __init__(self, *args):
        super(SelectTimeRangeDropDown, self).__init__(*args)
        time_ranges = [('Seconds', 'Seconds'), ('Minutes', 'Minutes'), ('Hours', 'Hours'), ('Days', 'Days')]
        selected = time_ranges[0]
        self.fields['time_ranges'].choices = time_ranges
        self.fields['time_ranges'].initial = [selected]
