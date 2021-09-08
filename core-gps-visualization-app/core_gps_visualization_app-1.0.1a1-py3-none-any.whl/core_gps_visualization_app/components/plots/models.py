"""
Plots models
"""

from django_mongoengine import fields, Document


class Plots(Document):
    """ Data Structure to handle Plots interactions

    """
    plots_data = fields.ListField(blank=False)
    default_config = fields.DictField(blank=False)
    configuration = fields.ListField(blank=True)  # [{'plot_selected,timeRange': html1},..]}
    plot_selected = fields.StringField(blank=False)
    time_range_selected = fields.StringField(blank=False)
    completed = fields.BooleanField(blank=False)

    def get_plot_selected(self):
        """

        Returns: plot selected

        """
        return self.plot_selected

    def get_time_range_selected(self):
        """

        Returns: time range selected

        """
        return self.time_range_selected

    def get_plots_data(self):
        """

        Returns: plots list

        """
        return self.plots_data

    def update_plot_selected(self, plot_name):
        """ Update plot selected

        Args:
            plot_name (string):

        Returns:

        """
        self.plot_selected = plot_name
        self.save()

    def update_time_range_selected(self, time_range):
        """ Update time range selected

        Args:
            time_range (string):

        Returns:

        """
        self.time_range_selected = time_range
        self.save()

    def get_default_config(self):
        """

        Returns:

        """
        return self.default_config

    def config_exists(self, config):
        """

        Args:
            config:

        Returns:

        """
        config_exists = False
        for existing_config in self.configuration:
            if config in existing_config:
                config_exists = True
        return config_exists

    def get_html(self, config):
        """

        Args:
            config:

        Returns:

        """
        html = "<p>No html found for this configuration..</p>"
        for existing_config in self.configuration:
            if config in existing_config:
                html = existing_config[config]
        return html

    def create_config(self, config, html):
        """

        Args:
            config:
            html:

        Returns:

        """
        if len(self.configuration) == 0:
            self.configuration = [{config: html}]
        else:
            self.configuration.append({config: html})
        self.save()

    def is_completed(self):
        return self.completed

    def update_completed(self):
        self.completed = not self.completed
        self.save()

    @staticmethod
    def create_plots(plots_data):
        """

        Args:
            plots_data:

        Returns:

        """
        return Plots.objects.create(plots_data=plots_data,
                                    default_config={'plot_selected': 'Scatter', 'time_range': 'Seconds'},
                                    plot_selected='Scatter',
                                    time_range_selected='Seconds',
                                    completed=False)

