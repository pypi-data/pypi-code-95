# TODO : plot forecast
# TODO: report estimation outputs


import base64
import datetime
import io


from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash_table import DataTable
import plotly.express as px
import plotly.graph_objects as go

import webbrowser

import numpy as np
import pandas as pd
pd.options.plotting.backend = "plotly"


from statsmodels.tsa.arima.model import ARIMA as tsaARMA # PARA ESTIMAR MODELO
from statsmodels.tsa.stattools import acf, pacf # autocorrelation and partial autocorrelation

from macrodemos.common_components import app_parameter, app_parameter_row, editable_cell_format, \
    colors, make_bottom_banner, make_top_banner, app_choose_parameter, app_one_option, app_model_parameter, app_table_headers




import warnings


omega = np.linspace(0, np.pi, 121)  # frequencies for spectral plot

def add_polar_scatter(fig, roots, name, ms=16):
    """
    Adds a polar scatter to existing figure

    To help making the plots for the roots of the ARIMA polynomial

    :param fig: existing plotly.Figure
    :param roots: roots of the characteristic polynomial
    :param name: name for the series (to use in legend)
    :param ms: marker size
    :return:
    float, maximum absolute value of roots.
    Updates fig in place
    """
    radium = np.abs(roots)
    angles = np.angle(roots, True)
    fig.add_trace(go.Scatterpolar(
        r=radium,
        theta=angles,
        name = name,
        mode = 'markers',
        marker_size=ms
    ))
    return max(radium)

def compute_spectral(yvalues):
    yy = yvalues - yvalues.mean()
    v = (yy ** 2).mean()  # estimated variance
    T = yy.size

    r = int(np.sqrt(T))
    gamma = acf(yy, adjusted=False, nlags=r, fft=False)
    k = np.arange(r + 1)
    g = 1 - k / r # Bartlett window
    sw = ((np.cos(np.outer(omega, k)) * (g * gamma)).sum(axis=1) * 2 - 1)
    sw *= v / (2 * np.pi)  # rescale
    return sw


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename[-4:]:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), parse_dates=[0])
        elif 'xls' in filename[-4:]:
            # Assume that the user uploaded an Excel file
            df = pd.read_excel(io.BytesIO(decoded), parse_dates=[0])
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    df.set_index(df.columns[0], inplace=True)

    return df


# =======================================================================================================================
#
#  ARMA_class CLASS
#
# _______________________________________________________________________________________________________________________


