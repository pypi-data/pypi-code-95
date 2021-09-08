from django.http import HttpResponseBadRequest, HttpResponse
import json

from core_gps_visualization_app.components.plots import api as plots_api
from core_gps_visualization_app.tasks import build_visualization_data


def load_initial_plots(request):
    """ load layout plots into the visualization page

    Args:
        request:

    Returns:
    """
    try:
        # Load all visualizations in Python objects before continuing the thread
        plots_object = plots_api.get_plots()
        charts_html = "<html><p>Charts are still loading, please come back later..</p></html>"

        if plots_object is None:
            # Launch task to build plots
            build_visualization_data()
            return HttpResponse(json.dumps({'charts_html': charts_html}), content_type='application/json')

        if not plots_api.is_completed(plots_object):
            # If task to build plots is not completed
            return HttpResponse(json.dumps({'charts_html': charts_html}), content_type='application/json')

        else:
            default_config = plots_api.get_default_config(plots_object)
            plots_api.update_time_range_selected(plots_object, default_config['time_range'])
            plots_api.update_plot_selected(plots_object, default_config['plot_selected'])
            config = str(default_config['plot_selected']) + ',' + str(default_config['time_range'])

            # Retrieve HTML (as string)
            if plots_api.config_exists(plots_object, config):
                charts_html = plots_api.get_html(plots_object, config)
            else:
                raise ValueError('No config has been found for the plots object...')

        return HttpResponse(json.dumps({'charts_html': charts_html}), content_type='application/json')

    except Exception as e:
        return HttpResponseBadRequest(str(e), content_type='application/javascript')


def update_selected_chart(request):
    """ Update the selected chart

    Args:
        request:

    Returns:
    """
    try:
        plot_selected = request.POST.get('plot_selected', None)

        plots_object = plots_api.get_plots()
        plots_api.update_plot_selected(plots_object, plot_selected)
        time_range_selected = plots_api.get_time_range_selected(plots_object)

        config = str(plot_selected) + ',' + str(time_range_selected)

        # Retrieve HTML (as string)
        if plots_api.config_exists(plots_object, config):
            charts_html = plots_api.get_html(plots_object, config)
        else:
            raise ValueError('No config has been found for the plots object...')

        return HttpResponse(json.dumps({'charts_html': charts_html}), content_type='application/json')
    except Exception as e:
        return HttpResponseBadRequest(str(e), content_type='application/javascript')


def update_time_range_chart(request):
    """ Update the time range for charts

    Args:
        request:

    Returns:

    """
    try:
        time_range_selected = request.POST.get('time_range_selected', None)

        plots_object = plots_api.get_plots()
        plots_api.update_time_range_selected(plots_object, time_range_selected)
        plot_selected = plots_api.get_plot_selected(plots_object)

        config = str(plot_selected) + ',' + str(time_range_selected)

        # Retrieve HTML (as string)
        if plots_api.config_exists(plots_object, config):
            charts_html = plots_api.get_html(plots_object, config)
        else:
            raise ValueError('No config has been found for the plots object...')

        return HttpResponse(json.dumps({'charts_html': charts_html}), content_type='application/json')
    except Exception as e:
        return HttpResponseBadRequest(str(e), content_type='application/javascript')
