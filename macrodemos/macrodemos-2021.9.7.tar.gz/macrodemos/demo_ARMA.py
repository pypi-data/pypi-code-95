"""
demo_ARMA: Module for learning about  ARMA processes

This module provides a single function, ARMA(), which creates a dash consisting of 7 plots to study the
theoretical properties of ARMA(p, q) process, as well as their estimated counterparts. The plots display
    1. a simulated sample
    2. autocorrelations
    3. partial autocorrelations
    4. impulse response function
    5. spectral density
    6. AR inverse roots
    7. MA inverse roots

Randall Romero Aguilar
2016-2021
"""



from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table
import plotly.express as px
import plotly.graph_objects as go
import webbrowser

from macrodemos.common_components import app_parameter, app_parameter_row, editable_cell_format, \
    colors, make_bottom_banner, make_top_banner

import numpy as np
from numpy.polynomial import Polynomial as P
import pandas as pd
from scipy import signal

from statsmodels.tsa.arima.model import ARIMA as tsaARMA # PARA ESTIMAR MODELO
from statsmodels.tsa.arima_process import ArmaProcess # MODELO TEORICO
from statsmodels.tsa.stattools import acf, pacf # autocorrelation and partial autocorrelation





# Esta parte controla asuntos de estética de la página
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


# Esta función se utiliza para calcular la varianza del proceso ARMA


def qnwsimp(n, a, b):
    """
    Compute univariate Simpson quadrature nodes and weights

    Parameters
    ----------
    n : int, the number of nodes
    a : int, the lower endpoint
    b : int, the upper endpoint

    Returns
    -------
    nodes : np.ndarray(dtype=float)
        An n element array of nodes

    weights : np.ndarray(dtype=float)
        An n element array of weights

    Notes
    -----
    Based of original function ``qnwsimp1`` in CompEcon toolbox by
    Miranda and Fackler

    References
    ----------
    Miranda, Mario J, and Paul L Fackler. Applied Computational
    Economics and Finance, MIT Press, 2002.

    """
    if n % 2 == 0:
        print("WARNING qnwsimp: n must be an odd integer. Increasing by 1")
        n += 1

    nodes = np.linspace(a, b, n)
    weights = np.tile([2.0, 4.0], [int((n + 1) / 2)])
    weights = weights[:n]
    weights[0] = weights[-1] = 1
    weights *= (b-a) / (3*(n-1))

    return nodes, weights


def validate_lists_of_values(value: str):
    """Splits AR and MA string into list of floats    """
    return [float(x) for x in value.split(',')] if value else None


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


