
from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
import plotly.express as px
import webbrowser
from warnings import warn

from macrodemos.common_components import app_parameter_row, editable_cell_format, header_cell_format, \
    colors, make_top_banner, make_bottom_banner

import numpy as np
import pandas as pd



# Esta parte controla asuntos de estética de la página
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']






class MarkovChain:

    def __init__(self, P, pi0=None, z=None):
        """

        Parameters
        ----------
        P   transition probability matrix, n.n
        pi0 initial distribution, n vector
        z   stochastic outcomes, n vector
        """
        P = np.atleast_2d(P)
        n, n2 = P.shape
        assert n == n2, "P must be a square array"
        assert np.all(P >= 0), "P elements must be nonnegative"
        assert np.allclose(P.sum(1), 1), "The rows of P must sum to 1"

        self.P = P
        self.n = n
        self.cdf = P.cumsum(1)

        if pi0 is None:
            self.pi0 = self.stationary_distribution if self.has_unique_stationary_distribution else np.ones((n) ) /n
        else:
            pi0 = np.asarray(pi0)
            assert pi0.ndim == 1 and pi0.size == n, "pi0 must be a vector with %d elements" % n
            assert np.all(pi0 >= 0), "pi0 elements must be nonnegative"
            assert np.allclose(pi0.sum(), 1), "The elements of pi0 must sum to 1"
            self.pi0 = pi0

        if z is None:
            self.outcomes = np.arange(n)
        else:
            z = np.asarray(z)
            assert z.ndim == 1 and z.size == n, "z must be a vector with %d elements" % n
            self.outcomes = z

        self.string_outcomes = isinstance(self.outcomes[0], str)

    @property
    def stationary_distribution(self):
        if self.has_unique_stationary_distribution:
            A = np.vstack((np.eye(self.n ) -self.P.T, np.ones((1 ,self.n))))
            b = np.hstack((np.zeros(self.n), np.ones((1))))
            return np.linalg.lstsq(A ,b)[0]
        else:
            warn("This Markov process does not have a unique stationary distribution")

    @property
    def has_unique_stationary_distribution(self):  # fixme: ugly implementation
        pn = self.P
        for it in range(50):
            if np.any(pn == 0.0):
                pn = pn @ self.P
            else:
                return True

        return False

    def rand(self, j):
        """
        Draw next state
        Parameters
        ----------
        j current state, integer = 0, 1,...,n-1

        Returns
        -------
        Integer: next state
        """
        return (np.random.rand() > self.cdf[j]).sum()

    def simulate(self, T: int = 120, j: int = 0):
        """
        Simulate the Markov process
        Parameters
        ----------
        T
        j

        Returns
        -------
        Vector: array of simulated values
        """
        assert j in range(self.n), 'Initial state must be a nonnegative integer less than %d' % self.n

        y = np.empty((1 + T))
        y[0] = j if self.string_outcomes else self.outcomes[j]
        for t in range(T):
            j = self.rand(j)
            y[t + 1] = j if self.string_outcomes else self.outcomes[j]

        return y

    def unconditional_distribution(self, T=24):
        prob = np.empty(( T +1, self.n))
        prob[0] = self.pi0
        for t in range(T):
            prob[t + 1] = np.dot(prob[t], self.P)
        df = pd.DataFrame(prob, columns=self.outcomes)
        df.index.name = 'Period'
        return df


    def plot(self, T=120):

        j = (np.random.rand() > self.pi0.cumsum()).sum() # initial state

        fig = px.line(y=self.simulate(T, j),
                      title='Simulated path',
                      line_shape='hv',
                      template='simple_white'
                      )

        fig.update_layout(
            legend_orientation='h',
            yaxis = dict(
                title='',
                tickvals=np.arange(self.n),
                ticktext=self.outcomes,
                range=[self.n - 0.8, -0.2]),
            xaxis_title='Period'
        )
        return fig



    def plot_probability(self, T=24):
        fig = px.bar(self.unconditional_distribution(T),
                     title='Unconditional probability',
                     template='simple_white')
        fig.update_layout(yaxis_title='Probability',
                          legend_orientation = 'h')
        return fig



    def __repr__(self):
        txt = 'A Markov Chain process with transition probability\n'
        txt += self.P.__str__()
        txt += '\n\nand possible outcomes\n'
        txt += self.outcomes.__str__()
        return txt

    # =======================================================================================================================
