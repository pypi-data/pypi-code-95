
from re import S
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import geopandas as gpd
import dash_bootstrap_components as dbc
from .. import geo
from .. import data
from . import config


class VisApp:
    """Dash application to visualize collected data"""

    def __init__(self):
        """Setup Dash aplication
        """
        # setup data
        self.df = self.data_for_map()

        # configuration for visualization

        self.columns = config.feature_info

        # creating a dash app
        self.app = dash.Dash(__name__, external_stylesheets=[
                             dbc.themes.BOOTSTRAP, "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.5.0/font/bootstrap-icons.css"])
        self.app.title = "IF_LICENSE_PLATES_COULD_TALK"
        self.app.layout = dbc.Container([
            dcc.Location(id="url", refresh=False),
            html.H1(children="IF_LICENSE_PLATES_COULD_TALK",
                    style={"margin-top": "30px"}),
            dbc.Tabs(id="page-content", children=[
                dbc.Tab(label="Maps", children=self.generate_map_page()),
                dbc.Tab(label="Scatter plots",
                        children=self.generate_scatter_page()),
                dbc.Tab(label="Time series",
                        children=self.generate_time_series_page())
            ]),
        ])
        self.setup_scatter_callbacks()
        self.setup_map_callbacks()
        self.setup_timeseries_callback()

    def run(self):
        """Start Dash server in debug mode

        Returns:
            None
        """
        self.app.run_server()

    def generate_map_page(self):
        return dbc.Container([
            dbc.Container([
                html.P("Feature:"),
                dcc.Dropdown(
                    id="map_feature_select",
                    options=[{"label": self.columns[feature]["title"],
                              "value": feature} for feature in self.columns],
                    value="crimes_pp"
                )],  style={"margin-top": "20px"}),
            dbc.Container([
                html.P("Year:"),
                dcc.Slider(id="map_year", min=2013, max=2018, value=2018, marks={y: f"{y}" for y in range(2013, 2019)})], style={"margin-top": "20px"}),
            html.Hr(),
            dcc.Loading(id="map_loading", type="circle",
                        children=[dbc.Container(id="map_output")])])

    def generate_scatter_page(self):

        return dbc.Container(
            [dbc.Row([dbc.Col(children=[
                html.P("Feature (x-axis):"),
                dcc.Dropdown(
                    id="scatter_feature_x",
                    options=[{"label": self.columns[feature]["title"],
                              "value": feature} for feature in self.columns],
                    value="crimes_pp"
                )]), dbc.Col(children=[html.P("Scale (x-axis):"),
                                       dcc.Dropdown(
                    id="scatter_log_x", options=[{"label":  "linear",
                                                  "value": "linear"}, {"label": "log", "value": "log"}],
                    value="linear"
                )])], style={"margin-top": "20px"}),
                dbc.Row([dbc.Col(children=[
                    html.P("Feature (y-axis):"),
                    dcc.Dropdown(
                        id="scatter_feature_y",
                        options=[{"label": self.columns[feature]["title"],
                                  "value": feature} for feature in self.columns],
                        value="income_pp"
                    )]), dbc.Col(children=[html.P("Scale (y-axis):"),
                                           dcc.Dropdown(
                        id="scatter_log_y", options=[{"label":  "linear",
                                                      "value": "linear"}, {"label": "log", "value": "log"}],
                        value="linear"
                    )])],  style={"margin-top": "20px"}),
             dbc.Container([
                 html.P("Year:"),
                 dcc.Slider(id="scatter_year", min=2013, max=2018, value=2018, marks={y: f"{y}" for y in range(2013, 2019)})], style={"margin-top": "20px"}),
             html.Hr(),
             dcc.Loading(id="scatter_loading", type="circle",
                         children=[dbc.Container(id="scatter_output")])
             ])

    def generate_scatter_plot(self, feature_x, log_x,  feature_y, log_y, year):
        featinfo_x = self.columns[feature_x]
        col_x = feature_x
        if featinfo_x["time_dep"]:
            col_x += f"_{year}"
        log_x = log_x == "log"

        featinfo_y = self.columns[feature_y]
        col_y = feature_y
        if featinfo_y["time_dep"]:
            col_y += f"_{year}"
        log_y = log_y == "log"

        fig = px.scatter(data_frame=self.df,
                         x=col_x, y=col_y, color="east",  hover_data=["kreis_name"],
                         labels={col_x: featinfo_x["label"],
                                 col_y: featinfo_y["label"]},
                         log_x=log_x,
                         log_y=log_y,
                         trendline="ols",
                         trendline_options=dict(log_x=log_x, log_y=log_y),
                         trendline_color_override="red")

        return dcc.Graph(
            id='scatter',
            figure=fig
        )

    def generate_timeseries_plot(self, feature, kreis):
        featinfo = self.columns[feature]

        df = self.df[self.df.kreis_key == kreis].melt()
        df.columns = ["year", feature]
        df = df[df.year.str.contains(feature+"_2")].copy()
        df.year = pd.to_numeric(df.year.str.slice(start=-4))

        df.dropna()

        fig = px.line(data_frame=df, x="year", y=feature,
                      labels={feature: featinfo["label"]})

        return dcc.Graph(
            id="timeseries",
            figure=fig
        )

    def generate_time_series_page(self):
        return dbc.Container([
            dbc.Container([
                html.P("Feature:"),
                dcc.Dropdown(
                    id="timeseries_feature",
                    options=[{"label": self.columns[feature]["title"],
                              "value": feature} for feature in self.columns if self.columns[feature]["time_dep"]],
                    value="crimes_pp"
                )],  style={"margin-top": "20px"}),
            dbc.Container([
                html.P("Region:"),
                dcc.Dropdown(
                    id="timeseries_kreis",
                    options=[{"label": row[1],
                              "value": row[0]} for row in self.df.sort_values(by="kreis_name")[["kreis_key", "kreis_name"]].values],
                    value="02000"
                )],  style={"margin-top": "20px"}),
            html.Hr(),
            dcc.Loading(id="timeseries_loading", type="circle",
                        children=[dbc.Container(id="timeseries_output")])])

    def generate_map_output(self, feature, year):
        """Generate output structure

        Args:
            feature (str): feature column to display
            year (int): -

        Returns:
            [Component]: dash components to display map of germany with selected regional data.
        """
        return [
            dbc.Row([
                dbc.Col([
                    html.Div(id="map_container",
                             children=[self.generate_map(feature, year)])
                ])
            ])
        ]

    def setup_map_callbacks(self):
        """Setup the callbacks for the map page

        Returns:
            None
        """
        @ self.app.callback(
            dash.dependencies.Output("map_output", "children"),
            [dash.dependencies.Input("map_feature_select", "value"), dash.dependencies.Input("map_year", "value")])
        def update(feature, year):
            if feature != None:
                return self.generate_map_output(feature, year)

        @ self.app.callback(
            dash.dependencies.Output("map_year", "disabled"),
            [dash.dependencies.Input("map_feature_select", "value")])
        def update(feature):
            if feature != None:
                return not self.columns[feature]["time_dep"]

    def setup_scatter_callbacks(self):
        """Setup the callbacks for the scatter page
        """
        @ self.app.callback(
            dash.dependencies.Output("scatter_output", "children"),
            [dash.dependencies.Input("scatter_feature_x", "value"), dash.dependencies.Input("scatter_log_x", "value"), dash.dependencies.Input(
                "scatter_feature_y", "value"), dash.dependencies.Input("scatter_log_y", "value"), dash.dependencies.Input("scatter_year", "value")])
        def update(feature_x, log_x, feature_y, log_y, year):
            if None not in [feature_x, log_x, feature_y, log_y]:
                return self.generate_scatter_plot(feature_x, log_x,  feature_y, log_y,  year)

    def setup_timeseries_callback(self):
        """Setup the callbacks for the scatter page
        """
        @ self.app.callback(
            dash.dependencies.Output("timeseries_output", "children"),
            [dash.dependencies.Input("timeseries_feature", "value"), dash.dependencies.Input(
                "timeseries_kreis", "value")])
        def update(feature, kreis):
            if None not in [feature, kreis]:
                return self.generate_timeseries_plot(feature, kreis)

    def data_for_map(self):
        """Load data for visualization"""
        df_geo = geo.utils.load_geodata()
        df = data.db.get_data()

        df_comb = df_geo.merge(
            df, left_on="RS", right_on="kreis_key", how="left")

        return df_comb

    def generate_map(self, feature, year):
        """Generate map for visualization

        Args:
            feature (str): feature column
            year (int): year

        Returns:
            dcc.Graph: Map component
        """

        feature_info = self.columns[feature]

        if feature_info["time_dep"]:
            col = f"{feature}_{year}"
        else:
            col = feature

        fig = px.choropleth(self.df.fillna(0), geojson=self.df.geometry, locations=self.df.index, color=col, scope="europe",
                            color_continuous_scale=feature_info["color"],
                            range_color=(self.df[col].min(
                            ), self.df[col].max()),
                            hover_name="kreis_name",
                            hover_data=[col],
                            color_discrete_map=feature_info["color"],
                            labels={
                                col: feature_info["label"]
        })
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        fig.update_layout(hoverlabel={"bgcolor": "white"})

        return dcc.Graph(
            id='map',
            figure=fig
        )
