r"""
showy.py

Showy
=====


**SHOWY**  in `arnica/utils` is a helper for matplotlib subplots.
If the data is stored as a disct, the layout can be saved as a template
in .yml format.
If can use wildcards if the dictionary keys allows it.


Simple example
***************


::

    import numpy as np
    from arnica.utils.matplotlib_display import showy


    def showy_demo_plain():
        data = dict()
        data["time"] = np.linspace(0, 0.1, num=256)

        data["sine_10"] = np.cos(data["time"] * 10 * 2 * np.pi)
        data["sine_30"] = np.cos(data["time"] * 30 * 2 * np.pi)
        data["sine_100"] = np.cos(data["time"] * 100 * 2 * np.pi)
        data["sine_100p1"] = 1. + np.cos(data["time"] * 100 * 2 * np.pi)

        # Creating a template
        layout = {
            "title": "Example",
            "graphs": [
                {
                    "curves": [{"var": "sine_10"}],
                    "x_var": "time",
                    "y_label": "Fifi [mol/m³/s]",
                    "x_label": "Time [s]",
                    "title": "Sinus of frquency *"
                },
                {
                    "curves": [{"var": "sine_30"}],
                    "x_var": "time",
                    "y_label": "Riri [Hz]",
                    "x_label": "Time [s]",
                    "title": "Second graph"
                },
                {
                    "curves": [
                        {
                            "var": "sine_100",
                            "legend": "origin",
                        },
                        {
                            "var": "sine_100p1",
                            "legend": "shifted",
                        }
                    ],
                    "x_var": "time",
                    "y_label": "Loulou [cow/mug]",
                    "x_label": "Time [s]",
                    "title": "Third graphg"
                }
            ],
            "figure_structure": [3, 1],
            "figure_dpi": 92.6
        }

    # Displaying the data described in the new created layout
    showy(layout, data)


Using wildcard ' * '
********************

In showy you can show all the graphs with a same prefix putting a "**\***".
For example if you have 3 variables like var_1, var_2, var_3
you can just write var_*. An example is shown below:

::

    import numpy as np
    from arnica.utils.matplotlib_display import display

    def showy_demo_wildcards():
        data = dict()
        data["time"] = np.linspace(0, 0.1, num=256)

        freq = 10.
        for freq in np.linspace(10, 20, num=9):
            data["sine_" + str(freq)] = np.cos(data["time"]*freq*2*np.pi)

        # Creating a template
        template = {
            "title": "Example",
            "graphs": [{
                "curves": [{"var": "sine_*"}],
                "x_var": "time",
                "y_label": "Sine [mol/m³/s]",
                "x_label": "Time [s]",
                "title": "Sinus of frquency *"
            }],
            "figure_structure": [3, 3],
            "figure_dpi": 92.6
        }

        showy(template, data)


Options available
***************

The scheme that showing all the options available is shown below.

.. highlight:: yaml

::

    title: Layout scheme
    description: The structure that a layout has to respect in order to be used to plot
      data with Showy
    type: object
    properties:
      title:
        description: The title of the layout
        type: string
      graphs:
        description: The graphs of the layout
        type: array
        items:
          description: A graph
          type: object
          properties:
            curves:
              description: The curves of the graph
              type: array
              items:
                description: A curve
                type: object
                properties:
                  var:
                    description: The name of the data for the Y-axis
                    type: string
                  legend:
                    description: The legend of the curve
                    type: string
                required:
                - var
                additionalProperties: false
              minItems: 1
            x_var:
              description: The name of the data for the X-axis
              type: string
            y_label:
              description: The label of the Y-axis
              type: string
            x_label:
              description: The label of the X-axis
              type: string
            title:
              description: The title of the graph
              type: string
          required:
          - curves
          - x_var
          additionalProperties: false
        minItems: 1
      figure_dpi:
        description: The number of dots per inch of the figure
        type: number
        exclusiveMinimum: 0
      figure_size:
        description: The size of the figure in inches
        type: array
        items:
          description: A length in inches
          type: number
          exclusiveMinimum: 0
        minItems: 2
        maxItems: 2
      figure_structure:
        description: The numbers of rows and columns of graphs
        type: array
        items:
          description: An integer for a number of rows or columns
          type: integer
          minimum: 1
        minItems: 2
        maxItems: 2
    required:
    - graphs
    additionalProperties: false

"""