#=======================================================================================================================
#
#  ARMA_class CLASS
#
#_______________________________________________________________________________________________________________________
class ARMA_class(ArmaProcess):
    """
    A class to represent stationary ARMA processes
    """

    def __init__(self, c=0, phi=None, theta=None, sigma2=1.0, nobs=120):
        """
        Making  a new ARMA_class object to represent $y_t = c + phi y_{t-lags} + e_t + theta e_{t- lags}$

        :param c:  float, intercept
        :param phi: list-like, autorregresive coefficients
        :param theta: list-like, moving average coefficients
        :param sigma2: float, positive, variance of the error term
        :param nobs: int, number of periods for simulated sample (if requested)
        """
        if type(phi) is np.ndarray:
            ar = np.r_[1, -phi]  # add zero-lag and negate
        elif phi in (None, 0, ''):
            ar = np.ones(1)
        else:
            ar = np.r_[1, -np.array(phi)]  # add zero-lag and negate

        if type(theta) is np.ndarray:
            ma = np.r_[1, theta]  # add zero-lag
        elif theta in (None, 0, ''):
            ma = np.ones(1)
        else:
            ma = np.r_[1, np.array(theta)]  # add zero-lag

        super().__init__(ar, ma, nobs)
        self.c = float(c)  # intercept
        self.Phi = P(self.ar) # AR polynomial
        self.Theta = P(self.ma)  # MA polynomial
        self.p = self.Phi.degree()
        self.q = self.Theta.degree()
        self.sigma2 = float(sigma2)  # white noise variance
        self.simulated_data = None
        self.show_estimates = False
        self.estimates = {'repr': ''}
        self.estimated = False
        self.estimated_table = []



    @property
    def mean(self):
        """
        Mean of the process (if stationary)
        :return:
        float: mean of the process
        """
        return self.c / self.Phi(1) if self.isstationary else np.nan

    @property
    def variance(self):
        """
        Variance of the process (if stationary)
        :return:
        float, variance of the process
        """
        frequencies, weights = qnwsimp(121, 0, np.pi)
        sw = self.periodogram(frequencies)
        return 2* weights.dot(sw)

    def __simulate_shocks(self, n, irf=False):
        if irf:
            shocks = np.zeros(n, float)
            shocks[0] = 1.0
        else:
            shocks = np.random.randn(n) * np.sqrt(self.sigma2)
        return shocks

    def __simulate_MA(self, e):
        #return np.convolve(self.Theta.coef[::-1], e, 'valid')
        return np.convolve(self.ma[::-1], e, 'valid')

    def __simulate_AR(self, e):
        p = self.p
        y0 = np.zeros(p)
        if self.isstationary:
            y0 += self.mean

        phi = self.arcoefs[::-1]
        y = np.hstack((y0, np.zeros_like(e)))

        for t, et in enumerate(e):
            y[t + p] = self.c + phi.dot(y[t:(t+p)]) + et
        return y

    def sample(self, n=101):
        """

        :param n:
        :return:
        """
        e = self.__simulate_shocks(n + self.q)
        ma = self.__simulate_MA(e)
        self.simulated_data = pd.Series(self.__simulate_AR(ma))

    #def sample(self, n=101):
    #    raw_data = self.generate_sample(nsample=n, scale=np.sqrt(self.sigma2))
    #    print(raw_data)
    #    self.simulated_data = pd.Series(raw_data + self.mean)

    def estimate(self, p, q):
        try:
            res = tsaARMA(self.simulated_data.values, order=[p, 0, q]).fit()
            self.estimates = {'c': res.params[0]}
            self.estimates['phi'] = res.arparams if p else None
            self.estimates['theta'] = res.maparams if q else None
            self.estimates['repr'] = str(ARMA_class(self.estimates['c'], self.estimates['phi'], self.estimates['theta']))
            self.estimates['fitted'] = pd.Series(res.fittedvalues)
            self.estimates['arroots'] = np.array([1/x for x in res.arroots])
            self.estimates['maroots'] = np.array([1 / x for x in res.maroots])
            self.estimated = True

            res1 = res.summary().tables[1]
            result = pd.DataFrame(res1.data[1:], columns=res1.data[0])
            result = result.iloc[:, [0, 1, 4]]
            result.rename(columns={'': 'param'}, inplace=True)


            new_estimate = dash_table.DataTable(
                data=result.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in result.columns])
            self.estimated_table = new_estimate.data
        except:
            self.estimated = False
            self.estimates['repr'] = 'The model could not be estimated'
            self.estimated_table = []

    def print2moments(self):
        return f'$E(y_t) = {self.mean:g}, V(y_t) = {self.variance:g}$' if self.isstationary else 'This process is not stationay!'

    def __str__(self):
        c = f'{self.c:g}' if self.c else ''
        if self.p:
            ar = ' '.join([f'{phi:+g}y_{{t-{k + 1}}}' for k, phi in enumerate(self.arcoefs) if phi])
        else:
            ar = ''
        if self.q:
            ma = ' '.join([f'{theta:+g}\epsilon_{{t-{k + 1}}}' for k, theta in enumerate(self.macoefs) if theta])
        else:
            ma = ''

        rhs = c + ar + ' + \epsilon_t' + ma
        rhs = rhs[1:] if rhs[0] == '+' else rhs  # drop leading + sign

        return r'$y_t = ' + rhs + '$'

    def periodogram(self, frecuencias):
        return abs(signal.freqz(self.ma, self.ar, worN=frecuencias)[1]) ** 2 / (2 * np.pi)

    def plot_spectral(self):
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=omega,
            y=self.periodogram(omega) if self.isstationary else np.zeros_like(omega),
            name='actual' if self.isstationary else 'not defined',
            fill='tozeroy')
        )

        if self.show_estimates:
            yy = self.simulated_data - self.simulated_data.mean()
            v = (yy ** 2).mean()  # estimated variance
            T = yy.size
            r = int(np.sqrt(T))
            gamma = acf(yy, adjusted=False, nlags=r, fft=False)
            k = np.arange(r + 1)
            g = 1 - k / r  # Bartlett window
            sw = ((np.cos(np.outer(omega, k)) * (g * gamma)).sum(axis=1) * 2 - 1)
            sw *= v / (2 * np.pi)  # rescale

            fig.add_trace(go.Scatter(
                x=omega,
                y=sw,
                mode='lines',
                name='estimated'
            )
            )

        fig.update_layout(
            title='Spectral Density',
            template='simple_white',
            xaxis=dict(
                tickmode='array',
                tickvals=np.linspace(0, np.pi, 5),
                ticktext=['0', r'$\pi/4$', r'$\pi/2$', r'$3\pi/4$', r'$\pi$']
            )
        )
        return fig

    def plot_correlogram(self, lags):
        lags += 1

        df = pd.DataFrame({'actual': self.acf(lags=lags)} if self.isstationary else {'not defined':np.zeros(lags)})
        if self.show_estimates:
            self.estimates['acf'] = acf(self.simulated_data, adjusted=True, nlags=lags-1, fft=False)
            df['estimated'] = self.estimates['acf']

        fig = px.bar(df,
                     barmode='group',
                     title='Autocorrelations',
                     template='simple_white')

        fig.update_layout(
            legend_orientation='h',
            xaxis_title='Lag',
            yaxis_title=r'$\rho$'
        )
        return fig


    def plot_partial_correlogram(self, lags):
        lags += 1

        df = pd.DataFrame({'actual': self.pacf(lags=lags)} if self.isstationary else {'not defined':np.zeros(lags)})
        if self.show_estimates:
            self.estimates['acf'] = pacf(self.simulated_data, nlags=lags-1)
            df['estimated'] = self.estimates['acf']

        fig = px.bar(df,
                     barmode='group',
                     title='Partial Autocorrelations',
                     template='simple_white')

        fig.update_layout(
            legend_orientation='h',
            xaxis_title='Lag',
            yaxis_title=r'$\rho$'
        )
        return fig



    def plot_process(self):
        df = pd.DataFrame({'actual':self.simulated_data.values,
                           r'$\mu$':self.mean})

        if self.show_estimates and self.estimated:
            df['fitted'] = self.estimates['fitted']

        fig = px.line(
            data_frame=df,
            title='Simulated Data',
            template='simple_white'
        )
        fig.update_layout(
            legend_orientation='h',
            xaxis_title='Period',
            yaxis_title=r'$y_t$',
        )

        fig.add_annotation(
            x=0.2,
            y=1.05,
            xref="paper",
            yref="paper",
            text=str(self),
            showarrow=False
        )

        return fig

    def plot_ar_roots(self):
        fig = go.Figure()
        if self.p:
            rmax0 = add_polar_scatter(fig, 1 / self.arroots,
                                      'actual')  # statsmodels gives roots of the lag polinomial, not the characteristic function
        else:
            rmax0 = add_polar_scatter(fig, [0], 'actual', ms=0)

        if self.show_estimates and self.estimated:
            roots = self.estimates['arroots']
            if len(roots):
                rmax1 = add_polar_scatter(fig, roots, 'estimated')
            else:
                rmax1 = 1
        else:
            rmax1 = 1

        maxr = max([1, rmax0, rmax1])
        fig.update_layout(
            title='AR inverse roots',
            polar={'angularaxis': {'thetaunit': 'radians', 'dtick': np.pi / 4},
                   'radialaxis': {'tickvals': [0.0, 1.0], 'range': [0, maxr]}}
        )
        return fig

    def plot_ma_roots(self):
        fig = go.Figure()
        if self.q:
            rmax0 = add_polar_scatter(fig, 1 / self.maroots,
                                      'actual')  # statsmodels gives roots of the lag polinomial, not the characteristic function
        else:
            rmax0 = add_polar_scatter(fig, [0], 'actual', ms=0)

        if self.show_estimates and self.estimated:
            roots = self.estimates['maroots']
            if len(roots):
                rmax1 = add_polar_scatter(fig, roots, 'estimated')
            else:
                rmax1 = 1
        else:
            rmax1 = 1

        maxr = max([1, rmax0, rmax1])
        fig.update_layout(
            title='MA inverse roots',
            polar={'angularaxis': {'thetaunit': 'radians', 'dtick': np.pi / 4},
                   'radialaxis': {'tickvals': [0.0, 1.0], 'range': [0, maxr]}}
        )
        return fig

    def plot_irf(self, horizon):

        df = pd.DataFrame({'actual':self.impulse_response(horizon)})

        if self.show_estimates and self.estimated:
            df['estimated'] = ARMA_class(self.estimates['c'],
                                         self.estimates['phi'],
                                         self.estimates['theta']).impulse_response(horizon)


        fig = px.bar(df,
                     barmode='group',
                     title='Impulse Response Function',
                     template='simple_white')

        fig.update_layout(
            legend_orientation='h',
            xaxis_title='Lag',
            yaxis_title='IRF'
        )
        return fig



