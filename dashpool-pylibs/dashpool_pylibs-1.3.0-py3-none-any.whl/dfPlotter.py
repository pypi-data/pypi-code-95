import numpy as _np
import pandas as _pd
from scipy import stats as _stats

import dash_core_components as _dcc
import dash_html_components as _html
import dash_bootstrap_components as _dbc


from dash.dependencies import Input as _Input
from dash.dependencies import Output as _Output
from dash.dependencies import State as _State

import json as _json
import dash as _dash
import plotly.express as _px
import plotly.graph_objects as _go
import plotly.io as _pio
import base64 as _base64

import sys


from dash.exceptions import PreventUpdate


class DfPlotter:

    """
    initialize the plotter with the dataframe to work with
    """

    def __init__(self, df, name, publicCols=None, title=None, init_cols=False):

        # assume publicCols is not maintained yet and skip it
        if(publicCols is not None and len(publicCols) == 0):
            publicCols = None

        self.df = df
        self._name = name

        # the title can differ from the name
        self._title = name
        if title:
            self._title = title

        # if columns should be  filled at startup
        self._init_cols = init_cols

        # analyze data for numerical and categorical variables
        # create a list of possible continous values
        self.numerical_Cols = [i for i in self.df.columns if self.df[i].dtype in (
            _np.float32,  _np.float64, _np.int32,  _np.int64) and (publicCols is None or i in publicCols)]
        self.numerical_Min = {}
        self.numerical_Max = {}

        for n in self.numerical_Cols:
            self.numerical_Min[n] = _np.min(self.df[n].dropna())
            self.numerical_Max[n] = _np.max(self.df[n].dropna())

        # create a list of categorical columns
        self.categorical_Cols = [i for i in self.df.columns if not self.df[i].dtype in (
            _np.float32,  _np.float64, _np.int32,  _np.int64) and (publicCols is None or i in publicCols)]
        self.category_Dict = {}

        for n in self.categorical_Cols:
            types = _np.unique(self.df[n].dropna())
            sortedList = list(types)
            sortedList.sort()
            self.category_Dict[n] = sortedList

        # all columns
        self.all_Cols = [i for i in self.df.columns if (
            publicCols is None or i in publicCols)]

        # define a variable to change the filter columns
        self.filter_Cols = self.all_Cols

        # the input and state variables can be used for a callback
        self.Input = None
        self.State = None

        # empty dataframe dummy
        self.dummyData = _pd.DataFrame([None])

    def get_layout(self):
        mainCard = [
            _dcc.Dropdown(
                id=self._name+'-plotTypeDropdown',
                options=[{'label': 'Scatter', 'value': 'scatter'},
                         {'label': 'Scatter Matrix', 'value': 'scatter_matrix'},
                         {'label': 'Density Contour', 'value': 'density_contour'},
                         {'label': 'Density Heatmap', 'value': 'density_heatmap'},
                         {'label': 'Box', 'value': 'box'},
                         {'label': 'Violin', 'value': 'violin'},
                         {'label': 'Bar', 'value': 'bar'},
                         {'label': 'Bar Count', 'value': 'bar_count'},
                         {'label': 'Histogram', 'value': 'histogram'},
                         {'label': 'Line Histogram', 'value': 'histogram_line'},
                         {'label': 'Probability Plot', 'value': 'probability'}
                         ],
                placeholder="PlotType",
                value="scatter",
                clearable=False
            ),

            _html.Label(
                "Axes", className="simpleLabel"),

            _html.Div([
                _dcc.Dropdown(
                    id=self._name+'-multiAxisDropdown',
                    multi=True,
                    placeholder="multi-axes"
                )], id=self._name+'-multiAxisDiv'),


            _html.Div([
                _dcc.Dropdown(
                    id=self._name+'-xAxisDropdown',
                    placeholder="x-axis"
                ),

                _dcc.Dropdown(
                    id=self._name+'-yAxisDropdown',
                    placeholder="y-axis"
                ),

            ], id=self._name+'-normalAxisDiv'),

            _dcc.Dropdown(
                id=self._name+'-colorAxisDropdown',
                placeholder="color-axis"
            ),

            _html.Div([
                _html.Button(
                    "Update Plot",
                    id=self._name+"-update-plot",
                    className="btn btn-outline-primary w-100"
                )
            ])

        ]

        extraCard = [

            _html.Label(
                "Errorbars", className="simpleLabel"),
            _dcc.Dropdown(
                id=self._name+'-errorxAxisDropdown',
                placeholder="x-axis error"
            ),

            _dcc.Dropdown(
                id=self._name+'-erroryAxisDropdown',
                placeholder="y-axis error"
            ),

            _html.Label(
                "Scaling", className="simpleLabel"),
            _dbc.Checklist(
                options=[
                    {"label": "log-x", "value": "x"},
                    {"label": "log-y", "value": "y"},
                ],
                value=[],
                id=self._name+'-logSwitches',
                inline=True,
                switch=True,
                style={"text-align": "center"}
            ),





            _html.Label(
                "Categorical", className="simpleLabel"),
            _dbc.Checklist(
                options=[
                    {"label": "cat-x", "value": "x"},
                    {"label": "cat-y", "value": "y"},
                ],
                value=["x", "y"],
                id=self._name+'-catSwitches',
                inline=True,
                switch=True,
                style={"text-align": "center"}
            ),



            _html.Label(
                "Box sample points", className="simpleLabel"),
            _dcc.Dropdown(
                id=self._name+'-pointsDropdown',
                options=[
                    {'label': 'all', 'value': 'all'},
                    {'label': 'outliers', 'value': 'outliers'},
                    {'label': 'suspected and outliers',
                        'value': 'suspectedoutliers'},
                    {'label': 'none', 'value': 'False'}
                ],
                placeholder="sample points",
                value="outliers",
                clearable=False
            ),
            _html.Label(
                "Box Configuration", className="simpleLabel"),
            _dcc.Dropdown(
                id=self._name+'-boxDropdown',
                options=[
                    {'label': 'stack', 'value': 'stack'},
                    {'label': 'group', 'value': 'group'},
                    {'label': 'overlay', 'value': 'overlay'},
                ],
                placeholder="box mode",
                value='overlay',
                clearable=False
            ),
            _dbc.Checklist(
                options=[
                    {"label": "notched", "value": "notched"},
                    {"label": "violin+box", "value": "box"},
                ],
                value=[],
                id=self._name+'-boxOptions',
                inline=True,
                switch=True,
                style={"text-align": "center"}
            ),



            _html.Label(
                "Edge Plots", className="simpleLabel"),
            _dcc.Dropdown(
                id=self._name+'-marginalXDropdown',
                options=[{'label': 'Histogram', 'value': 'histogram'},
                         {'label': 'Box', 'value': 'box'},
                         {'label': 'Violin', 'value': 'violin'},
                         {'label': 'Samples', 'value': 'rug'}
                         ],
                placeholder="x-axis type"
            ),

            _dcc.Dropdown(
                id=self._name+'-marginalYDropdown',
                options=[{'label': 'Histogram', 'value': 'histogram'},
                         {'label': 'Box', 'value': 'box'},
                         {'label': 'Violin', 'value': 'violin'},
                         {'label': 'Samples', 'value': 'rug'}
                         ],
                placeholder="y-axis type"
            ),


            _html.Label("Binning in x", className="simpleLabel"),
            _html.Div([
                _dcc.Slider(
                    id=self._name+'-nbinsxSlider',
                    min=2,
                    max=250,
                    step=1,
                    value=40,
                    marks={x: str(x) for x in range(20, 250, 20)},
                )], style={"margin": "4px", "width": "95%"}),
            _html.Label("Binning in y", className="simpleLabel"),
            _html.Div([
                _dcc.Slider(
                    id=self._name+'-nbinsySlider',
                    min=2,
                    max=250,
                    step=1,
                    value=40,
                    marks={x: str(x) for x in range(20, 250, 20)},
                )], style={"margin": "4px", "width": "95%"}),


            _html.Label("Opacity", className="simpleLabel"),
            _html.Div([
                _dcc.Slider(
                    id=self._name+'-opacity',
                    min=0,
                    max=1,
                    step=0.01,
                    value=0.7,
                    marks={x*0.01: str(x) + "%" for x in range(10, 100, 10)},
                )], style={"margin": "4px", "width": "95%"}),

            _html.Label("Histogram options", className="simpleLabel"),
            _dcc.Dropdown(
                id=self._name+'-histBarmode',
                options=[{'label': 'Relative', 'value': 'relative'},
                         {'label': 'Overlay ', 'value': 'overlay'}
                         ],
                placeholder="barmode"
            ),
            _dcc.Dropdown(
                id=self._name+'-histnorm',
                options=[{'label': 'absolute ', 'value': None},
                         {'label': 'probability density',
                             'value': 'probability density'},
                         {'label': 'percent ', 'value': 'percent'}
                         ],
                placeholder="histnorm"
            ),
            _dbc.Checklist(
                options=[
                    {"label": "cumulative", "value": "cumulative"}
                ],
                value=[],
                id=self._name+'-histogramOptions',
                inline=True,
                switch=True,
                style={"text-align": "center"}
            ),



            _html.Label(
                "Tredline", className="simpleLabel"),
            _dcc.Dropdown(
                id=self._name+'-trendlineDropdown',
                options=[{'label': 'Least squares', 'value': 'ols'},
                         {'label': 'LOWESS ', 'value': 'lowess'}
                         ],
                placeholder="typ"
            ),


            _html.Label(
                "Grouping grid", className="simpleLabel"),
            _dcc.Dropdown(
                id=self._name+'-facet-colDropdown',
                placeholder="columns"
            ),
            _dcc.Dropdown(
                id=self._name+'-facet-rowDropdown',
                placeholder="rows"
            ),
            _html.Label("Cols per row", className="simpleLabel"),
            _html.Div([
                _dcc.Slider(
                    id=self._name+'-facetColWrapSlider',
                    min=1,
                    max=10,
                    step=1,
                    value=1,
                    marks={x: str(x) for x in range(1, 11)},
                )], style={"margin": "4px", "width": "95%"}),

            _dbc.Checklist(
                options=[
                    {"label": "independent-x", "value": "x"},
                    {"label": "independent-y", "value": "y"},
                ],
                value=[],
                id=self._name+'-independentSwitches',
                inline=True,
                switch=True,
                style={"text-align": "center"}
            ),





            _dbc.Checklist(
                options=[
                    {"label": "render as png", "value": "png"}
                ],
                value=[],
                id=self._name+'-renderOptions',
                inline=True,
                switch=True,
                style={"text-align": "center"}
            ),


            _dcc.Textarea(
                id=self._name+'-state',
                hidden="True"
            )

        ]

        labelsCard = [

            _html.Label(
                "Title", className="simpleLabel"),
            _dbc.Input(
                placeholder='optional title',
                id=self._name+'-title',
                type='text',
                value=''
            ),
            _html.Label(
                "Hover text", className="simpleLabel"),
            _dcc.Dropdown(
                id=self._name+'-hoverNameDropdown',
                placeholder="label"
            ),
            _dcc.Dropdown(
                id=self._name+'-hoverDataDropdown',
                placeholder="data",
                multi=True
            ),
            _html.Label("Replace label", className="simpleLabel"),
            _dcc.Dropdown(
                id=self._name+'-replaceNameOld',
                placeholder="old name"
            ),
            _dbc.Input(
                placeholder='new name',
                type='text',
                value='',
                id=self._name+'-replaceNameNew',
            ),
            _html.Div([
                _html.Button(
                    "Add",
                    id=self._name+"-replaceAdd",
                    className="btn btn-outline-light"
                ),
                _html.Button(
                    "Remove",
                    id=self._name+"-replaceRemove",
                    className="btn btn-outline-light"
                ),
                _html.Button(
                    "Clear",
                    id=self._name+"-replaceClear",
                    className="btn btn-outline-light"
                )],
                className="btn-group special btn-group-sm mt-1 ", role="group"
            ),
            _dbc.Card(_dbc.CardBody([
                _dcc.Markdown(
                    id=self._name+'-replaceDesc',
                    className="lightAndSmall"
                )
            ]), className="mt-1", style={"height": "100px", "overflow-y": "scroll"}),
            _dcc.Textarea(
                id=self._name+'-replaceState',
                hidden="True"
            )


        ]

        layout = _html.Div([

            _dbc.Card(_dbc.CardBody([
                _html.Label(
                    self._title, className="highlightLabel card-collaps-label"),
                *mainCard
            ])),


            _dbc.Card(_dbc.CardBody([
                _html.Label(
                    self._title+" Addons", className="highlightLabel card-collaps-label"),
                *extraCard
            ]),
                className="card-collapsed"
            ),


            _dbc.Card(_dbc.CardBody([
                _html.Label(
                    self._title+" Labels", className="highlightLabel card-collaps-label"),
                *labelsCard
            ]),
                className="card-collapsed"
            ),

            _dcc.Store(id=self._name+'-initial-state'),
            _dcc.Store(id=self._name+'-init-cols')

        ])

        self.Input = _Input(self._name+'-state', 'value')
        self.State = _State(self._name+'-state', 'value')
        self.InitialState = _Output(self._name+'-initial-state', 'data')
        self.InitCols = _Output(self._name+'-init-cols', 'data')
        return layout

    """
    register the plot optionis callbacks to the dashapp
    """

    def register_callbacks(self, dashapp):

        # fill the options if people start to search for
        def fill_with_all_Cols(search_value, initial_data, oldOptions):
            if oldOptions:
                raise PreventUpdate

            # check if the update is triggered by the initial_state
            ctx = _dash.callback_context
            if initial_data != None and ctx.triggered and  \
                    ctx.triggered[0]['prop_id'] == self._name+"-initial-state.data":
                input = _json.loads(initial_data)
                if "params" in input:
                    ctx = _dash.callback_context
                    dropdown = list(ctx.states.keys())[0]
                    params = input["params"]

                    if ("multiAxisDropdown" in dropdown and "dimensions" in params) or \
                        ("xAxisDropdown" in dropdown and "x" in params) or \
                        ("yAxisDropdown" in dropdown and "y" in params) or \
                        ("colorAxisDropdown" in dropdown and "color" in params) or \
                        ("errorxAxisDropdown" in dropdown and "error_x" in params) or \
                        ("erroryAxisDropdown" in dropdown and "error_y" in params) or \
                            ("hoverDataDropdown" in dropdown and "hover_data" in params):
                        return [{'label': d, 'value': d} for d in self.all_Cols]

                    raise PreventUpdate
            if not search_value and not self._init_cols:
                raise PreventUpdate
            return [{'label': d, 'value': d} for d in self.all_Cols]

        # apply the fill cols as callback
        for component in ['multiAxisDropdown',
                          'xAxisDropdown',
                          'yAxisDropdown',
                          'colorAxisDropdown',
                          'errorxAxisDropdown',
                          'erroryAxisDropdown',
                          'hoverDataDropdown'
                          ]:
            dashapp.callback(
                _Output(self._name+'-'+component, 'options'),
                [_Input(self._name+'-'+component, 'search_value'),
                 _Input(self._name+'-initial-state', 'data')
                 ],
                [_State(self._name+'-'+component, 'options')]
            )(fill_with_all_Cols)

        def fill_with_categorical_Cols(search_value,  initial_data, oldOptions):

            if oldOptions:
                raise PreventUpdate

            # check if the update is triggered by the initial_state
            ctx = _dash.callback_context
            if initial_data != None and ctx.triggered and  \
                    ctx.triggered[0]['prop_id'] == self._name+"-initial-state.data":
                input = _json.loads(initial_data)
                if "params" in input:
                    ctx = _dash.callback_context
                    dropdown = list(ctx.states.keys())[0]
                    params = input["params"]

                    if ("facet-colDropdown" in dropdown and "facet_col" in params) or \
                        ("facet-rowDropdown" in dropdown and "facet_row" in params) or \
                            ("hoverNameDropdown" in dropdown and "hover_name" in params):
                        return [{'label': d, 'value': d} for d in self.all_Cols]

                    raise PreventUpdate

            if not search_value and not self._init_cols:
                raise PreventUpdate
            return [{'label': d, 'value': d} for d in self.categorical_Cols]
        for component in ['facet-colDropdown', 'facet-rowDropdown', 'hoverNameDropdown']:
            dashapp.callback(
                _Output(self._name+'-'+component, 'options'),
                [_Input(self._name+'-'+component, 'search_value'),
                 _Input(self._name+'-initial-state', 'data')
                 ],
                [_State(self._name+'-'+component, 'options')]
            )(fill_with_categorical_Cols)

        def fill_with_all_Cols_and_count(search_value, oldOptions):
            if not search_value:
                raise PreventUpdate
            if oldOptions:
                raise PreventUpdate
            output = [{'label': d, 'value': d} for d in self.all_Cols]
            output.append({'label': 'count', 'value': 'count'})
            return output
        for component in ['replaceNameOld']:
            dashapp.callback(
                _Output(self._name+'-'+component, 'options'),
                [_Input(self._name+'-'+component, 'search_value')],
                [_State(self._name+'-'+component, 'options')]
            )(fill_with_all_Cols_and_count)

        # initialize the plotter component with data from the initial-state
        @dashapp.callback([
            _Output(self._name+'-plotTypeDropdown', 'value'),
            _Output(self._name+'-multiAxisDropdown', 'value'),
            _Output(self._name+'-xAxisDropdown', 'value'),
            _Output(self._name+'-yAxisDropdown', 'value'),
            _Output(self._name+'-errorxAxisDropdown', 'value'),
            _Output(self._name+'-erroryAxisDropdown', 'value'),
            _Output(self._name+'-colorAxisDropdown', 'value'),
            _Output(self._name+'-marginalXDropdown', 'value'),
            _Output(self._name+'-marginalYDropdown', 'value'),
            _Output(self._name+'-trendlineDropdown', 'value'),
            _Output(self._name+'-facet-colDropdown', 'value'),
            _Output(self._name+'-facet-rowDropdown', 'value'),
            _Output(self._name+'-nbinsxSlider', 'value'),
            _Output(self._name+'-nbinsySlider', 'value'),
            _Output(self._name+'-logSwitches', 'value'),
            _Output(self._name+'-catSwitches', 'value'),
            _Output(self._name+'-hoverNameDropdown', 'value'),
            _Output(self._name+'-hoverDataDropdown', 'value'),

            _Output(self._name+'-pointsDropdown', 'value'),
            _Output(self._name+'-boxDropdown', 'value'),
            _Output(self._name+'-boxOptions', 'value'),

            _Output(self._name+'-opacity', 'value'),
            _Output(self._name+'-histBarmode', 'value'),
            _Output(self._name+'-histnorm', 'value'),
            _Output(self._name+'-histogramOptions', 'value'),

            _Output(self._name+'-title', 'value'),
            _Output(self._name+'-renderOptions', 'value'),

            _Output(self._name+'-independentSwitches', 'value'),
            _Output(self._name+'-facetColWrapSlider', 'value')

        ], [
            _Input(self._name+'-initial-state', 'data')
        ]
        )
        def setup(initial_data):
            params = {}
            title = None
            input = None
            plotType = "scatter"

            if initial_data != None:
                input = _json.loads(initial_data)
                plotType = input.get("type", "scatter")
                params = input.get("params", {})
                title = input.get("title", None)

            logOptions = []
            if("log_x" in params and params["log_x"]):
                logOptions.append("x")
            if("log_y" in params and params["log_y"]):
                logOptions.append("y")

            catOptions = ['x', 'y']
            if "cat_x" in params and not params["cat_x"]:
                catOptions.remove("x")
            if "cat_y" in params and not params["cat_y"]:
                catOptions.remove("y")

            indepOptions = []
            if("indep_x" in params and params["indep_x"]):
                indepOptions.append("x")
            if("indep_y" in params and params["indep_y"]):
                indepOptions.append("y")

            points = "outliers"
            if ("points" in params):
                if params["points"] == False:
                    points = "False"
                else:
                    points = params["points"]

            boxOptions = []
            if("box" in params and params["box"]):
                boxOptions.append("box")
            if("notched" in params and params["notched"]):
                boxOptions.append("notched")

            histogramOptions = []
            if("cumulative" in params and params["cumulative"]):
                histogramOptions.append("cumulative")

            renderOptions = []
            if input is not None and "render" in input:
                renderOptions = input["render"]

            return plotType, params.get("dimensions"), \
                params.get("x"), params.get("y"), \
                params.get("error_x"), params.get("error_y"), \
                params.get("color"), \
                params.get("marginal_x", params.get("marginal")), params.get("marginal_y"), \
                params.get("trendline"), \
                params.get("facet_col"), params.get("facet_row"), \
                params.get("nbinsx", params.get("nbins", 20)), params.get("nbinsy", 20), \
                logOptions, catOptions, \
                params.get("hover_name"), params.get("hover_data"), \
                points, \
                params.get("boxmode", params.get("barmode", "overlay")), \
                boxOptions, \
                params.get("opacity", 0.7), \
                params.get("barmode"), params.get("histnorm"), \
                histogramOptions, \
                title, \
                renderOptions, \
                indepOptions, params.get("facet_col_wrap", 1)

        # replace label add delete ... handling
        """
        update the filter content once a button is pressed
        """
        @dashapp.callback(
            [
                _Output(self._name+'-replaceDesc', 'children'),
                _Output(self._name+'-replaceState', 'value')
            ],
            [
                _Input(self._name+'-replaceAdd', 'n_clicks'),
                _Input(self._name+'-replaceRemove', 'n_clicks'),
                _Input(self._name+'-replaceClear', 'n_clicks'),

                _Input(self._name+'-initial-state', 'data')
            ],
            [
                _State(self._name+'-replaceState', 'value'),
                _State(self._name+'-replaceNameOld', 'value'),
                _State(self._name+'-replaceNameNew', 'value')
            ]
        )
        def update_replace_config(add_clicks, remove_clicks, clear_clicks,

                                  initial_state,

                                  replace_state_string,
                                  oldName,
                                  newName
                                  ):

            ctx = _dash.callback_context

            # check if the update is triggered by the initial_state
            if ctx.triggered:
                if ctx.triggered[0]['prop_id'] == self._name+"-initial-state.data":
                    if initial_state != None and len(initial_state) > 2:
                        parsed = _json.loads(initial_state)["params"]
                        if "labels" in parsed:
                            replace_state = parsed["labels"]
                        else:
                            replace_state = ""

                        listOutput = ""
                        for f in replace_state:
                            listOutput = listOutput + \
                                "{0} **-->** {1}  \n".format(f,
                                                             replace_state[f])

                        return listOutput, _json.dumps(replace_state)
                    else:
                        return "", "{}"

            if ctx.triggered:
                button_id = ctx.triggered[0]['prop_id'].split('.')[0]
                if button_id == self._name+"-replaceClear":
                    replace_state = None
                    return "", _json.dumps(replace_state)

            if oldName == None or newName == None or newName == "":
                return "", "{}"
                #raise Exception("no variable name")

            if replace_state_string is not None and replace_state_string != "" and replace_state_string != "null":
                replace_state = {f: v for f, v in _json.loads(
                    replace_state_string).items() if f != oldName}
            else:
                replace_state = {}

            if ctx.triggered:
                if button_id == self._name+"-replaceAdd":
                    replace_state[oldName] = newName

            listOutput = ""
            for f in replace_state:
                listOutput = listOutput + \
                    "{0} **-->** {1}  \n".format(f, replace_state[f])

            return listOutput, _json.dumps(replace_state)

        # update the visibility of the options in the main plot card
        # other cards always show all features, even if they are not possible
        @dashapp.callback(
            [
                _Output(self._name+'-multiAxisDiv', 'style'),
                _Output(self._name+'-normalAxisDiv', 'style')
            ],
            [
                _Input(self._name+'-plotTypeDropdown', 'value')
            ]
        )
        def update_visibility(plotType):

            if plotType == "scatter_matrix":
                return {}, {'display': 'none'}
            else:
                return {'display': 'none'}, {}

        # update the plot config json
        @dashapp.callback(
            _Output(self._name+'-state', 'value'),
            [
                _Input(self._name+'-update-plot', 'n_clicks'),
                _Input(self._name+'-initial-state', 'data')
            ],
            [
                _State(self._name+'-plotTypeDropdown', 'value'),
                _State(self._name+'-multiAxisDropdown', 'value'),
                _State(self._name+'-xAxisDropdown', 'value'),
                _State(self._name+'-yAxisDropdown', 'value'),
                _State(self._name+'-errorxAxisDropdown', 'value'),
                _State(self._name+'-erroryAxisDropdown', 'value'),
                _State(self._name+'-colorAxisDropdown', 'value'),
                _State(self._name+'-marginalXDropdown', 'value'),
                _State(self._name+'-marginalYDropdown', 'value'),
                _State(self._name+'-trendlineDropdown', 'value'),
                _State(self._name+'-facet-colDropdown', 'value'),
                _State(self._name+'-facet-rowDropdown', 'value'),
                _State(self._name+'-nbinsxSlider', 'value'),
                _State(self._name+'-nbinsySlider', 'value'),
                _State(self._name+'-logSwitches', 'value'),
                _State(self._name+'-catSwitches', 'value'),
                _State(self._name+'-hoverNameDropdown', 'value'),
                _State(self._name+'-hoverDataDropdown', 'value'),

                _State(self._name+'-pointsDropdown', 'value'),
                _State(self._name+'-boxDropdown', 'value'),
                _State(self._name+'-boxOptions', 'value'),

                _State(self._name+'-opacity', 'value'),
                _State(self._name+'-histBarmode', 'value'),
                _State(self._name+'-histnorm', 'value'),
                _State(self._name+'-histogramOptions', 'value'),

                _State(self._name+'-replaceState', 'value'),
                _State(self._name+'-title', 'value'),
                _State(self._name+'-renderOptions', 'value'),

                _State(self._name+'-independentSwitches', 'value'),
                _State(self._name+'-facetColWrapSlider', 'value')
            ]
        )
        def update_plot_content(clicks,
                                initial_state,

                                plotType,
                                multiAxis,
                                xAxis,
                                yAxis,
                                error_x,
                                error_y,
                                colorAxis,
                                marginalX,
                                marginalY,
                                trendline,
                                facetCol,
                                facetRow,
                                nbinsx,
                                nbinsy,
                                logOptions,
                                catOptions,
                                hover_name,
                                hover_data,
                                points,
                                boxmode,
                                boxOptions,
                                opacity,
                                histBarmode,
                                histnorm,
                                histogramOptions,

                                replace_state_string,
                                title,
                                renderOptions,

                                indepOptions,
                                facetColWrap

                                ):

            ctx = _dash.callback_context

            # check if the update is triggered by the initial_state
            if ctx.triggered:
                if ctx.triggered[0]['prop_id'] == self._name+"-initial-state.data":
                    return(initial_state)

            output = {}
            output["title"] = title
            output["render"] = renderOptions
            output["type"] = plotType
            output["params"] = {}
            if xAxis and xAxis != None and not plotType in ["scatter_matrix"]:
                if xAxis in self.categorical_Cols or not plotType in ["box", "violin", "bar", "bar_count"]:
                    output["params"]["x"] = xAxis
            if yAxis and yAxis != None and not plotType in ["scatter_matrix"]:
                output["params"]["y"] = yAxis

            if error_x and error_x != None and plotType in ["scatter"]:
                output["params"]["error_x"] = error_x
            if error_y and error_y != None:
                output["params"]["error_y"] = error_y

            if multiAxis and multiAxis != None and len(multiAxis) > 0 and plotType in ["scatter_matrix"]:
                output["params"]["dimensions"] = multiAxis
            if colorAxis and colorAxis != None and not plotType in ["density_heatmap"]:
                output["params"]["color"] = colorAxis
            if marginalX and marginalX != None and plotType in ["scatter", "density_contour", "density_heatmap"]:
                output["params"]["marginal_x"] = marginalX
            if marginalY and marginalY != None and plotType in ["scatter", "density_contour", "density_heatmap"]:
                output["params"]["marginal_y"] = marginalY
            if marginalX and marginalX != None and plotType in ["histogram"]:
                output["params"]["marginal"] = marginalX
            if trendline and trendline != None and not plotType in ["scatter_matrix", "density_heatmap", "box", "violin", "bar", "bar_count"]:
                output["params"]["trendline"] = trendline
            if facetCol and facetCol != None:
                output["params"]["facet_col"] = facetCol
                if facetColWrap > 1:
                    output["params"]["facet_col_wrap"] = facetColWrap
            if facetRow and facetRow != None:
                output["params"]["facet_row"] = facetRow
            if hover_name and hover_name != None and not plotType in ["bar_count"]:
                output["params"]["hover_name"] = hover_name
            if hover_data and hover_data != None and not plotType in ["bar_count"]:
                output["params"]["hover_data"] = hover_data

            if points and points != None and plotType in ["box", "violin"]:
                if points == 'False':
                    output["params"]["points"] = False
                else:
                    output["params"]["points"] = points
            if boxmode and boxmode != None:
                if plotType == "box":
                    if boxmode == "stack":
                        output["params"]["boxmode"] = "overlay"
                    else:
                        output["params"]["boxmode"] = boxmode
                if plotType == "violin":
                    if boxmode == "stack":
                        output["params"]["violinmode"] = "overlay"
                    else:
                        output["params"]["violinmode"] = boxmode
                if plotType == "bar" or plotType == "bar_count":
                    output["params"]["barmode"] = boxmode

            if plotType == "violin" and "box" in boxOptions:
                output["params"]["box"] = True
            if plotType == "box" and "notched" in boxOptions:
                output["params"]["notched"] = True

            if plotType in ['scatter', 'density_contour', 'density_heatmap', 'bar', 'area', 'histogram']:
                if "x" in logOptions:
                    output["params"]["log_x"] = True
                if "y" in logOptions:
                    output["params"]["log_y"] = True

            if "x" in catOptions:
                output["params"]["cat_x"] = True
            if "y" in catOptions:
                output["params"]["cat_y"] = True

            if "x" in indepOptions:
                output["params"]["indep_x"] = True
            if "y" in indepOptions:
                output["params"]["indep_y"] = True

            if plotType in ['density_heatmap']:
                output["params"]["color_continuous_scale"] = "oranges"

            if plotType in ['scatter'] and not (
                (error_x and error_x != None) or (error_y and error_y != None)
            ):
                output["params"]["render_mode"] = "webgl"

            if plotType in ["density_heatmap", "density_contour"]:
                output["params"]["nbinsx"] = nbinsx
                output["params"]["nbinsy"] = nbinsy
            if plotType in ["histogram", "histogram_line"]:
                output["params"]["nbins"] = nbinsx

            if plotType in ["histogram", "bar", "scatter", "scatter_matrix"]:
                output["params"]["opacity"] = opacity

            if "cumulative" in histogramOptions and plotType in ["histogram", "histogram_line"]:
                output["params"]["cumulative"] = True

            if histBarmode and plotType in ["histogram", "histogram_line"]:
                output["params"]["barmode"] = histBarmode
            if histnorm and plotType in ["histogram", "histogram_line"]:
                output["params"]["histnorm"] = histnorm

            if replace_state_string is not None and replace_state_string != "" and replace_state_string != "null":
                labels = _json.loads(replace_state_string)
                output["params"]["labels"] = labels

            return _json.dumps(output)

    # create the plot output
    def getPlot(self, inputDataFrame, plotConfig):

        errorResult = "Empty plot"

        try:
            # check if filter defined
            if plotConfig != None:

                # output figure
                fig = None

                plotConfigData = plotConfig
                # json parse the filter config if needed
                if isinstance(plotConfig, str):
                    plotConfigData = _json.loads(plotConfig)

                # don't try to hard if we have no params
                if not "params" in plotConfigData:
                    return _px.scatter(self.dummyData, title=errorResult)

                # also json parse the nested params, if needed
                if isinstance(plotConfigData["params"], str):
                    plotConfigData["params"] = _json.loads(
                        plotConfigData["params"])

                # don't try too hard, if there is no plot axis
                if not("x" in plotConfigData["params"] or "y" in plotConfigData["params"] or "dimensions" in plotConfigData["params"]):
                    return _px.scatter(self.dummyData, title=errorResult)

                # if we want to force an axis as categorical
                markCatX = False
                markCatY = False
                if "cat_x" in plotConfigData["params"]:
                    markCatX = True
                    del plotConfigData["params"]["cat_x"]
                if "cat_y" in plotConfigData["params"]:
                    markCatY = True
                    del plotConfigData["params"]["cat_y"]

                # if we have cols and rows, we want to make independent
                makeIndepX = False
                makeIndepY = False
                if "indep_x" in plotConfigData["params"]:
                    makeIndepX = True
                    del plotConfigData["params"]["indep_x"]
                if "indep_y" in plotConfigData["params"]:
                    makeIndepY = True
                    del plotConfigData["params"]["indep_y"]


                # add a sort command for categorical x columns
                if "x" in plotConfigData["params"] and plotConfigData["params"]["x"] in self.categorical_Cols and markCatX:
                    if not "category_orders" in plotConfigData["params"]:
                        plotConfigData["params"]["category_orders"] = {}
                    plotConfigData["params"]["category_orders"][plotConfigData["params"]
                                                                ["x"]] = self.category_Dict[plotConfigData["params"]["x"]]

                # add a sort command for categorical y columns
                if "y" in plotConfigData["params"] and plotConfigData["params"]["y"] in self.categorical_Cols and markCatY:
                    if not "category_orders" in plotConfigData["params"]:
                        plotConfigData["params"]["category_orders"] = {}
                    plotConfigData["params"]["category_orders"][plotConfigData["params"]
                                                                ["y"]] = self.category_Dict[plotConfigData["params"]["y"]]

                # remove nan values from dataframe
                usedCols = [b for a in [
                            (c if type(c) == list else [c]) for c in [
                                plotConfigData["params"].get(key) for key in
                                ["x", "y", "error_x", "error_y", "dimensions",
                                    "color", "facet_col", "facet_row"]
                            ] if c is not None
                            ] for b in a]
                inputDataFrame = inputDataFrame.dropna(subset=usedCols)

                # return the corresponding plot
                if plotConfigData["type"] == "scatter":
                    fig = _px.scatter(inputDataFrame, **
                                      plotConfigData["params"])
                if plotConfigData["type"] == "scatter_matrix":
                    fig = _px.scatter_matrix(
                        inputDataFrame, **plotConfigData["params"])
                if plotConfigData["type"] == "density_heatmap":
                    fig = _px.density_heatmap(
                        inputDataFrame, **plotConfigData["params"])
                if plotConfigData["type"] == "density_contour":
                    fig = _px.density_contour(
                        inputDataFrame, **plotConfigData["params"])
                if plotConfigData["type"] == "box":
                    fig = _px.box(inputDataFrame, **plotConfigData["params"])
                if plotConfigData["type"] == "violin":
                    fig = _px.violin(inputDataFrame, **
                                     plotConfigData["params"])
                if plotConfigData["type"] == "bar":
                    if "x" in plotConfigData["params"] and "y" in plotConfigData["params"]:
                        fig = _px.bar(inputDataFrame, **
                                      plotConfigData["params"])
                if plotConfigData["type"] == "histogram":
                    if "x" in plotConfigData["params"]:
                        fig = _px.histogram(
                            inputDataFrame, **plotConfigData["params"])

                # special plot histogram with line
                if plotConfigData["type"] == "histogram_line":
                    if "x" in plotConfigData["params"]:
                        # extrat params
                        x = plotConfigData["params"]["x"]
                        nbins = plotConfigData["params"]["nbins"]
                        cumulative = True if "cumulative" in plotConfigData[
                            "params"] and plotConfigData["params"]["cumulative"] else False
                        histnorm = "count"
                        normalize = False
                        if "histnorm" in plotConfigData["params"]:
                            if "density" in plotConfigData["params"]["histnorm"]:
                                histnorm = "density"
                                normalize = True
                            if "percent" in plotConfigData["params"]["histnorm"]:
                                histnorm = "percent"
                                normalize = True

                        groupParams = []
                        # add color and facet entries to possible data groupings
                        if "color" in plotConfigData["params"]:
                            groupParams.append(
                                plotConfigData["params"]["color"])
                        if "facet_row" in plotConfigData["params"]:
                            groupParams.append(
                                plotConfigData["params"]["facet_row"])
                        if "facet_col" in plotConfigData["params"]:
                            groupParams.append(
                                plotConfigData["params"]["facet_col"])
                        groupParams = list(set(filter(None, groupParams)))

                        plotData = None
                        if (len(groupParams) > 0):
                            for group, allValues in inputDataFrame.groupby(groupParams):

                                # extract the sampels to compute the histogram
                                histSamples = _np.array(allValues[x])

                                # compute an grid
                                histX = _np.linspace(
                                    _np.min(histSamples), _np.max(histSamples), nbins)
                                gridNorm = histX[1]-histX[0]
                                computeGrid = _np.linspace(
                                    histX[0]-0.5*gridNorm, histX[-1]+0.5*gridNorm, nbins+1)

                                # bin the data
                                histY, _ = _np.histogram(
                                    histSamples, bins=computeGrid, density=normalize)
                                if cumulative:
                                    histY = _np.cumsum(histY)
                                if normalize:
                                    histY = histY*gridNorm
                                if histnorm == "percent":
                                    histY *= 100.0

                                if plotData is None:
                                    if(len(groupParams) > 1):
                                        plotData = _pd.DataFrame(_np.transpose(
                                            [*_np.transpose([group]*nbins), histX, histY]))
                                    else:
                                        plotData = _pd.DataFrame(
                                            _np.transpose([[group]*nbins, histX, histY]))
                                else:
                                    if(len(groupParams) > 1):
                                        extra = _pd.DataFrame(_np.transpose(
                                            [*_np.transpose([group]*nbins), histX, histY]))
                                    else:
                                        extra = _pd.DataFrame(_np.transpose(
                                            [[group]*nbins, histX, histY]))
                                    plotData = plotData.append(extra)

                            colName = (
                                'cumulative ' if cumulative else '') + histnorm
                            plotData.columns = [*groupParams, x, colName]
                        else:
                            # extract the sampels to compute the histogram
                            histSamples = _np.array(inputDataFrame[x])

                            # compute an grid
                            histX = _np.linspace(
                                _np.min(histSamples), _np.max(histSamples), nbins)
                            gridNorm = histX[1]-histX[0]
                            computeGrid = _np.linspace(
                                histX[0]-0.5*gridNorm, histX[-1]+0.5*gridNorm, nbins+1)

                            # bin the data
                            histY, _ = _np.histogram(
                                histSamples, bins=computeGrid, density=normalize)
                            if cumulative:
                                histY = _np.cumsum(histY)
                            if normalize:
                                histY = histY*gridNorm
                            if histnorm == "percent":
                                histY *= 100.0

                            plotData = _pd.DataFrame(
                                _np.transpose([histX, histY]))
                            colName = (
                                'cumulative ' if cumulative else '') + histnorm
                            plotData.columns = [x, colName]

                        params = {p: plotConfigData["params"][p] for p in plotConfigData["params"] if p not in [
                            "nbins", "cumulative", "histnorm", "barmode"]}
                        params["y"] = colName

                        fig = _px.line(plotData, **params)

                if plotConfigData["type"] == "bar_count" and "x" in plotConfigData["params"]:
                    # daw a count plot
                    x = plotConfigData["params"]["x"]
                    groupParams = [x]

                    # add color and facet entries to possible data groupings
                    if "color" in plotConfigData["params"]:
                        groupParams.append(plotConfigData["params"]["color"])
                    if "facet_row" in plotConfigData["params"]:
                        groupParams.append(
                            plotConfigData["params"]["facet_row"])
                    if "facet_col" in plotConfigData["params"]:
                        groupParams.append(
                            plotConfigData["params"]["facet_col"])
                    groupParams = list(set(filter(None, groupParams)))

                    # group data and count the entries of each group
                    plotData = inputDataFrame.groupby(groupParams)[x].count()
                    # transoform the data back to have a count entry for each group tuple
                    plotData = _pd.DataFrame(plotData)
                    plotData.rename(columns={x: "count"}, inplace=True)
                    plotData.reset_index(inplace=True)
                    plotConfigData["params"]["y"] = "count"

                    # plot the data
                    fig = _px.bar(plotData, **plotConfigData["params"])

                if plotConfigData["type"] == "probability" and "x" in plotConfigData["params"]:
                    x = plotConfigData["params"]["x"]
                    del plotConfigData["params"]["x"]

                    showFit = False
                    if "trendline" in plotConfigData["params"] and plotConfigData["params"]["trendline"] == "ols":
                        showFit = True
                        del plotConfigData["params"]["trendline"]

                    groupParams = []
                    # add color and facet entries to possible data groupings
                    if "color" in plotConfigData["params"]:
                        groupParams.append(plotConfigData["params"]["color"])
                    if "facet_row" in plotConfigData["params"]:
                        groupParams.append(
                            plotConfigData["params"]["facet_row"])
                    if "facet_col" in plotConfigData["params"]:
                        groupParams.append(
                            plotConfigData["params"]["facet_col"])
                    groupParams = list(set(filter(None, groupParams)))

                    def getProbPlot(groupData, grouped=True):
                        res = _stats.probplot(groupData[x])
                        if grouped:
                            return _pd.Series({"Theoretical quantiles": res[0][0], "Percent": _stats.norm.cdf(res[0][0])*100.0, x: res[0][1], "Fit": res[0][0]*res[1][0] + res[1][1]})
                        else:
                            return _pd.DataFrame({"Theoretical quantiles": res[0][0], "Percent": _stats.norm.cdf(res[0][0])*100.0, x: res[0][1], "Fit": res[0][0]*res[1][0] + res[1][1]})

                    if len(groupParams) > 0:
                        plotData = inputDataFrame.groupby(groupParams).apply(
                            lambda x: getProbPlot(x)).apply(_pd.Series.explode).reset_index()
                    else:
                        plotData = getProbPlot(inputDataFrame, False)

                    # create the output plot
                    fig = _go.Figure()
                    plotConfigData["params"]["hover_data"] = ["Percent"]

                    scatterPlot = _px.scatter(
                        plotData, y="Theoretical quantiles", x=x,  **plotConfigData["params"])
                    for d in scatterPlot.data:
                        fig.add_trace(d)
                    if showFit:
                        for d in _px.line(plotData, y="Theoretical quantiles", x="Fit", **plotConfigData["params"]).data:
                            d.showlegend = False
                            fig.add_trace(d)
                    fig.update_layout(scatterPlot.layout)
                    fig.update_layout(
                        yaxis = dict(
                            tickmode = 'array',
                            tickvals = [-3.090232306,-2.326347874,-1.281551566,-0.841621234,-0.524400513,-0.253347103,0,0.253347103,0.524400513,0.841621234,1.281551566,1.644853627,2.326347874,3.090232306],
                            ticktext = ["0.1%","1%","10%","20%","30%","40%","50%","60%","70%","80%","90%","95%","99%","99.9%"]
                        )
                    )

                # if we want to force an axis as categorical
                if "x" in plotConfigData["params"] and plotConfigData["params"]["x"] in self.categorical_Cols and markCatX:
                    fig.update_layout(xaxis_type='category')
                if "y" in plotConfigData["params"] and plotConfigData["params"]["y"] in self.categorical_Cols and markCatY:
                    fig.update_layout(yaxis_type='category')

                if "title" in plotConfigData and plotConfigData["title"] is not None and plotConfigData["title"] != "":
                    fig.update_layout(title=plotConfigData["title"])

                # if we want to have independent x and y axis
                if makeIndepX:
                    fig.update_xaxes(matches=None, showticklabels=True)
                    for idx, a in enumerate([a for a in fig.layout if "xaxis" in a]):
                        d_min, d_max = fig.layout[a].domain
                        d_center = 0.5*(d_min+d_max)
                        d_width = 0.43*(d_max - d_min)
                        fig.layout[a].domain = ( d_center - d_width, d_center+d_width)
                if makeIndepY:
                    fig.update_yaxes(matches=None, showticklabels=True)
                

                # transform the fig to an png if object too big
                if "render" in plotConfigData and "png" in plotConfigData["render"]:

                    try:
                        # prepare to compute the image on a remote orca server
                        fig.update_layout(
                            template="plotly_white"
                        )
                        img_bytes = _pio.to_image(
                            fig, width=1200, height=700, scale=2)
                        encoded = _base64.b64encode(img_bytes)

                        # create an empty figure with some fixed axis
                        fig = _go.Figure()
                        fig.update_layout(
                            xaxis=_go.layout.XAxis(
                                showticklabels=False,
                                showgrid=False,
                                zeroline=False,
                                range=[0, 1200]
                            ),
                            yaxis=_go.layout.YAxis(
                                showticklabels=False,
                                showgrid=False,
                                zeroline=False,
                                range=[0, 700],
                                scaleanchor='x'
                            ),
                            margin={'l': 0, 'r': 0, 't': 0, 'b': 0},
                            autosize=True,
                        )

                        # add the png to the figure
                        fig.add_layout_image(
                            dict(
                                source="data:image/png;base64,{}".format(
                                    encoded.decode('ascii')),
                                xref="x",
                                yref="y",
                                x=0,
                                sizex=1200,
                                y=700,
                                sizey=700,
                                opacity=1.0,
                                layer="below",
                                sizing="stretch"
                            )
                        )

                    except Exception as ex:
                        print(ex)

                return fig

        except Exception as inst:
            errorResult = "Error: " + str(inst)

        return _px.scatter(self.dummyData, title=errorResult)