import warnings
from math import ceil
import matplotlib.pyplot as plt
from arnica.utils.lay_and_temp_manager import decompact_template

__all__ = ["showy", "display"]



def display(**kwargs):
    """Retro compatibility"""

    warnings.warn("Use *showy* instead of *display*", DeprecationWarning)
    showy(**kwargs)


def showy(layout, data, data_c=None, show=True):
    """It displays the desired graphs described by the provided layout
    thanks to the provided key-value object which contains
    the required data

    Input:
    ------
    data : key-value object
    layout : nested object
    """
    #print(layout['graphs'])
    
    for graph_layout in layout["graphs"]:
        #print(graph_layout['y_label'])
        if "*" in graph_layout["y_label"]:
            layout = decompact_template(layout, data)
        for var in graph_layout["curves"]:
            for val in var.values():
                if "*" in val:
                    layout = decompact_template(layout, data)

    figure_number = 0
    graph_position = 1
    display_params = initialize_display(layout)

    if data_c is None:

        for graph_layout in layout['graphs']:
            if (graph_position > display_params['numb_max_of_graphs_per_fig']
                    or figure_number == 0):
                graph_position = 1
                figure_number += 1
                figure = build_new_figure(display_params, figure_number)

                
            build_new_graph(figure, display_params['fig_struct'],
                            graph_position, graph_layout, data)
            graph_position += 1
            
    else:

        for graph_layout in layout['graphs']:
            if (graph_position > display_params['numb_max_of_graphs_per_fig']
                    or figure_number == 0):
                graph_position = 1
                figure_number += 1
                figure = build_new_figure(display_params, figure_number)

            build_new_graph(figure, display_params['fig_struct'],
                            graph_position, graph_layout, data, data_c)
                
            graph_position += 1
    
    if show:
        plt.show()


def initialize_display(layout):
    """Sets some parameters needed by the function "display", thanks
    to the provided layout, and returns them in a dictionary

    Input:
    ------
    layout : nested object

    Output:
    ------
    display_params : dictionary
    """

    display_params = {}
    display_params['numb_of_graphs'] = len(layout['graphs'])

    if "figure_structure" in layout:
        display_params['fig_struct'] = layout["figure_structure"]
    else:
        if display_params['numb_of_graphs'] == 1:
            display_params['fig_struct'] = [1, 1]
        else:
            display_params['fig_struct'] = [2, 3]

    display_params['numb_max_of_graphs_per_fig'] = (
        display_params['fig_struct'][0] * display_params['fig_struct'][1])
    display_params['numb_of_figs'] = ceil(
        display_params['numb_of_graphs']
        / display_params['numb_max_of_graphs_per_fig'])

    if "figure_dpi" in layout:
        display_params['fig_dpi'] = layout["figure_dpi"]
    else:
        display_params['fig_dpi'] = None

    if "figure_size" in layout:
        # print('figure_size', layout["figure_size"])
        display_params['fig_size'] = layout["figure_size"]
    else:
        display_params['fig_size'] = None

    
    if "title" in layout:
        if layout['title'] == 'NS':
            display_params['lay_title'] = 'NS: Navier-Stokes global quantities'
        elif layout['title']== 'REAC':
            display_params['lay_title'] = 'REAC: Reaction parameters'
        else:
            display_params['lay_title'] =  layout['title'] 
    else:
        display_params['lay_title'] = None


    return display_params


def build_new_figure(display_params, figure_number):
    """Builds a new matplotlib figure thanks to the provided parameters

    Input:
    ------
    display_params : dictionary
    figure_number : integer

    Output:
    ------
    figure : matplotlib object
    """

    if display_params['fig_dpi']:
        figure = plt.figure(dpi=display_params['fig_dpi'])
    else:
        figure = plt.figure()

    if display_params['fig_size']:
        figure.set_size_inches(*display_params['fig_size'])

    if display_params['lay_title']:
        if display_params['numb_of_graphs'] <= (
                display_params['numb_max_of_graphs_per_fig']):
            figure_name = display_params['lay_title']
        else:
            figure_name = (display_params['lay_title'] +
                           ' (' + str(figure_number) + '/' +
                           str(display_params['numb_of_figs']) + ')')
        figure.canvas.set_window_title(figure_name)
        figure.suptitle(figure_name, fontsize=10,
                        fontweight='bold', y=0.99)

    figure.subplots_adjust(left=0.11, bottom=0.12,
                           right=0.9, top=0.9,
                           wspace=0.38, hspace=0.32)

    return figure


