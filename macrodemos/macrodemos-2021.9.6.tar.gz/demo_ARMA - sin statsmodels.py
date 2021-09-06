import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import webbrowser

import numpy as np
import pandas as pd
from numpy.polynomial import Polynomial as P

from statsmodels.tsa.arima_model import ARMA as tsaARMA
from statsmodels.tsa.stattools import acf


from warnings import warn

#from filters import HP, HP_SquareGain, BK, BK_SquareGain, Diff, Diff_SquareGain, ideal_filter, Seasonal, Seasonal_SquareGain

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

colors = {
    'background': 'SteelBlue',
    'text': 'White',
    'controls':'#DDDDDD',
    'buttons':'Orange'
}

def qnwsimp(n, a, b):
    """
    Compute univariate Simpson quadrature nodes and weights

    Parameters
    ----------
    n : int
        The number of nodes

    a : int
        The lower endpoint

    b : int
        The upper endpoint

    Returns
    -------
    nodes : np.ndarray(dtype=float)
        An n element array of nodes

    nodes : np.ndarray(dtype=float)
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


#=======================================================================================================================
#
#  ARMA_class CLASS
#
#_______________________________________________________________________________________________________________________
class ARMA:
    def __init__(self, c=0, phi=(0,), theta=(0,), sigma2=1):
        self.phi = phi
        self.theta = theta
        self.c = float(c)  # intercept
        self.sigma2 = float(sigma2)  # white noise variance
        self.simulated_data = None
        self.show_estimates = False
        self.estimates = {'repr': ''}
        self.estimated = False

    @property
    def phi(self):
        return -self.Phi.coef[1:]

    @phi.setter
    def phi(self, value):
        value, one, x = self.__validate_lists_of_values(value)
        self.Phi = one - x * P(value)  # AR polynomial

    @property
    def theta(self):
        return self.Theta.coef[1:]

    @theta.setter
    def theta(self, value):
        value, one, x = self.__validate_lists_of_values(value)

        self.Theta = one + x * P(value)  # MA polynomial

    def __validate_lists_of_values(self, value):
        if len(value) == 0:
            value = 0
        elif type(value) is str:
            value = [float(x) for x in value.split(',')]
        one = P([1])
        x = P([0, 1])
        return value, one, x

    @property
    def roots(self):
        return 1/self.Phi.roots()

    @property
    def p(self):
        return self.Phi.degree()

    @property
    def q(self):
        return self.Theta.degree()

    @property
    def is_stationary(self):
        r = self.roots
        return np.all(abs(r) < 1)

    @property
    def mean(self):
        return self.c / self.Phi(1) if self.is_stationary else np.nan

    @property
    def variance(self):
        frequencies, weights = qnwsimp(121, 0, np.pi)
        sw = self.spectral_density(frequencies)
        return 2 * weights.dot(sw)

    def ARpower(self, w: np.array):
        pp = np.outer(self.Phi.coef, self.Phi.coef)
        amplitude = np.array([pp.diagonal(k).sum() for k in range(self.p + 1)])
        amplitude[1:] *= 2
        return np.cos(np.outer(w, np.arange(amplitude.size))).dot(amplitude)

    def MApower(self, w: np.array):
        pp = np.outer(self.Theta.coef, self.Theta.coef)
        amplitude = np.array([pp.diagonal(k).sum() for k in range(self.q + 1)])
        amplitude[1:] *= 2
        return np.cos(np.outer(w, np.arange(amplitude.size))).dot(amplitude)

    def spectral_density(self, w: np.array):
        if self.is_stationary:
            return self.sigma2 * (self.MApower(w) / self.ARpower(w)) / (2 * np.pi)
        else:
            warn('This ARMA_class(%d,%d) process is not stationary' % (self.p, self.q))
            return np.nan + np.zeros_like(w)



    def autocovariance(self, maxlag=20):
        w, p = qnwsimp(121, 0, np.pi)
        sw = self.spectral_density(w)
        gamma = 2 * np.array([p.dot(sw * np.cos(k * w)) for k in range(maxlag + 1)])
        return gamma

    def autocorrelation(self, maxlag=20):
        gamma = self.autocovariance(maxlag)
        return gamma / gamma[0]

    def __simulate_shocks(self, n, irf=False):
        if irf:
            shocks = np.zeros(n,float)
            shocks[0] = 1.0
        else:
            shocks = np.random.randn(n) * np.sqrt(self.sigma2)
        return shocks

    def __simulate_MA(self, e):
        return np.convolve(self.Theta.coef[::-1], e, 'valid')

    def __simulate_AR(self, e, y0=None):
        if y0 is None:
            y0 = np.zeros(self.p)
            if self.is_stationary:
                y0 += self.mean

        phi = self.phi[::-1]
        p = self.p
        y = np.hstack((y0, np.zeros_like(e)))
        for t, et in enumerate(e):
            y[t + p] = self.c + phi.dot(y[t:(t+p)]) + et
        return y

    def sample(self, n=101, y0=None):
        e = self.__simulate_shocks(n + self.q)
        ma = self.__simulate_MA(e)
        self.simulated_data = pd.Series(self.__simulate_AR(ma, y0))

    def estimate(self, p, q):
        try:
            res = tsaARMA(self.simulated_data.values, order=[p, q]).fit()
            self.estimates = {'c': res.params[0], 'phi': res.arparams, 'theta': res.maparams}
            self.estimates['repr'] = str(ARMA(self.estimates['c'], self.estimates['phi'], self.estimates['theta']))
            self.estimates['fitted'] = pd.Series(res.fittedvalues)
            self.estimates['arroots'] = np.array([1/x for x in res.arroots])
            self.estimated = True
        except:
            self.estimated = False
            self.estimates['repr'] = 'The model could not be estimated'



    def irf(self, n=25):
        p = self.p
        if p == 0:
            response = np.zeros(n, dtype=float)
            response[0] = 1.0
        elif p==1:
            response = self.phi ** np.arange(n)
        else:
            Phi = np.zeros((p, p))
            Phi[0] = self.phi
            Phi[1:, :-1] = np.eye(p-1)
            Response = np.zeros((n, p, p))
            Response[0] = np.eye(p)
            for k in range(n-1):
                Response[k+1] = Response[k] @ Phi
            response = Response[:, 0, 0]
        return response


    def __str__(self):
        c = f'{self.c:g}' if self.c else ''
        if self.p:
            ar = ' '.join([f'{phi:+g}y_{{t-{k+1}}}' for k, phi in enumerate(self.phi) if phi])
        else:
            ar = ''
        if self.q:
            ma = ' '.join([f'{theta:+g}\epsilon_{{t-{k+1}}}' for k, theta in enumerate(self.theta) if theta])
        else:
            ma = ''

        return r'$y_t = ' + c + ar + ' + \epsilon_t' + ma + '$'

    def plot_spectral(self):
        results = {'layout': {'title': 'Spectral Density'}}
        if self.is_stationary:
            results['data'] = [{'x': omega, 'y': self.spectral_density(omega), 'type': 'line', 'name': 'actual', 'fill': 'tozeroy'}]
            if self.show_estimates:
                yy = self.simulated_data - self.simulated_data.mean()
                v = (yy ** 2).mean()  # estimated variance
                T = yy.size
                r = int(np.sqrt(T))
                gamma = acf(yy, unbiased=False, nlags=r, fft=False)
                k = np.arange(r + 1)
                g = 1 - k / r # Bartlett window
                sw = ((np.cos(np.outer(omega, k)) * (g * gamma)).sum(axis=1) * 2 - 1)
                sw *= v / (2 * np.pi)  # rescale
                results['data'].append({'x': omega, 'y': sw, 'type': 'line', 'name': 'estimated'})
        else:
            results['data'] = [{'x': omega, 'y': np.zeros_like(omega), 'type': 'line', 'name': 'not defined'}]
        return results

    def plot_correlogram(self, lags):
        results = dict()
        results['data'] = [{'y': self.autocorrelation(maxlag=lags), 'type': 'bar', 'name': 'actual'}]
        results['layout'] = {'title': 'Autocorrelations'}

        if self.show_estimates:
            self.estimates['acf'] = acf(self.simulated_data, unbiased=True, nlags=lags, fft=False)
            results['data'].append({'y': self.estimates['acf'], 'type': 'bar', 'name': 'estimated'})

        return results

    def plot_process(self):
        y = self.simulated_data.values
        t = np.arange(y.size)
        results = dict()
        results['data'] = [{'x': t, 'y': y, 'type': 'line','name': 'actual'},
                           {'x': [0, t[-1]], 'y': [self.mean, self.mean], 'type':'line','name':r'$\mu$'}]
        results['layout'] = {'title': 'Simulated Data'}
        if self.show_estimates and self.estimated:
            results['data'].insert(1, {'x': t, 'y': self.estimates['fitted'], 'type': 'line','name': 'fitted'})

        """process = go.Figure()
        process.add_trace(go.Scatter(x=t, y=y, name='actual'))
        if self.show_estimates and self.estimated:
            process.add_trace(go.Scatter(x=t, y=self.estimates['fitted'], name='fitted'))
        process.add_trace(go.Scatter(x=[0, t[-1]], y=[self.mean, self.mean], name=r'$\mu$'))
        process.update_layout(title_text='Simulated Data')
        """
        return results #process


    def plot_ar_roots(self):
        results = dict()

        if self.p:
            roots = self.roots
            radium = np.abs(roots)
            angles = np.angle(roots, True)
            results['data'] = [{'r': radium, 'theta': angles, 'type': 'scatterpolar','mode': 'markers', 'marker': {'size': 16}, 'name': 'actual'}]
        else:
            radium = np.ones(2)
            results['data'] = [{'r': [0], 'theta': [0], 'type': 'scatterpolar','mode': 'markers','marker': {'size': 1}, 'name': 'Actual'}]

        if self.show_estimates and self.estimated:
            roots = self.estimates['arroots']
            if len(roots):
                radium2 = np.abs(roots)
                angles2 = np.angle(roots, True)

                results['data'].append(
                    {'r': radium2, 'theta': angles2, 'type': 'scatterpolar', 'mode': 'markers', 'marker': {'size': 16},
                     'name': 'estimated'})
            else:
                radium2 = np.ones(2)
        else:
            radium2 = np.ones(2)

        maxr = max([1, radium.max(), radium2.max()])
        results['layout'] = {'title': 'AR inverse roots',
                             'polar': {'angularaxis': {'thetaunit': 'radians', 'dtick': np.pi / 4},
                                       'radialaxis': {'tickvals': [0.0, 1.0], 'range': [0, maxr]}}
                             }

        return results

    def plot_irf(self, horizon):
        y = self.irf(horizon)
        x = np.arange(y.size)
        result = dict()
        result['data'] = [{'x': x, 'y': y, 'type': 'bar', 'name': 'actual'}]
        result['layout'] = {'title': 'Impulse Response Function'}

        if self.show_estimates and self.estimated:
            temp = ARMA(self.estimates['c'], self.estimates['phi'], self.estimates['theta']).irf(horizon)
            x = np.arange(temp.size)
            result['data'].append({'x': x, 'y': temp, 'type': 'bar', 'name': 'estimated'})
        return result



#=======================================================================================================================
#
#  APP STARTS HERE
#
#_______________________________________________________________________________________________________________________
omega = np.linspace(0, np.pi, 121)

def app_parameter(label, appid, inputtype, value, size='20'):
    return html.Th(label), html.Th(dcc.Input(id=appid, type=inputtype, value=value, size=size))

def app_parameter_row(label, appid, inputtype, value, size='20'):
    return html.Tr([*app_parameter(label, appid, inputtype, value, size)])


mathjax = ["https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML"]

app =  dash.Dash(__name__,external_stylesheets=external_stylesheets, external_scripts=mathjax)


app.layout = html.Div(children=[
    html.H2(id='title',
            style={'textAlign': 'center', 'color': colors['text']}),
    html.P(id='estimated',
            style={'textAlign': 'center', 'color': colors['text']}),
    html.Div(children=[html.H4("ARMA_class Parameters"),
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
                       html.Div(id='p,q', children = [html.Tr([*app_parameter('p', 'p', 'text', '0', '5'),
                                                               *app_parameter('q', 'q', 'text', '0', '5')])]),
                       html.Hr(),
                       html.Button('PLOT', id='execute',style={'textAlign': 'center', 'backgroundColor': colors['buttons']}),
                       html.P('ARMA_class PROCESS DEMO', style={'textAlign': 'center', 'color': colors['text'],'marginTop':500}),
                       ],
             style={'textAlign': 'center', 'color': colors['controls'], 'width': '20%', 'display': 'inline-block'}),

    html.Div(style={'width': '80%', 'float': 'right', 'display': 'inline-block'},
             children=[
                 # --PLOT 1:  SIMULATED TIME SERIES----------------------------------------------------------------------
                 dcc.Graph(id='plot-process',
                           style={'width': '100%', 'float': 'right', 'display': 'inline-block'}),
                 #--PLOT 2a:  SPECTRAL DENSITY--------------------------------------------------------------------------
                 dcc.Graph(id='plot-spectrum',
                           style={'width': '50%', 'float': 'left', 'display': 'inline-block'}),
                 #--PLOT 2b:  AUTOCORRELOGRAM---------------------------------------------------------------------------
                 dcc.Graph(id='plot-correlogram',
                           style={'width': '50%', 'float': 'right', 'display': 'inline-block'}),
                 #--PLOT 3a:  AR ROOTS----------------------------------------------------------------------------------
                 dcc.Graph(id='plot-ar-roots',
                           style={'width': '50%', 'float': 'left', 'display': 'inline-block'}),
                 # --PLOT 3b:  IMPULSE RESPONSE FUNCTION----------------------------------------------------------------
                 dcc.Graph(id='plot-irf',
                           style={'width': '50%', 'float': 'right', 'display': 'inline-block'}),
                 html.A(children='Randall Romero Aguilar', href='mailto:randall.romero@ucr.ac.cr', style={'textAlign': 'center', 'color': colors['text'],'marginBottom':60}),
             ]),
],
style={'backgroundColor': colors['background']})



@app.callback(
    [Output('title', 'children'),
     Output('plot-process', 'figure'),
     Output('plot-spectrum', 'figure'),
     Output('plot-correlogram', 'figure'),
     Output('plot-ar-roots', 'figure'),
     Output('plot-irf', 'figure'),
     Output('moments', 'children'),
     Output('moments', 'style'),
     Output('estimated', 'children'),
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
    Y = ARMA(c, phi, theta, sigma2)
    Y.sample(int(periods) + 1)
    if Y.is_stationary:
        moments = f'$E(y_t) = {Y.mean:g}, V(y_t) = {Y.variance:g}$'
        style = {'textAlign': 'center', 'color': colors['text']}
    else:
        moments = 'This process is not stationay!'
        style = {'textAlign': 'center', 'color': 'red'}

    Y.show_estimates = (showestimates == 'Yes')
    if Y.show_estimates:
        Y.estimate(int(p), int(q))

    return [
        str(Y),
        Y.plot_process(),
        Y.plot_spectral(),
        Y.plot_correlogram(lags=int(lags)),
        Y.plot_ar_roots(),
        Y.plot_irf(horizon=int(horizon)),
        moments,
        style,
        Y.estimates['repr']
    ]


@app.callback(
    [Output('p,q', 'children'),
     Output('p,q', 'style')],
    [Input('showestimates', 'value')],
    [State('AR', 'value'),
     State('MA', 'value')])
def show_pq_options(showestimates, phi, theta):
    Y = ARMA(0, phi, theta, 1)
    p, q = Y.p, Y.q
    children = html.Tr([*app_parameter('p', 'p', 'text', p, '4'),
                        *app_parameter('q', 'q', 'text', q, '4')])
    style = {'display': 'none'} if (showestimates == 'No') else {}
    return children, style



if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:8050/')
    app.run_server(debug=True)

