""" Visualization tasks """
import logging
import copy
import time
import holoviews as hv
from celery import shared_task

from core_gps_visualization_app.components.plots import api as plots_api
from core_gps_visualization_app.components.data import operations
from core_gps_visualization_app.components.plots import operations as plots_operations
from core_gps_visualization_app.views.user.forms import SelectPlotDropDown, SelectTimeRangeDropDown

logger = logging.getLogger(__name__)


#@periodic_task(run_every=crontab(minute=0, hour=0))
@shared_task
def build_visualization_data():
    """Build visualization data every day at midnight"""
    try:

        start_time = time.time()
        logger.info("Periodic task: START creating plots objects")

        all_parsed_data = operations.get_all_data()
        all_parsed_data = operations.parse_all_data(all_parsed_data)
        plots_object = plots_api.create_and_get_plots(all_parsed_data)
        plots_types = SelectPlotDropDown().fields['plots'].choices
        time_ranges = SelectTimeRangeDropDown().fields['time_ranges'].choices

        for plots_type_tuple in plots_types:
            for time_range_tuple in time_ranges:
                config = str(plots_type_tuple[0]) + ',' + str(time_range_tuple[0])
                plots_data = copy.deepcopy(plots_api.get_plots_data(plots_object))
                layout = plots_operations.plot_layout_by_time_range(plots_data, plots_type_tuple[0], time_range_tuple[0])
                if layout != 0:
                    hv.save(layout, "temp.html")
                    chart_file = open("temp.html", 'r')
                    chart_html = chart_file.read()
                else:
                    chart_html = "<html><p>No charts for this configuration...</p></html>"
                plots_api.create_config(plots_object, config, chart_html)
        plots_api.update_completed(plots_object)

        logger.info("Periodic task: FINISH creating plots objects " +
                    "(" + str((time.time() - start_time)/60) + "minutes)")
    except Exception as e:
        logger.error("An error occurred while creating plots objects")
