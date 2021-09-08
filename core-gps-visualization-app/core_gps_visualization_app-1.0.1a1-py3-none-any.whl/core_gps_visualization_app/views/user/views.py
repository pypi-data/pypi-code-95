"""GPS Visualization user views"""

from core_main_app.utils.rendering import render
from core_gps_visualization_app.views.user.forms import SelectPlotDropDown, SelectTimeRangeDropDown


def index(request):
    """ GPS Visualization homepage

    Args:
        request:

    Returns:

    """
    select_plot = SelectPlotDropDown()
    select_time_range = SelectTimeRangeDropDown()

    context = {
        'plot_selected': select_plot,
        'time_range_selected': select_time_range
    }

    assets = {
        "js": [
            {
                "path": 'core_gps_visualization_app/user/js/load_initial_plots.js',
                "is_raw": False
            },
            {
                "path": 'core_gps_visualization_app/user/js/select_chart_form.js',
                "is_raw": False
            },
            {
                "path": 'core_gps_visualization_app/user/js/select_time_range_form.js',
                "is_raw": False
            },
        ]
    }

    return render(request, "core_gps_visualization_app/user/gps_visualization.html",
                  assets=assets,
                  context=context)