#
#  APP STARTS HERE
#
# _______________________________________________________________________________________________________________________
mathjax = ["https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML"]  # to display math
omega = np.linspace(0, np.pi, 121)  # frequencies for spectral plot




def make_the_app(states):
    n_states = len(states)

    app = JupyterDash(__name__ ,external_stylesheets=external_stylesheets, external_scripts=mathjax)

    # ======DESIGN THE APP===============

    app.layout = html.Div(children=[
        *make_top_banner(f'Markov Chain with {n_states} states'),
        html.Div(children=[html.H4("Transition matrix"),
                           dash_table.DataTable(
                               id='table-row-headers',
                               columns=([{'id': 'State', 'name': 'State'}]),
                               data=[dict(State=param) for param in states],
                               editable=False,
                               style_table={'width' :'20%', 'float' :'left'},
                               style_cell=header_cell_format
                           ),
                           dash_table.DataTable(
                               id='table-transition-matrix',
                               columns=([{'id': p, 'name': p} for p in states]),
                               data=[dict(**{param: x for param, x in zip(states, fila)})
                                     for fila in np.identity(n_states)],
                               editable=True,
                               style_table={'width' :'75%'},
                               style_cell=editable_cell_format,
                               style_header=header_cell_format
                           ),
                           html.Hr(),
                           html.H4("Initial probability"),
                           dash_table.DataTable(
                               id='table-row-headers0',
                               columns=([{'id': 'State0', 'name': 'State'}]),
                               data=[dict(State0=param) for param in states],
                               editable=False,
                               style_table={'width': '20%', 'float': 'left'},
                               style_cell=header_cell_format
                           ),
                           dash_table.DataTable(
                               id='table-states0',
                               columns=([{'id': 'Prob0',  'name': 'Probability'}]),
                               data=[dict(Prob0=x) for x in np.ones(n_states ) /n_states],
                               editable=True,
                               style_table={'width' :'50%'},
                               style_cell=editable_cell_format,
                               style_header=header_cell_format
                           ),
                           html.Hr(),
                           html.H4("Figure parameter"),
                           html.Table(children=[
                               app_parameter_row('Number of periods, simulations', 'horizon', 'text', 120, '10'),
                               app_parameter_row('Number of periods, distribution', 'horizon2', 'text', 32, '10'),
                           ]),
                           html.Button('PLOT', id='execute'
                                       ,style={'textAlign': 'center', 'backgroundColor': colors['buttons']}),
                           ],
                 style={'textAlign': 'center', 'color': colors['controls'], 'width': '25%', 'display': 'inline-block'}),

        html.Div(style={'width': '75%', 'float': 'right', 'display': 'inline-block'},
                 children=[
                     # --PLOT 1a:  capital stock----------------------------------------------------------------------------
                     dcc.Graph(id='plot-capital',
                               style={'width': '100%', 'display': 'inline-block'}),
                     # --PLOT 1b:  output per capita ------------------------------------------------------------------------------
                     dcc.Graph(id='plot-output',
                               style={'width': '100%',  'display': 'inline-block'}),
                 ]),
        make_bottom_banner("macrodemos.Markov('state 0', 'state 1',...,'state n')")
    ],
        style={'backgroundColor': colors['background']})


    @app.callback(
        [Output('plot-capital', 'figure'),
         Output('plot-output', 'figure'),
         ],
        [Input('execute', 'n_clicks')],
        [State('horizon', 'value'),
         State('horizon2', 'value'),
         State('table-transition-matrix', 'data'),
         State('table-states0', 'data') ,])
    def update_Markov_parameters(n_clicks, T, T2, data, pi0data):


        P = pd.DataFrame(data).astype(float)
        states = P.columns
        pi0 = pd.DataFrame(pi0data).iloc[: ,0].astype(float).values
        markov = MarkovChain(P, pi0, states)

        return [markov.plot(int(T)), markov.plot_probability(int(T2))]

    return app

def Markov(*states, colab=False):
    app = make_the_app([str(x) for x in states])
    if colab:
        app.run_server(mode='external')
    else:
        webbrowser.open('http://127.0.0.1:8050/')
        app.run_server(debug=False)

Markov_demo = Markov


if __name__ == '__main__':
    Markov('state 0', 'state 1')