#=======================================================================================================================
#
#  APP STARTS HERE
#
#_______________________________________________________________________________________________________________________
mathjax = ["https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML"]  # to display math
omega = np.linspace(0, np.pi, 121)  # frequencies for spectral plot


app = JupyterDash(__name__,external_stylesheets=external_stylesheets, external_scripts=mathjax)

#======DESIGN THE APP===============

app.layout = html.Div(children=[
    *make_top_banner("The ARMA model"),
    html.Div(children=[html.H4("ARMA Parameters"),
                       html.Table(children=[
                           app_parameter_row('c', 'c', 'number', 0),
                           app_parameter_row('AR', 'AR', 'text', ''),
                           app_parameter_row('MA', 'MA', 'text', ''),
                           app_parameter_row('V[e]', 'vare', 'number', 1.0)],
                       ),
                       html.Hr(),
                       html.H5(id='moments'),
                       html.H4("Figure Parameters"),
                       html.Table(children=[
                           app_parameter_row('Periods', 'periods', 'text', 120, '8'),
                           app_parameter_row('AC-lags', 'lags', 'text', 12, '8'),
                           app_parameter_row('IRF horizon', 'horizon', 'text', 24, '8'),
                           html.Tr([html.Th('Show estimates'),
                                    html.Th(dcc.RadioItems(id='showestimates',
                                                         options=[{'label': 'Yes', 'value': 'Yes'}, {'label': 'No', 'value': 'No'}],
                                                         value='No'))]),
                       ],
                       ),
                       html.Div(id='p,q', children=[html.Tr([*app_parameter('p', 'p', 'text', '0', '5'),
                                                               *app_parameter('q', 'q', 'text', '0', '5')],
                                                              style={'border':'3px dashed SteelBlue'}),
                                                    dash_table.DataTable(
                                                        id='estimate_table',
                                                        columns=[{'name': '  ', 'id': 'param'},
                                                                 {'name': 'coef', 'id': 'coef'},
                                                                 {'name': 'p-value', 'id': 'P>|z|'}],
                                                        data=[])
                                                    ]),
                       html.Hr(),
                       html.Button('PLOT', id='execute',style={'textAlign': 'center', 'backgroundColor': colors['buttons']}),
                       ],
             style={'textAlign': 'center', 'color': colors['controls'], 'width': '20%', 'display': 'inline-block'}),

    html.Div(style={'width': '80%', 'float': 'right', 'display': 'inline-block'},
             children=[
                 # --PLOT 1:  SIMULATED TIME SERIES----------------------------------------------------------------------
                 dcc.Graph(id='plot-process',
                           style={'width': '99%', 'float': 'left', 'display': 'inline-block'}),
                 #--PLOT 2a:  AUTOCORRELOGRAM---------------------------------------------------------------------------
                 dcc.Graph(id='plot-correlogram',
                           style={'width': '33%', 'float': 'left', 'display': 'inline-block'}),
                 #--PLOT 2b:  PARCIAL AUTOCORRELOGRAM---------------------------------------------------------------------------
                 dcc.Graph(id='plot-partial-correlogram',
                           style={'width': '33%', 'float': 'left', 'display': 'inline-block'}),
                 # --PLOT 2c:  IMPULSE RESPONSE FUNCTION----------------------------------------------------------------
                 dcc.Graph(id='plot-irf',
                           style={'width': '33%', 'float': 'left', 'display': 'inline-block'}),
                 #--PLOT 2a:  SPECTRAL DENSITY--------------------------------------------------------------------------
                 dcc.Graph(id='plot-spectrum',
                           style={'width': '39%', 'float': 'left', 'display': 'inline-block'}),
                 #--PLOT 3a:  AR ROOTS----------------------------------------------------------------------------------
                 dcc.Graph(id='plot-ar-roots',
                           style={'width': '30%', 'float': 'left', 'display': 'inline-block'}),
                 # --PLOT 3b:  IMPULSE RESPONSE FUNCTION----------------------------------------------------------------
                 dcc.Graph(id='plot-ma-roots',
                           style={'width': '30%', 'float': 'left', 'display': 'inline-block'}),
             ]),
    make_bottom_banner('macrodemos.ARMA( )', width=20)
],
style={'backgroundColor': colors['background']})



