import holoviews as hv
from core_main_app.commons import exceptions
from core_gps_visualization_app.utils.parser import stringify, unit_stringify
from core_gps_visualization_app.utils import parser as utils


def plot_layout(plots_type, plots_data):
    """

    Args:
        plots_type:
        plots_data:

    Returns:

    """
    hv.extension('bokeh')

    if plots_type == 'Scatter':
        layout = plot_scatter(plots_data)
    if plots_type == 'Line':
        layout = plot_line(plots_data)
    if plots_type == 'Box':
        layout = plot_box(plots_data)

    try:
        return layout
    except Exception:
        raise exceptions.DoesNotExist("No plots type found!")


def plot_layout_by_time_range(plots_data, plots_type, time_range):
    """

    Args:
        plots_data:
        plots_type:
        time_range:

    Returns:

    """
    if plots_type == 'Box' and time_range != "Seconds":
        return 0
    for dict_data in plots_data:
        if dict_data['x'][0] == "Time (UTC)":
            dict_data['data'] = utils.parse_time_range_data(dict_data['data'], time_range)
    return plot_layout(plots_type, plots_data)


def plot_scatter(plots_data):
    """

    Args:
        plots_data:

    Returns:

    """
    already_plot = []
    all_scatter_plots = []
    len_plots = 0
    while len(already_plot) == len_plots:
        plots_to_overlay = []
        for scatter_data_dict in plots_data:
            if len(plots_to_overlay) > 0:
                if plots_to_overlay[0]['x'] == scatter_data_dict['x'] and \
                        plots_to_overlay[0]['y'] == scatter_data_dict['y']:
                    plots_to_overlay.append(scatter_data_dict)
            else:
                if (scatter_data_dict['x'], scatter_data_dict['y']) not in already_plot:
                    plots_to_overlay.append(scatter_data_dict)

        if len(plots_to_overlay) > 0:
            plots = []
            # All plots share same x and y so we can take the first one
            y_tuple = plots_to_overlay[0]['y']
            x_tuple = plots_to_overlay[0]['x']

            for plot in plots_to_overlay:
                label = ''
                if plot['ids'] is not None:
                    for id_dict in plot['ids']:
                        label += stringify(next(iter(id_dict.keys()))) + ': ' + stringify(next(iter(id_dict.values())))
                        label += ' - '
                    label = label[:-3]

                x_unit_label = unit_stringify(plot['x'][1])
                y_unit_label = unit_stringify(plot['y'][1])

                scatter_plot = hv.Scatter(plot['data'], stringify(plot['x'][0]) + x_unit_label,
                                          stringify(plot['y'][0]) + y_unit_label, label=label)

                plots.append(scatter_plot)

            overlaid_plot = hv.Overlay(plots)
            overlaid_plot.label = "Scatter: " + stringify(y_tuple[0]) + " against " + stringify(x_tuple[0])
            overlaid_plot.opts(hv.opts.Overlay(legend_position='left', show_legend=True, legend_limit=100,
                                               show_frame=False))

            all_scatter_plots.append(overlaid_plot)
            already_plot.append((x_tuple, y_tuple))
        len_plots += 1

    layout = hv.Layout(all_scatter_plots).cols(1)
    layout.opts(hv.opts.Scatter(width=1200, height=600))

    return layout


def plot_line(plots_data):
    """

    Args:
        plots_data:

    Returns:

    """
    already_plot = []
    all_line_plots, all_line_plots, all_box_plots = [], [], []
    len_plots = 0
    while len(already_plot) == len_plots:
        plots_to_overlay = []
        for line_data_dict in plots_data:

            if len(plots_to_overlay) > 0:
                if plots_to_overlay[0]['x'] == line_data_dict['x'] and plots_to_overlay[0]['y'] == \
                        line_data_dict['y']:
                    plots_to_overlay.append(line_data_dict)
            else:
                if (line_data_dict['x'], line_data_dict['y']) not in already_plot:
                    plots_to_overlay.append(line_data_dict)

        if len(plots_to_overlay) > 0:
            plots = []
            # All plots share same x and y so we can take the first one
            y_tuple = plots_to_overlay[0]['y']
            x_tuple = plots_to_overlay[0]['x']
            for plot in plots_to_overlay:
                label = ''
                if plot['ids'] is not None:
                    for id_dict in plot['ids']:
                        label += stringify(next(iter(id_dict.keys()))) + ': ' + stringify(next(iter(id_dict.values())))
                        label += ' - '
                    label = label[:-3]

                x_unit_label = unit_stringify(plot['x'][1])
                y_unit_label = unit_stringify(plot['y'][1])
                line_plot = hv.Curve(plot['data'], stringify(plot['x'][0]) + x_unit_label,
                                     stringify(plot['y'][0]) + y_unit_label, label=label)
                plots.append(line_plot)

            overlaid_plot = hv.Overlay(plots)
            overlaid_plot.label = "Line: " + str(y_tuple[0]) + " against " + str(x_tuple[0])
            overlaid_plot.opts(hv.opts.Overlay(legend_position='left', show_frame=False, show_legend=True,
                                               legend_limit=100))

            all_line_plots.append(overlaid_plot)
            already_plot.append((x_tuple, y_tuple))
        len_plots += 1

    layout = hv.Layout(all_line_plots).cols(1)
    layout.opts(hv.opts.Curve(width=1200, height=600))

    return layout


def plot_box(plots_data):
    """

    Args:
        plots_data:

    Returns:

    """
    box_plots = []
    for box_data_dict in plots_data:
        x_unit_label = unit_stringify(box_data_dict['x'][1])
        y_unit_label = unit_stringify(box_data_dict['y'][1])
        box_plot = hv.BoxWhisker(box_data_dict['data'], stringify(box_data_dict['x'][0])
                                 + x_unit_label,  stringify(box_data_dict['y'][0])
                                 + y_unit_label)
        box_plots.append(box_plot)
    layout = hv.Layout(box_plots).cols(1)
    layout.opts(hv.opts.BoxWhisker(width=1200, height=600))

    return layout




