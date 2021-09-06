
from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
from dash_table import DataTable


import webbrowser

from macrodemos.common_components import app_model_parameter, app_table_headers, editable_cell_format, header_cell_format, \
    make_bottom_banner, colors, make_top_banner


import numpy as np
import pandas as pd


# Esta parte controla asuntos de estética de la página
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


class SolowSwan:
    names = dict(
        A='total productivity of factors',
        s='marginal rate of savings',
        α='marginal product of capital',
        δ='depreciation rate',
        n='population growth rate',
        k='Capital Stock (per capita)',
        y='Output per capita',
        sy='Savings per capita',
        c='Consumption per capita',
        i='Investment per capita',
        Δk='Change in capital stock',
        gy='Output growth rate'
    )

    math_form = dict(
        A=r'$A$',
        s=r'$s$',
        α=r'$\alpha$',
        δ=r'$\delta$',
        n=r'$n$',
        k=r'$k_t$',
        y=r'$y_t$',
        sy=r'$sy_t$',
        c=r'$c_t$',
        i=r'$i_t$',
        Δk=r'$\Delta k_t$',
        gy=r'${g_y}_t$'
    )
    endogenous = ['k', 'y', 'sy', 'c', 'Δk', 'gy']

    def __init__(self, A, s, α, δ, n):
        """

        :param A: float, total productivity of factors
        :param s: float, marginal rate of savings
        :param α: float, marginal product of capital
        :param δ: float, depreciation rate
        :param n: float, population growth rate
        """
        self.A = A
        self.s = s
        self.α = α
        self.δ = δ
        self.n = n
        self.data = None
        self.steady_state = dict()
        self.compute_steady_state()

    @property
    def parameters(self):
        return self.A, self.s, self.α, self.δ, self.n

    def f(self, k):
        return self.A * k ** self.α

    def compute_steady_state(self):
        A, s, α, δ, n = self.parameters

        k = (s * A / (n + δ)) ** (1 / (1 - α))
        y = self.f(k)
        i = (n + δ) * k
        c = y - i

        for name, value in zip('ykic', [y, k, i, c]):
            self.steady_state[name] = value

        self.steady_state['Δk'] = 0.0
        self.steady_state['gy'] = 0.0
        self.steady_state['sy'] = s * y

    def compute_ksteady(self, s):
        A, _, α, δ, n = self.parameters
        k = (s * A / (n + δ)) ** (1 / (1 - α))
        y = self.f(k)
        i = (n + δ) * k
        c = y - i
        return pd.DataFrame({'k': k, 'y': y, 'i': i, 'c': c}, index=s)

    def simulate(self, T, K0=None):
        A, s, α, δ, n = self.parameters

        if K0 is None:
            K0 = self.steady_state['k']

        Y0 = self.f(K0)
        S0 = s * Y0

        K, S, Y = np.zeros([3, T + 1], dtype=float)
        K[0], S[0], Y[0] = K0, S0, Y0

        for t in range(T):
            K[t + 1] = ((1 - δ) * K[t] + S[t]) / (1 + n)
            Y[t + 1] = A * K[t + 1] ** α
            S[t + 1] = s * Y[t + 1]

        datos = pd.DataFrame({'k': K, 'y': Y, 'sy': S})
        datos['c'] = Y - S
        datos['Δk'] = (S - (n + δ) * K) / (1 + n)
        datos.loc[0, 'Δk'] = (S[0] - (self.n + self.δ) * K[0]) / (1 + self.n)
        datos['gy'] = datos['Δk'] * datos['k']

        self.data = datos

    def plot_compare_paths(self, other, ser):
        df = pd.concat([self.data[ser], other.data[ser]],
                       keys=['Baseline', 'Alternative'],
                       axis=1)
        fig = px.line(df,
                      y=df.columns,
                      title=self.names[ser],
                      template='simple_white'
                      )
        fig.update_layout(legend_orientation='h',
                          xaxis_title='',
                          yaxis_title='')

        fig.add_annotation(x=0.1,
                           y=0.9,
                           xref='paper',
                           yref='paper',
                           showarrow=False,
                           text=self.math_form[ser],
                           font=dict(size=30)
                           )
        return fig

    def plot_golden(self, df, ser):
        fig = px.line(df,
                      y=['Baseline', 'Alternative'],
                      title=self.names[ser],
                      template='simple_white'
                      )
        fig.update_layout(#legend_orientation='h',
                          xaxis_title='Savings rate',
                          yaxis_title='')

        fig.add_annotation(x=0.1,
                           y=0.9,
                           xref='paper',
                           yref='paper',
                           showarrow=False,
                           text=self.math_form[ser],
                           font=dict(size=30)
                           )

        return fig

    def plot_compare_golden_rule(self, other):
        s = np.linspace(0, 1, 201)
        df = pd.concat([self.compute_ksteady(s), other.compute_ksteady(s)],
                       axis=1,
                       keys=['Baseline', 'Alternative']).swaplevel(axis=1)

        return [self.plot_golden(df[ser], ser) for ser in 'ciky']

    def plot_compare_steady_state(self, other):

        A0, s0, α0, δ0, n0 = self.parameters
        A1, s1, α1, δ1, n1 = other.parameters

        kmax = max(self.steady_state['k'], other.steady_state['k'])

        k = np.linspace(0, 1.2 * kmax, 201)

        df = pd.DataFrame({
            '$f(k)_0$': self.f(k),
            '$sf(k)_0$': s0 * self.f(k),
            '$(n+δ)k_0$': (n0 + δ0) * k,
            '$f(k)_1$': other.f(k),
            '$sf(k)_1$': s1 * other.f(k),
            '$(n+δ)k_1$': (n1 + δ1) * k},
            index=k)

        fig = px.line(df,
                      y=df.columns,
                      title='Determining the steady-state level of capital',
                      template='simple_white'
                      )
        fig.update_layout(height=600,
                          legend_orientation='h',
                          xaxis_title='$k_t$',
                          yaxis_title='$f(k_t),\quad sf(k_t)$')

        fig.add_annotation(x=self.steady_state['k'],
                           y=self.steady_state['sy'],
                           showarrow=False,
                           text='$k^*_0$',
                           font=dict(size=20)
                           )

        fig.add_annotation(x=other.steady_state['k'],
                           y=other.steady_state['sy'],
                           showarrow=False,
                           text='$k^*_1$',
                           font=dict(size=20)
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
    # TOP BANNER-------
    *make_top_banner('The Solow-Swan Model'),
    # ==================================================================================================================
    #            INICIO DE COLUMNA DE PARÁMETROS
    # ------------------------------------------------------------------------------------------------------------------
    html.Div(
        style={'textAlign': 'center', 'color': colors['controls'], 'width': '25%', 'display': 'inline-block'},
        children=[
            html.H4("Parameters"),
            html.Table(children=[
                app_table_headers(['  ', 'Baseline', 'Alternative']),
                app_model_parameter('α', 0.35, 0.35),
                app_model_parameter('δ', 0.06, 0.06),
                app_model_parameter('n', 0.02, 0.02)]
            ),
            html.Hr(),
            html.H4("Exogenous variables"),
            html.Table(children=[
                app_table_headers(['  ', 'Baseline', 'Alternative']),
                app_model_parameter('A', 1.0, 1.0),
                app_model_parameter('s', 0.2, 0.2)]
                ),
            html.Hr(),
            html.H4("Steady state"),
            html.Div(id='output-data-upload', children=[
            DataTable(
                id='table-transition-matrix',
                columns=([{'id': p, 'name': p} for p in ['Variable', 'Baseline', 'Alternative', '% change']]),
                editable=False,
                #style_table={'width': '75%'},
                style_cell=editable_cell_format,
                style_header=header_cell_format
            )
        ],
                 ),
        html.Hr(),
        html.H4("Figure parameter"),
        html.Table(children=[
            html.Tr([html.Th('Number of periods'), dcc.Input(id='horizon', type='text', value=60, size='10')])]
        ),
        html.Button('PLOT', id='execute',style={'textAlign': 'center', 'backgroundColor': colors['buttons']}),
        html.P('Based on chapter 9 of Bongers, Gómez and Torres (2019) Introducción a la Macroeconomía Computacional. Vernon Press.',
               style={'textAlign': 'left', 'color': colors['text'],'marginTop':20}),
    ],
        ),
    # ==================================================================================================================
    #            INICIO DE COLUMNA DE RESULTADOS
    # ------------------------------------------------------------------------------------------------------------------
    html.Div(style={'width': '75%', 'float': 'right', 'display': 'inline-block'},
             children=[dcc.Tabs([
                 # Panel 1: Simulation==================================================================================
                 dcc.Tab(label="Simulations",
                         children=[
                             # --PLOT 1a:  capital stock----------------------------------------------------------------
                             dcc.Graph(id='path-capital',
                                       style={'width': '49%', 'float': 'left', 'display': 'inline-block'}),
                             #--PLOT 1b:  output per capita ------------------------------------------------------------
                             dcc.Graph(id='path-output',
                                       style={'width': '49%', 'float': 'left', 'display': 'inline-block'}),
                             #--PLOT 1c: savings------------------------------------------------------------------------
                             dcc.Graph(id='path-savings',
                                       style={'width': '49%', 'float': 'left', 'display': 'inline-block'}),
                             # --PLOT 2a:  consumption------------------------------------------------------------------
                             dcc.Graph(id='path-consumption',
                                       style={'width': '49%', 'float': 'left', 'display': 'inline-block'}),
                             #--PLOT 2b: change in capital--------------------------------------------------------------
                             dcc.Graph(id='path-delta-capital',
                                       style={'width': '49%', 'float': 'left', 'display': 'inline-block'}),
                             #--PLOT 2c:  Growth rate ------------------------------------------------------------------
                             dcc.Graph(id='path-growth',
                                       style={'width': '49%', 'float': 'left', 'display': 'inline-block'})
                         ]),
                 # Panel 2: Equilibrium=================================================================================
                 dcc.Tab(label="Equilibrium",
                         children=[
                             # --PLOT 1a:  Equilibrium----------------------------------------------------------------
                             dcc.Graph(id='model-equilibrium',
                                       style={'width': '98%', 'float': 'left', 'display': 'inline-block'}),
                         ]
                         ),
                 # Panel 3: Golden Rule=================================================================================
                 dcc.Tab(label="Golden Rule",
                         children=[
                             # --PLOT 1a:  capital stock----------------------------------------------------------------
                             dcc.Graph(id='golden-capital',
                                       style={'width': '49%', 'float': 'left', 'display': 'inline-block'}),
                             #--PLOT 1b:  output per capita ------------------------------------------------------------
                             dcc.Graph(id='golden-output',
                                       style={'width': '49%', 'float': 'left', 'display': 'inline-block'}),
                             #--PLOT 1c: savings------------------------------------------------------------------------
                             dcc.Graph(id='golden-savings',
                                       style={'width': '49%', 'float': 'left', 'display': 'inline-block'}),
                             # --PLOT 2a:  consumption------------------------------------------------------------------
                             dcc.Graph(id='golden-consumption',
                                       style={'width': '49%', 'float': 'left', 'display': 'inline-block'}),
                         ]
                         ),
             ]), # end of Tabs
             ]),
    make_bottom_banner("macrodemos.Solow( )")
],
    style={'backgroundColor': colors['background']})


