"""
This module contains components that are common to several demo layouts.

"""
import dash_core_components as dcc
import dash_html_components as html
from plotly.subplots import make_subplots
import numpy as np

colors = {
    'background': 'SteelBlue',
    'text': 'White',
    'controls': '#DDDDDD',
    'buttons': 'Orange'
}



def app_parameter(label, appid, inputtype, value, size='20'):
    """
    A label and a Input control, as elements of a table row
    :param label: str, label to show in app layout
    :param appid:  str, label to identify user input within the app
    :param inputtype: str, type of input, either "text" or "number"
    :param value: initial value for this parameter
    :param size: str, size of input field
    :return:
    tuple, a label and a Input control, as html.Th elements to be included in a html.Tr table row
    """
    return html.Th(label), html.Th(dcc.Input(id=appid, type=inputtype, value=value, size=size))


def app_parameter_row(label, appid, inputtype, value, size='20'):
    """
    Table row with a label and a Input control
    :param label: str, label to show in app layout
    :param appid:  str, label to identify user input within the app
    :param inputtype: str, type of input, either "text" or "number"
    :param value: initial value for this parameter
    :param size: str, size of input field
    :return:
    a html.TR table row, with a label and a Input control
    """
    return html.Tr([
        *app_parameter(label, appid, inputtype, value, size)],
        style={'border':'3px dashed SteelBlue'}
    )


def app_choose_parameter(label, appid, list_of_options, value):
    """
    A label and a dropdown menu
    :param label: str, label to show in app layout
    :param appid: str, label to identify user input within the app
    :param list_of_options: list of str, available options to choose from
    :param value: initial value for this parameter
    :return:
    a html.TR table row, with a label and a Dropdown control
    """
    options = [{'label': x, 'value': x} for x in list_of_options]
    return html.Tr([
        html.Th(label),
        html.Th(dcc.Dropdown(id=appid, options=options, value=value), style={'width': '100%'})],
                   style={'border':'3px dashed SteelBlue'}
    )


def app_model_parameter(label, base_value, scen_value):
    """
    A label and two Input controls
    :param label: str, label to show in app layout
    :param base_value: initial baseline value for this parameter
    :param scen_value: initial alternative value for this parameter
    :return:
    a html.TR table row, with a label, an Input control for baseline and a Input control for alternative
    """
    txt = html.Th(label)
    param1 = html.Th(dcc.Input(id='base_' + label, type='text', value=base_value, size='10'))
    param2 = html.Th(dcc.Input(id='scen_' + label, type='text', value=scen_value, size='10'))
    return html.Tr(
        [txt, param1, param2],
        style={'border':'3px dashed SteelBlue'}
    )


def app_one_option(label, appid, list_of_labels, list_of_values, value):
    """
    A label and single choice options, inline
    :param label: str, label to show in app layout
    :param appid: str, label to identify user input within the app
    :param list_of_labels: list of str, available options to show in app
    :param list_of_values: list of str, available options to choose from
    :param value: initial value for this parameter
    :return:
    a html.TR table row, with a label, an RadioItems control
    """

    options = [{'label': x, 'value': y} for x, y in zip(list_of_labels, list_of_values)]
    return html.Tr([
        html.Th(label),
        html.Th(dcc.RadioItems(
            id=appid,
            options=options,
            value=value,
            labelStyle={'display': 'inline-block'}),
            style={'width': '100%'})],
        style={'border':'3px dashed SteelBlue'}
    )


def app_table_headers(labels):
    """
    Headers for table of Inputs
    :param labels: list of str, headers to show on top of inputs
    :return:
    a html.TR table row, with a list of headers
    """
    return html.Tr(
        [html.Th(label) for label in labels],
        style={'border':'3px dashed SteelBlue'}
    )


editable_cell_format = {
    'backgroundColor': 'rgb(75, 75, 75)',
    'color': 'white',
    'fontWeight': 'bold',
    'fontSize': 18
}

header_cell_format = {
    'backgroundColor': 'rgb(50, 50, 50)',
    'color': 'white',
    'fontWeight': 'bold',
    'fontSize': 18
}

def add_plot(fig, existing, **kwargs):
    """
    Add a plotly figure as traces to another figure

    :param fig: a plotly.Figure obtained with make_plots, where to insert next figure
    :param existing: a plotly.Figure to be added as subplot to the figure above
    :param kwargs: parameters passed to method fig.add_trace
    :return: None, updates fig in place
    """
    for ff in existing.select_traces():
        fig.add_trace(ff, **kwargs)


def merge_plots(figures, cols=1, shared_xaxes=True, shared_yaxes=True, subplot_titles=None, title_text=None):
    """
    Merges several plotly.Figures into a single figure (as subplots)

    :param figures: the plotly.Figures to be merged together
    :param cols: number of columns for resulting subplots
    :param shared_xaxes: True if every column must have same x scale
    :param shared_yaxes: True if every row must have same y scale
    :param subplot_titles: a collection of strings to be used as titles for the subplots
    :param title_text: a string to be used as title to the merged figure
    :return:
        a plotly.Figure
    """
    rows = int(np.ceil(len(figures)/cols))
    bigfig = make_subplots(rows, cols, subplot_titles=subplot_titles,shared_xaxes=shared_xaxes, shared_yaxes=shared_yaxes)
    for n, fig in enumerate(figures):
        add_plot(bigfig, fig, row=n // cols + 1, col=n % cols + 1)
    bigfig.update_layout(title_text=title_text, showlegend=False)
    return bigfig

def make_top_banner(title):
    logo = html.Div(
        style={'textAlign': 'center', 'color': colors['controls'], 'width': '5%', 'display': 'inline-block'},
        children=[
            html.Img(src='https://randall-romero.github.io/econometria/_static/r2-logo.png',
                     width='100%',
                     style={'margin-left': '0px',
                            'margin-top': '2px',
                            'margin-bottom': '2px'
                            })])
    header = html.Div(
        style={'textAlign': 'center', 'color': colors['controls'], 'width': '93%', 'display': 'inline-block'},
        children=[
            html.H2(id='title',
                    children=title,
                    style={'textAlign': 'center', 'color': colors['text']})])

    return logo, header

def make_bottom_banner(name_of_demo, width=25):
    footer = html.Div(
        style={'textAlign': 'center', 'color': colors['controls'], 'width': '100%', 'display': 'inline-block'},
        children=[
            html.Div(style={'textAlign': 'center', 'color': colors['controls'], 'width': f'{width}%', 'display': 'inline-block'},
                     children=[html.P(name_of_demo,
                                      style={'textAlign': 'center', 'color': colors['text'] ,'marginTop' :10})]),
            html.Div(style={'textAlign': 'left', 'color': colors['controls'], 'width': f'{100-width}%', 'display': 'inline-block'},
                     children=[html.A(children='Randall Romero Aguilar',
                                      href='http://randall-romero.com',
                                      style={'textAlign': 'left', 'color': colors['text'] ,'marginBottom' :20})])
        ]
    )

    return footer