class ARIMA:
    def __init__(self, df):
        self.data = df
        self.y = None
        self.current_variable_name = None
        self.estimates = [{}, {}]
        self.estimates[0]['residuals'] = np.zeros(5)
        self.estimates[1]['residuals'] = np.zeros(5)
        self.estimated = [False, False]
        self.estimation_order = [dict(p=0, q=0), dict(p=0, q=0)]

    def transform_series(self, varname, take_log, diff):
        serie = self.data[varname]
        name = varname

        if take_log == 'yes':
            serie = np.log(serie)
            name = f'log({name})'

        if diff == '1':
            serie = serie.diff()
            name = f'Δ{name}'

        if diff == '2':
            serie = serie.diff().diff()
            name = f'Δ2{name}'

        self.y = serie.dropna()
        self.current_variable_name = name

        # ACTUAL DATA PLOTS-----------------------------------------

    def plot_actual_data(self):
        return self.y.plot(title=self.current_variable_name)
        # return px.line(y=self.y.values,
        #               title=self.current_variable_name,
        #               template='simple_white'
        #              )

    def plot_correlogram(self, lags):
        return px.bar(y=acf(self.y.values, adjusted=True, nlags=lags, fft=False),
                      title='Autocorrelations',
                      labels=dict(x='lag', y='coefficient'),
                      # color_discrete_sequence=px.colors.qualitative.Dark24,
                      template='simple_white'
                      )

    def plot_partial_correlogram(self, lags):
        return px.bar(y=pacf(self.y.values, nlags=lags),
                      title='Partial Autocorrelations',
                      labels=dict(x='lag', y='coefficient'),
                      # color_discrete_sequence=px.colors.qualitative.Dark24,
                      template='simple_white'
                      )

    def plot_spectral(self):

        return px.area(
            x=omega,
            y=compute_spectral(self.y.values),
            title='Spectral Density',
            labels=dict(x=r'$\omega$', y=r'$s(\omega)$'),
            # color_discrete_sequence=px.colors.qualitative.Dark24,
            template='simple_white'
        )

    # ESTIMATION OF MODELS--------------------------------------------------
    def estimate(self, p, q, modelo):
        try:
            print(f'Trying to estimate the model ARMA({p}, {q}) ')
            # res = tsaARMA(self.y, order=[p, 0, q], freq=self.data.index.freqstr).fit()
            res = tsaARMA(self.y, order=[p, 0, q]).fit()
            self.estimates[modelo] = {
                'c': res.params[0],
                'phi': res.arparams if p else None,
                'theta': res.maparams if q else None,
                'fitted': pd.Series(res.fittedvalues),
                'residuals': pd.Series(res.resid),
                'arroots': np.array([1 / x for x in res.arroots]) if p else None,
                'maroots': np.array([1 / x for x in res.maroots]) if q else None
            }
            self.estimated[modelo] = True
            self.estimation_order[modelo] = dict(p=p, q=q)

            res1 = res.summary().tables[1]
            result = pd.DataFrame(res1.data[1:], columns=res1.data[0])
            result = result.iloc[:, [0, 1, 4]]
            result.rename(columns={'': 'param'}, inplace=True)

            new_estimate = DataTable(
                data=result.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in result.columns])
            self.estimated_table = new_estimate.data
            print(f'Model {modelo} succesfully estimated!')

        except:
            self.estimated[modelo] = False
            print('The model could not be estimated')
            # self.estimates['repr'] = 'The model could not be estimated'
            self.estimated_table = []

            # RESIDUAL PLOTS-------------------------------------------

    def plot_residual(self):
        residuos = pd.DataFrame(
            {'Model 1': self.estimates[0]['residuals'],
             'Model 2': self.estimates[1]['residuals']},
            index=self.data.index
        )
        return residuos.plot(title='Model Fit Residuals')

    def plot_residual_correlogram(self, nlags):
        df = pd.DataFrame(
            {'Model 1': acf(self.estimates[0]['residuals'].values, adjusted=True, nlags=nlags, fft=False),
             'Model 2': acf(self.estimates[1]['residuals'].values, adjusted=True, nlags=nlags, fft=False)}
        )

        fig = px.bar(df.iloc[1:],
                     barmode='group',
                     title='Autocorrelations of Model Residuals',
                     template='simple_white')

        fig.update_layout(
            legend_orientation='h',
            xaxis_title='Lag',
            yaxis_title=r'$\rho$'
        )
        return fig

    def plot_residual_partial_correlogram(self, nlags):
        df = pd.DataFrame(
            {'Model 1': pacf(self.estimates[0]['residuals'].values, nlags=nlags),
             'Model 2': pacf(self.estimates[1]['residuals'].values, nlags=nlags)}
        )

        fig = px.bar(df.iloc[1:],
                     barmode='group',
                     title='Partial Autocorrelations of Model Residuals',
                     template='simple_white')

        fig.update_layout(
            legend_orientation='h',
            xaxis_title='Lag',
            yaxis_title=r'$\rho$'
        )
        return fig

    def plot_residual_spectral(self):

        df = pd.DataFrame(
            {'Model 1': compute_spectral(self.estimates[0]['residuals'].dropna().values),
             'Model 2': compute_spectral(self.estimates[1]['residuals'].dropna().values),
             'Frequency': omega}
        )

        # sw0 = compute_spectral(self.estimates[0]['residuals'].dropna().values)
        # sw1 = compute_spectral(self.estimates[1]['residuals'].dropna().values)

        fig = px.area(
            df,
            x='Frequency',
            y=['Model 1'],
            title='Spectral Density',
            labels=dict(x=r'$\omega$', y=r'$s(\omega)$'),
            # color_discrete_sequence=px.colors.qualitative.Dark24,
            template='simple_white'
        )

        fig.add_trace(go.Scatter(
            x=df['Frequency'],
            y=df['Model 2'],
            fill='tozeroy',
            mode='lines',
            name='Model 2'
        )
        )
        return fig

    def plot_ar_roots(self):
        fig = go.Figure()
        rmax0 = add_polar_scatter(fig, self.estimates[0]['arroots'] if self.estimation_order[0]['p'] else [0],
                                  'Model 1')
        rmax1 = add_polar_scatter(fig, self.estimates[1]['arroots'] if self.estimation_order[1]['p'] else [0],
                                  'Model 2')

        maxr = max([1, rmax0, rmax1])
        fig.update_layout(
            title='AR inverse roots',
            polar={'angularaxis': {'thetaunit': 'radians', 'dtick': np.pi / 4},
                   'radialaxis': {'tickvals': [0.0, 1.0], 'range': [0, maxr]}}
        )
        return fig

    def plot_ma_roots(self):
        fig = go.Figure()
        rmax0 = add_polar_scatter(fig, self.estimates[0]['maroots'] if self.estimation_order[0]['q'] else [0],
                                  'Model 1')
        rmax1 = add_polar_scatter(fig, self.estimates[1]['maroots'] if self.estimation_order[1]['q'] else [0],
                                  'Model 2')

        maxr = max([1, rmax0, rmax1])
        fig.update_layout(
            title='MA inverse roots',
            polar={'angularaxis': {'thetaunit': 'radians', 'dtick': np.pi / 4},
                   'radialaxis': {'tickvals': [0.0, 1.0], 'range': [0, maxr]}}
        )
        return fig