@app.callback(
    [Output('path-capital', 'figure'),
     Output('path-output', 'figure'),
     Output('path-savings', 'figure'),
     Output('path-consumption', 'figure'),
     Output('path-delta-capital', 'figure'),
     Output('path-growth', 'figure'),
     Output('table-transition-matrix', 'data'),
     Output('golden-capital', 'figure'),
     Output('golden-output', 'figure'),
     Output('golden-savings', 'figure'),
     Output('golden-consumption', 'figure'),
     Output('model-equilibrium', 'figure'),
     ],
    [Input('execute', 'n_clicks')],
    [State('horizon','value'),
     State('base_α', 'value'),
     State('base_δ', 'value'),
     State('base_n', 'value'),
     State('base_A', 'value'),
     State('base_s', 'value'),
     State('scen_α', 'value'),
     State('scen_δ', 'value'),
     State('scen_n', 'value'),
     State('scen_A', 'value'),
     State('scen_s', 'value')])
def update_Solow_parameters(n_clicks,T, α, δ, n, A, s, α1, δ1, n1, A1, s1):
    # baseline scenario
    baseline = SolowSwan(*[float(xx) for xx in (A, s, α, δ, n)])
    baseline.simulate(T=int(T))

    #alternative scenario
    alternative = SolowSwan(*[float(xx) for xx in (A1, s1, α1, δ1, n1)])
    alternative.simulate(T=int(T), K0=baseline.steady_state['k'])

    # Plots for TAB Simulation
    simulation_plots = [baseline.plot_compare_paths(alternative,ser) for ser in baseline.endogenous]

    # Plots for TAB Golden
    golden_plots = baseline.plot_compare_golden_rule(alternative)

    #Plot for TAB Equilibrium
    equilibrium_plots = [baseline.plot_compare_steady_state(alternative)]

    # Table to compare the steady-states of baseline v. alternative
    df = pd.DataFrame({'Baseline': [v for v in baseline.steady_state.values()],
                      'Alternative': [v for v in alternative.steady_state.values()]},
                      index=baseline.steady_state.keys()
                      )
    df['% change'] = 100 * (df['Alternative'] / df['Baseline'] - 1)
    df = df.round(3).loc[baseline.endogenous]
    df.index.name = 'Variable'
    steady_state_table = [df.reset_index().to_dict('records')]

    return simulation_plots + steady_state_table + golden_plots + equilibrium_plots




def Solow(colab=False):
    if colab:
        app.run_server(mode='external')
    else:
        webbrowser.open('http://127.0.0.1:8050/')
        app.run_server(debug=False)


Solow_demo = Solow # kept for backward compatibility

if __name__ == '__main__':
    Solow()