@app.callback(
    [
        Output('plot-process', 'figure'),
        Output('plot-correlogram', 'figure'),
        Output('plot-partial-correlogram', 'figure'),
        Output('plot-irf', 'figure'),
        Output('plot-spectrum', 'figure'),
        Output('plot-ar-roots', 'figure'),
        Output('plot-ma-roots', 'figure'),
        Output('moments', 'children'),
        Output('moments', 'style'),
        Output('estimate_table','data')
     ],
    [Input('execute', 'n_clicks')],
    [State('c', 'value'),
     State('AR', 'value'),
     State('MA', 'value'),
     State('vare', 'value'),
     State('periods', 'value'),
     State('lags', 'value'),
     State('horizon', 'value'),
     State('showestimates', 'value'),
     State('p', 'value'),
     State('q', 'value'),
     ])
def update_ARMA_parameters(n_clicks, c, phi, theta, sigma2, periods, lags, horizon, showestimates, p, q):
    phi = validate_lists_of_values(phi)
    theta = validate_lists_of_values(theta)
    Y = ARMA_class(c, phi, theta, sigma2, periods)
    Y.sample(int(periods) + 1)
    style = {'textAlign': 'center', 'color': colors['text'] if Y.isstationary else 'red'}
    Y.show_estimates = (showestimates == 'Yes')
    if Y.show_estimates:
        Y.estimate(int(p), int(q))

    return [
        Y.plot_process(),
        Y.plot_correlogram(lags=int(lags)),
        Y.plot_partial_correlogram(lags=int(lags)), #FIXME
        Y.plot_irf(horizon=int(horizon)),
        Y.plot_spectral(),
        Y.plot_ar_roots(),
        Y.plot_ma_roots(),
        Y.print2moments(),
        style,
        Y.estimated_table
    ]



