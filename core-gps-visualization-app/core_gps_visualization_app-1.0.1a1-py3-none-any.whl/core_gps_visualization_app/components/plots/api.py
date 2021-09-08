from core_gps_visualization_app.components.plots.models import Plots


def create_and_get_plots(all_data):
    """ There is maximum a single plots object at any time

    Args:
        all_data:

    Returns:

    """
    plots = Plots.objects.all()
    if len(plots) == 0:
        Plots.create_plots(all_data)
        plots = get_plots()
        return plots
    else:
        return plots[0]


def get_plots():
    """ get unique plots object if it exists, otherwise get None

    Returns:

    """
    plots = Plots.objects.all()
    if len(plots) > 0:
        return plots[0]
    return None


def update_plot_selected(plots, plot_name):
    """ Update the type of plot selected for all plots

    Args:
        plots:
        plot_name:

    Returns:

    """
    return Plots.update_plot_selected(plots, plot_name)


def update_time_range_selected(plots, time_range):
    """ Update the time range selected for all plots

    Args:
        plots:
        time_range

    Returns:

    """
    return Plots.update_time_range_selected(plots, time_range)


def get_plot_selected(plots):
    """

    Returns:

    """
    return Plots.get_plot_selected(plots)


def get_time_range_selected(plots):
    """

    Returns:

    """
    return Plots.get_time_range_selected(plots)


def get_plots_data(plots):
    """

    Returns:

    """
    return Plots.get_plots_data(plots)


def get_default_config(plots):
    """

    Args:
        plots:

    Returns:

    """
    return Plots.get_default_config(plots)


def config_exists(plots, config):
    """

    Args:
        plots:
        config:

    Returns:

    """
    return Plots.config_exists(plots, config)


def get_html(plots, config):
    """

    Args:
        plots:
        config:

    Returns:

    """
    return Plots.get_html(plots, config)


def create_config(plots, config, html):
    """

    Args:
        plots:
        config:
        html:

    Returns:

    """
    return Plots.create_config(plots, config, html)


def is_completed(plots):
    return Plots.is_completed(plots)


def update_completed(plots):
    return Plots.update_completed(plots)