APPDATA = ARIMA(None)

# Esta parte controla asuntos de estética de la página
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# =======================================================================================================================
#
#  APP STARTS HERE
#
# _______________________________________________________________________________________________________________________
mathjax = ["https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML"]  # to display math



app = JupyterDash(__name__, external_stylesheets=external_stylesheets, external_scripts=mathjax,
                  suppress_callback_exceptions=True)

# ======DESIGN THE APP===============

app.layout = html.Div(children=[
    *make_top_banner("Box Jenkins methodology"),
    html.Div(children=[
        html.H4("Getting data ready"),
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('select a CSV or Excel file')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            multiple=False  # Allow multiple files to be uploaded
        ),
        html.Table(id='select-variable', style={'width': '100%'},
                   # children=[app_choose_parameter('Variable', 'variable', UPLOADED_DATA.columns.tolist(), UPLOADED_DATA.columns[0])]
                   ),
        html.Table(children=[
        ]
        ),
        html.Hr(),
        html.H4("Model specifications"),
        html.Table(children=[
            app_table_headers(['   ', 'Model 1', 'Model 2']),
            app_model_parameter('p', 1, 0),
            app_model_parameter('q', 0, 1),
        ],
        ),
        html.Hr(),
        html.H4("Figure Parameters"),
        html.Table(children=[
            app_parameter_row('AC and PAC lags', 'lags', 'text', '12', '8'),
            app_parameter_row('IRF horizon', 'horizon', 'text', '24', '8')]),
        html.Hr(),
        html.Button('ESTIMATE', id='estimate', style={'textAlign': 'center', 'backgroundColor': colors['buttons']}),
    ],
        style={'textAlign': 'center', 'color': colors['controls'], 'width': '20%', 'display': 'inline-block'}),

    html.Div(style={'width': '80%', 'float': 'right', 'display': 'inline-block'},
             children=[
                 dcc.Tabs([
                     dcc.Tab(label='Data plots',
                             children=[
                                 # --PLOT 1:  SIMULATED TIME SERIES--------------------------------------------------
                                 dcc.Graph(id='plot-data-series',
                                           style={'width': '99%', 'float': 'left', 'display': 'inline-block'}),
                                 # --PLOT 2a:  AUTOCORRELOGRAM---------------------------------------------------------
                                 dcc.Graph(id='plot-data-acf',
                                           style={'width': '33%', 'float': 'left', 'display': 'inline-block'}),
                                 # --PLOT 2b:  PARCIAL AUTOCORRELOGRAM-------------------------------------------------
                                 dcc.Graph(id='plot-data-pacf',
                                           style={'width': '33%', 'float': 'left', 'display': 'inline-block'}),
                                 # --PLOT 2a:  SPECTRAL DENSITY---------------------------------------------------------
                                 dcc.Graph(id='plot-data-spectrum',
                                           style={'width': '33%', 'float': 'left', 'display': 'inline-block'}),
                             ]
                             ),
                     dcc.Tab(label='Estimation plots',
                             children=[
                                 # --PLOT 1:  Residuals--------------------------------------------------
                                 dcc.Graph(id='plot-residual-series',
                                           style={'width': '99%', 'float': 'left', 'display': 'inline-block'}),
                                 # --PLOT 2a:  AUTOCORRELOGRAM---------------------------------------------------------
                                 dcc.Graph(id='plot-residual-acf',
                                           style={'width': '49%', 'float': 'left', 'display': 'inline-block'}),
                                 # --PLOT 2b:  PARCIAL AUTOCORRELOGRAM-------------------------------------------------
                                 dcc.Graph(id='plot-residual-pacf',
                                           style={'width': '49%', 'float': 'left', 'display': 'inline-block'}),
                                 # --PLOT 2a:  SPECTRAL DENSITY---------------------------------------------------------
                                 dcc.Graph(id='plot-residual-spectrum',
                                           style={'width': '39%', 'float': 'left', 'display': 'inline-block'}),
                                 # --PLOT 3a:  AR ROOTS-----------------------------------------------------------------
                                 dcc.Graph(id='plot-estimated-ar-roots',
                                           style={'width': '30%', 'float': 'left', 'display': 'inline-block'}),
                                 # --PLOT 3b:  IMPULSE RESPONSE FUNCTION------------------------------------------------
                                 dcc.Graph(id='plot-estimated-ma-roots',
                                           style={'width': '30%', 'float': 'left', 'display': 'inline-block'}),
                             ]
                             ),
                     dcc.Tab(label='Uploaded data',
                             children=html.Div(id='output-data-upload')),
                 ]),
             ]),
    make_bottom_banner("macrodemos.BoxJenkins()", width=20)
],
    style={'backgroundColor': colors['background']})