@app.callback(
    [Output('p,q', 'children'),
     Output('p,q', 'style')],
    [Input('showestimates', 'value')],
    [State('AR', 'value'),
     State('MA', 'value')])
def show_pq_options(showestimates, phi, theta):
    phi = validate_lists_of_values(phi)
    theta = validate_lists_of_values(theta)
    Y = ARMA_class(0, phi, theta, 1.0)
    p, q = Y.p, Y.q
    children = [html.Tr([*app_parameter('p', 'p', 'text', p, '4'),
                        *app_parameter('q', 'q', 'text', q, '4')],
                       style={'border':'3px dashed SteelBlue'}),
                dash_table.DataTable(
                    id='estimate_table',
                    columns=[{'name': '  ', 'id': 'param'},
                             {'name': 'coef', 'id': 'coef'},
                             {'name': 'p-value', 'id': 'P>|z|'}],
                    data=[],
                    style_cell=editable_cell_format
                )
                ]
    style = {'display': 'none'} if (showestimates == 'No') else {'border': '3px dashed SteelBlue'}
    return children, style




def ARMA(colab=False):
    if colab:
        app.run_server(mode='external')
    else:
        webbrowser.open('http://127.0.0.1:8050/')
        app.run_server(debug=False)

ARMA_demo = ARMA  # kept for backward compatibility


if __name__ == '__main__':
    ARMA()