def build_new_graph(
        figure,
        figure_structure,
        graph_position,
        graph_layout,
        dataframe, data_c=None):
    """Builds a new matplotlib graph in the provided matplotlib
    figure thanks to the provided parameters

    Input:
    ------
    figure : matplotlib object
    figure_structure : tuple of 2 integers
    graph_position : integer
    graph_layout : nested object
    dataframe : pandas data frame
    data_c : pandas data frame for data to compare with
    """


    subplot = figure.add_subplot(*figure_structure, graph_position)
    
    if "x_label" in graph_layout:
        subplot.set_xlabel(graph_layout["x_label"])

    if "y_label" in graph_layout:
        subplot.set_ylabel(graph_layout["y_label"])

    if "title" in graph_layout:
        subplot.set_title(graph_layout["title"],
                           fontweight='bold')


    if graph_layout["x_var"] in dataframe.keys():

        for curve_it, curve_layout in enumerate(graph_layout["curves"]):

            if curve_layout["var"] in dataframe.keys():
                if "legend" in curve_layout:
                    curve_legend = curve_layout["legend"]
                else:
                    curve_legend = curve_layout["var"]
                #print(graph_layout["x_var"],curve_layout["var"] )

                if data_c is None:
                    
                    custom_style = custom_cycler_iterate(curve_it)

                    subplot.plot(dataframe[graph_layout["x_var"]],
                             dataframe[curve_layout["var"]], **custom_style,
                             label=curve_legend)


                else:

                    custom_style = custom_cycler_iterate(curve_it, compare=False)
                    custom_style_c = custom_cycler_iterate(curve_it, compare=True)
                    #print(custom_style, custom_style_c)

                    subplot.plot(dataframe[graph_layout["x_var"]],
                             dataframe[curve_layout["var"]], 
                            **custom_style,
                             label=curve_legend)

                    subplot.plot(data_c[graph_layout["x_var"]],
                             data_c[curve_layout["var"]], 
                             **custom_style_c,
                             label=curve_legend)

                             
    figure.tight_layout()
    #subplot.legend(bbox_to_anchor=(1.05, 1), loc = 9)
    subplot.legend(loc = 0)
   
def custom_cycler_iterate(index, compare=False):

    '''
    Returns a dictionary with keys and values in accordance to the Matplotlib
    syntax. The graph style includes a color from a list defined for
    colour-blind people by https://personal.sron.nl/~pault/,
    depending if the data is compared with other data.
    input: the index of the current plotted curve
    output: the dicionnary with the style for this curve:
        - color
        - linestyle
        - marker
        - markersize
        - markerfacecolor
    '''

    custom_style = {}
    custom_cycler = ['#4477AA', '#66CCEE', '#228833', 
                            '#CCBB44', '#EE6677',
                            '#AA3377', '#BBBBBB']
    custom_cycler_marker = ["o", "*", "D", "s",
                            "^", "v", "+"]
    if compare == False:

        ind_ = index%len(custom_cycler)
        custom_style['color'] = custom_cycler[ind_]
        custom_style['linestyle'] = '-'
        custom_style['marker'] = custom_cycler_marker[ind_]
        custom_style['markersize'] = 5    
        custom_style['markevery'] = 0.05 
        custom_style['markeredgewidth'] = 0.5
        #custom_style['markerfacecolor'] = None

    else:
        ind_ = index%len(custom_cycler)
        custom_style['color'] = custom_cycler[ind_]
        custom_style['linestyle'] = '--'
        custom_style['marker'] = custom_cycler_marker[ind_]
        custom_style['markersize'] = 5    
        custom_style['markevery'] = 0.05 
        custom_style['markeredgewidth'] = 0.5
        custom_style['markerfacecolor'] = 'white'
        
    if index > len(custom_cycler):
        print("WARNING!: More than 7 plots on one graph")
    
    return custom_style