def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename[-4:]:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), parse_dates=[0])
        elif 'xls' in filename[-4:]:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded), parse_dates=[0])
    except Exception as e:
        print(e)
        # return html.Div([
        #    'There was an error processing this file.'
        # ])

    df.set_index(df.columns[0], inplace=True)

    return df


@app.callback([Output('select-variable', 'children'),
               Output('output-data-upload', 'children')],
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_variable_selector(contents, filename, date):
    if contents is not None:
        df = parse_contents(contents, filename)
        APPDATA.data = df
        indicators = df.columns
        variable_selector = [
            app_choose_parameter('Variable', 'variable', indicators, indicators[0]),
            app_one_option('Take log?', 'log', ['yes', 'no'], ['yes', 'no'], 'no'),
            app_one_option('Differentiate?', 'I', ['no', 'once', 'twice'], ['0', '1', '2'], '0')
        ]
        data_table = html.Div([
            html.H5(f'Uploaded file: {filename}',
                    style={'color': 'white'}),
            html.H6(f'Last modified: {datetime.datetime.fromtimestamp(date)}',
                    style={'color': 'white'}),

            DataTable(
                data=df.reset_index().to_dict('records'),
                columns=[{'name': i, 'id': i} for i in df.columns])
        ])
        return variable_selector, data_table


@app.callback([Output('plot-data-series', 'figure'),  # fix this
               Output('plot-data-acf', 'figure'),
               Output('plot-data-pacf', 'figure'),
               Output('plot-data-spectrum', 'figure'),
               ],  # fix this
              [Input('variable', 'value'),
               Input('log', 'value'),
               Input('I', 'value')],
              [State('lags', 'value'),
               State('upload-data', 'contents')]
              )
def prepare_data(varname, take_log, diff, nlags, fileuploaded):
    if fileuploaded:
        APPDATA.transform_series(varname, take_log, diff)
        nlags = int(nlags)
        return (APPDATA.plot_actual_data(),
                APPDATA.plot_correlogram(nlags),
                APPDATA.plot_partial_correlogram(nlags),
                APPDATA.plot_spectral()
                )


@app.callback([Output('plot-residual-series', 'figure'),  # fix this
               Output('plot-residual-acf', 'figure'),
               Output('plot-residual-pacf', 'figure'),
               Output('plot-residual-spectrum', 'figure'),
               Output('plot-estimated-ar-roots', 'figure'),
               Output('plot-estimated-ma-roots', 'figure'),
               ],  # fix this
              [Input('estimate', 'n_clicks')],
              [State('base_p', 'value'),
               State('base_q', 'value'),
               State('scen_p', 'value'),
               State('scen_q', 'value'),
               State('lags', 'value')]
              )
def estimate_models(n_clicks, p1, q1, p2, q2, nlags):
    APPDATA.estimate(int(p1), int(q1), 0)
    APPDATA.estimate(int(p2), int(q2), 1)

    nlags = int(nlags)

    return (
        APPDATA.plot_residual(),
        APPDATA.plot_residual_correlogram(nlags),
        APPDATA.plot_residual_partial_correlogram(nlags),
        APPDATA.plot_residual_spectral(),
        APPDATA.plot_ar_roots(),
        APPDATA.plot_ma_roots()
    )


def BoxJenkins(colab=True):
    if colab:
        app.run_server(mode='external')
    else:
        webbrowser.open('http://127.0.0.1:8050/')
        app.run_server(debug=False)

BoxJenkins_demo = BoxJenkins # kept to keep consistency with all names


if __name__ == '__main__':
    BoxJenkins()