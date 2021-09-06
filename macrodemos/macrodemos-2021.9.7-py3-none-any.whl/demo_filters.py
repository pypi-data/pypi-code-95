"""
demo_filters: Module for learning about time series filters to measure the business cycle

This module provides a single function, filters(), which creates a dash consisting of 3 tabs with a single plot in
each of them, to compare the business cycle measurement implied by different filters. The plots display
    1. The original data and trend
    2. the cyclical component
    3. the comovement with GPD

This demo considers four time series filters
    1. Hodrick Prescott
    2. Baxter King
    3. Christiano Fitzgerald
    4. Hamilton

So far, the demo works with national accounts data from only 2 countries
    1. Costa Rica
    2. United States

Randall Romero Aguilar
2016-2021
"""


from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
#import dash_bootstrap_components as dbc  #conda install -c conda-forge dash-bootstrap-components
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px

from macrodemos.common_components import app_parameter_row, app_choose_parameter, \
    colors, make_bottom_banner, make_top_banner

from statsmodels.formula.api import ols
import webbrowser

import numpy as np
import pandas as pd
from scipy.linalg import toeplitz

import requests
import bs4 as bs
import os

pd.core.common.is_list_like = pd.api.types.is_list_like


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']



"""==========================================================================================================
IMF IFS data
"""
def as_url_list(param):
    if type(param) is str:
        param = [param]
    return '+'.join(param)

def make_IFS_series(xmlseries: bs.element.Tag):
    ref_area = xmlseries['ref_area']
    date0 = xmlseries.find('obs')['time_period']
    values = [float(x['obs_value']) for x in xmlseries.find_all('obs')]
    nobs = len(values)
    dates = pd.period_range(start=date0, freq=xmlseries['freq'], periods=nobs)
    index = pd.MultiIndex.from_product([[ref_area], dates], names=['ref_area', 'time_period'])
    return pd.Series(values, index=index, name=xmlseries['indicator'])


def make_IFS_dataframe(xmldataset: bs.element.Tag):
    allseries = [make_IFS_series(x) for x in xmldataset.find_all('series')]

    indicators = set([series.name for series in allseries])

    data_by_indicator = {indicator: list() for indicator in indicators}

    for series in allseries:
        data_by_indicator[series.name].append(series)

    for indicator in indicators:
        data_by_indicator[indicator] = pd.concat(data_by_indicator[indicator], axis=0)

    return pd.concat([data_by_indicator[indicator] for indicator in indicators], sort=True, axis=1)


def read_IFS(indicator, ref_area, frequency='M', startPeriod=None, endPeriod=None):
    IFS_ROOT_URL = 'http://dataservices.imf.org/REST/SDMX_XML.svc/CompactData/IFS/'
    params = dict(startPeriod=startPeriod, endPeriod=endPeriod)

    # Convert parameters to url lists
    indicator = as_url_list(indicator)
    ref_area = as_url_list(ref_area)


    url = IFS_ROOT_URL + '.'.join([frequency, ref_area, indicator])
    print(f'Downloading data from {url}')

    response = requests.get(url=url, params=params)

    # Data transformation

    if response.status_code == 200:
        soup = bs.BeautifulSoup(response.content, features='lxml')
        if soup.find('series'):  # True if at least 1 series in dataset
            return make_IFS_dataframe(soup.find('dataset'))
        else:
            print('Error: No available records, please change parameters')
    else:
        print('Error: %s' % response.status_code)
        print(response.url)




"""==========================================================================================================
DATAFILE contains the raw data to be filtered
"""
DATAFILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'IFS_GDP.xlsx')
AVAILABLE_COUNTRIES = pd.read_excel(DATAFILE, 'Countries')

AVAILABLE_COUNTRIES.set_index(['ISO', 'NAME'], inplace=True)
AVAILABLE_COUNTRIES = AVAILABLE_COUNTRIES[AVAILABLE_COUNTRIES.sum(axis=1)>0]
AVAILABLE_COUNTRIES = AVAILABLE_COUNTRIES.astype(bool)
AVAILABLE_COUNTRIES.reset_index(inplace=True)
AVAILABLE_COUNTRIES.set_index('ISO', inplace=True)

INDICATORS = pd.read_excel(DATAFILE, 'Indicators')


def get_iso(country):
    return AVAILABLE_COUNTRIES[AVAILABLE_COUNTRIES['NAME'] == country].index[0]


def get_data(country, datatype):
    iso = get_iso(country)

    freq = 'Q'
    indic = INDICATORS[['NAME', datatype]]

    indic.dropna(how='any', inplace=True)
    indic.set_index(datatype, inplace=True)

    datos = read_IFS(indic.index.to_list(), iso, freq).loc[iso]
    datos.index = datos.index.to_timestamp()
    column_order = [x for x in indic.index if x in datos.columns]
    datos = datos[column_order]
    datos.rename(columns=indic['NAME'].to_dict(), inplace=True)

    datos = datos.div(datos['Deflator'], axis='rows')

    del datos['Deflator']
    return datos.dropna(how='any')


"""==========================================================================================================
This block defines all filters
"""
def HP_filter(x: pd.DataFrame, lambda_: float):
    """
    Returns the Hodrick-Prescott trend
    :param x: data
    :param lambda_: smoothing parameter
    :return: two pd.DataFrame with trend and cycle data
    """
    T = x.shape[0]
    A = np.zeros((T-2, T))
    for i in range(T-2):
        A[i, i:i+3] = 1, -2, 1
    B = np.identity(T) + lambda_ * (A.T @ A)
    trend = np.linalg.solve(B, np.log(x))
    trend = pd.DataFrame(np.exp(trend), index=x.index, columns=x.columns)
    return trend, 100*(x/trend - 1)

def BK_filter(x: pd.DataFrame, K:int=8, pL=6, pH=32):
    """
    Baxter-King filter

    :param x: data to be filtered
    :param pL: cut-off low-periodicity, integer
    :param pH: cut-off high-periodicity, integer
    :param K: number of leads and lags for moving average approximation
    :return: two pd.DataFrame with trend and cycle data
    """
    pL, pH = (pH, pL) if pL > pH else (pL, pH)
    wh, wl = 2 * np.pi / np.array([pL, pH])
    h = np.arange(1, K+1)  # lags   
    beta = (np.sin(h*wh) - np.sin(h*wl)) / (h*np.pi)
    beta = np.r_[beta[::-1], (wh-wl)/np.pi, beta]
    beta -= beta.mean()  # weights add-up to zero
    m = beta.size # = 2*K + 1

    xcycle = np.log(x).rolling(m, min_periods=m, center=True).apply(lambda df: beta.dot(df), raw=True)
    xtrend = np.log(x) - xcycle
    return np.exp(xtrend), 100*xcycle


def CF_filter(x: pd.DataFrame, pL=6, pH=32, undrift=True):
    """
    Christiano Fitzgerald asymmetric, random walk filter.

    :param x: data to be filtered
    :param pL: cut-off low-periodicity, integer
    :param pH: cut-off high-periodicity, integer
    :param undrift: whether to remove the drift, bool
    :return: two pd.DataFrame with trend and cycle data

    Note: ported from Matlab code posted by authors at https://www.frbatlanta.org/cqer/research/bpf.aspx
    """
    T = x.shape[0]
    t = np.arange(T)
    t1 = t[1:]

    pL, pH = (pH, pL) if pL > pH else (pL, pH)
    wh, wl = 2 * np.pi / np.array([pL, pH])

    # remove the drift
    logx = np.log(x)
    if undrift:
        drift = (logx.iloc[-1] - logx.iloc[0]) / (T - 1)
        Xun = logx - np.outer(t, drift)
    else:
        Xun = logx

    # create ideal betas then construct AA matrix
    bnot = (wh - wl) / np.pi
    bhat = bnot / 2

    beta = np.r_[bnot, (np.sin(t1 * wh) - np.sin(t1 * wl)) / (t1 * np.pi)]
    AA = toeplitz(beta, beta)
    AA[0, 0] = AA[-1, -1] = bhat

    AA[1:, 0] = AA[0, 0] - beta[:-1].cumsum()
    AA[:-1, -1] = np.flip(AA[:-1, 0] - beta[:-1])

    xcycle = AA @ Xun
    xcycle.index = x.index

    xtrend = logx - xcycle
    return np.exp(xtrend), 100 * xcycle


def Hamilton_filter(y: pd.DataFrame, h=8, p=4):
    """
    Calculates the cyclical component based on 2-year-ahead forecast error
    from linear regression.

    Input:
        y: a vector of data, pd.Series
        h: forecast horizon, in quarters
        p: lags in regression

    """
    cycle = 0 * y # quick way to copy data structure
    ly = np.log(y)

    for serie in ly:
        data = ly[[serie]].copy()
        data.columns = ['y']
        for j in range(p):
            data[f'L{h + j}y'] = data['y'].shift(h + j)
        frml = 'y ~ ' + ' + '.join(data.columns[1:])
        cycle[serie] = ols(frml, data).fit().resid

    trend = ly - cycle
    return np.exp(trend), 100*cycle


FILTERS = {'HP': HP_filter,
           'BK': BK_filter,
           'CF': CF_filter,
           'H': Hamilton_filter}



"""==========================================================================================================
This block contains auxiliary functions to make it easier to build the app layout
"""

mathjax = ["https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML"]


def parse_parameters(lambda_, K, pL, pH, cfpL, cfpH, undrift, h, p):
    K, h, p = (int(x) for x in [K, h, p])
    lambda_, pL, pH, cfpL, cfpH = (float(x) for x in [lambda_, pL, pH, cfpL, cfpH])
    undrift = undrift=='Yes'
    parameters = {
        'HP': (lambda_, ),
        'BK': (K, pL, pH),
        'CF': (cfpL, cfpH, undrift),
        'H': (h, p),
    }
    return parameters


def add_filtered_data_to_plots(filter, trend_plot, cycle_plot, comovement_data, indicator, *args):
    trend = f"{filter} trend"
    cycle = f"{filter} cycle"
    DATA[trend], DATA[cycle] = FILTERS[filter](DATA['original'], *args)
    trend_plot.add_trace(go.Scatter(x=DATA[trend].index, y=DATA[trend][indicator], name=trend))
    cycle_plot.add_trace(go.Scatter(x=DATA[cycle].index, y=DATA[cycle][indicator], name=cycle))
    comovement_data[filter] = DATA[cycle]
    return None



"""==========================================================================================================
This block builds the app layout
"""
app = JupyterDash(__name__,external_stylesheets=external_stylesheets, external_scripts=mathjax)

app.layout = html.Div(children=[
    *make_top_banner('Filtering of historical time series data'),
    html.Div(children=[html.H4("Choose Series"),
                       html.Table(children=[
                           app_choose_parameter('Country',
                                                'country',
                                                AVAILABLE_COUNTRIES['NAME'].tolist(),
                                                'Costa Rica')]
                       ),
                       html.Table(id='datatype-selector', style={'width': '100%'},
                                  children=[app_choose_parameter(
                                      'Adjusted?',
                                      'datatype',
                                      AVAILABLE_COUNTRIES.loc['CR'].index.to_list(),
                                      'Seasonally Adjusted')]
                       ),
                       html.Table(id='select-indicator', style={'width': '100%'},
                                  children=[app_choose_parameter('Series', 'indicator', 'Costa Rica', 'GDP')]),
                       html.H5(id='moments'),
                       html.H4("Filter Parameters"),
                       dcc.Tabs([
                           dcc.Tab(label='Hodrick-Prescott', style={'padding-left': '0.4em'},
                                   children=[html.Table(children=[app_parameter_row('lambda','lambda','text',1600,'6')])]),
                           dcc.Tab(label='Baxter-King', style={'padding-left': '0.4em'},
                                   children=[html.Table(
                                       children=[app_parameter_row('K', 'K', 'text', 8, '6'),
                                                 app_parameter_row('p_L', 'pL', 'text', 6, '6'),
                                                 app_parameter_row('p_H', 'pH', 'text', 32, '6')],
                                   )]),
                           dcc.Tab(label='Christiano-Fitzgerald', style={'padding-left': '0.4em'},
                                   children=[html.Table(
                                       children=[app_parameter_row('p_L', 'cfpL', 'text', 6, '6'),
                                                 app_parameter_row('p_H', 'cfpH', 'text', 32, '6'),
                                                 html.Tr([html.Th('Remove drift'),
                                                          html.Th(dcc.RadioItems(id='undrift',
                                                                                 options=[{'label': 'Yes', 'value': 'Yes'}, {'label': 'No', 'value': 'No'}],
                                                                                 value='Yes'))]),
                                                 ],
                                   )]),
                           dcc.Tab(label='Hamilton', style={'padding-left': '0.4em'},
                                   children=[html.Table(
                                       children=[app_parameter_row('h', 'h', 'text', 8, '6'),
                                                 app_parameter_row('p', 'p', 'text', 4, '6')]
                                   )]),
                       ]),
                       html.H4("Plot options"),
                       dcc.Checklist(id='what-to-plot',
                                     options=[
                                         {'label': 'Hodrick-Prescott', 'value': 'HP'},
                                         {'label': 'Baxter-King', 'value': 'BK'},
                                         {'label': 'Christiano-Fitzgerald', 'value': 'CF'},
                                         {'label': 'Hamilton', 'value': 'H'},
                                     ],
                                     value=['HP']
                                     ),
                       html.Button('PLOT', id='execute',style={'textAlign': 'center', 'backgroundColor': colors['buttons']}),
                       ],
             style={'textAlign': 'center', 'color': colors['controls'], 'width': '20%', 'display': 'inline-block'}),

    html.Div(style={'width': '80%', 'float': 'right', 'display': 'inline-block'},
             children=[
                 dcc.Tabs([
                     dcc.Tab(label='Trend',
                             children=dcc.Graph(id='plot-trend',
                                                style={'width': '100%', 'float': 'right', 'display': 'inline-block'})),
                     dcc.Tab(label='Cycle',
                             children=dcc.Graph(id='plot-cycle',
                                                style={'width': '100%', 'float': 'right', 'display': 'inline-block'})),
                     dcc.Tab(label='Co-movement',
                             children=dcc.Graph(id='plot-comovement',
                                                style={'width': '100%', 'float': 'right', 'display': 'inline-block'})),
                     dcc.Tab(label='About',
                             children=[
                                 html.Div(style={"background-color": 'white'},
                                          children=[
                                              dcc.Markdown(
                                 """
                                 #### About the filters
                                     
                                   The purpose of this demo is to help you understand several popular time series filtering
                                 methods:  
                                 
                                 * Hodrick and Prescott [(1997)](http://www.jstor.org/stable/2953682) *Postwar U.S. Business Cycles: An Empirical Investigation*
                                 * Baxter and King [(1995)](http://www.jstor.org/stable/2646708) *Measuring Business Cycles: Approximate Band-Pass Filters for Economic Time Series* 
                                 * Christiano and Fitzgerald [(2003)](https://doi.org/10.1111/1468-2354.t01-1-00076) *The Band Pass Filter*
                                 * Hamilton [(2017)](https://doi.org/10.1162/rest_a_00706) *Why You Should Never Use the Hodrick-Prescott Filter*
                                 
                                 
                                 #### About the filter parameters
                                 
                                 For each of this filters, you can choose the filtering parameters and see the filtered trend and cycle, as well as the correlation of the 
                                 cycles of the series with the GDP cycle.
                                 
                                 * Hodrick and Prescott:  **lambda** controls the trend smoothness
                                 * Baxter and King: **K** number of quarters to keep (each side) for computation,  **p_L** and **p_H** number of quarters that define a business cycle 
                                 * Christiano and Fitzgerald: **p_L** and **p_H** number of quarters that define a business cycle
                                 * Hamilton: **h** forecast horizon, **p** number of lags in forecast regression.
                                 
                                 #### About the data
                                 All data is quarterly, and is downloaded from the [IFS database](https://data.imf.org/ifs) (IMF); for this reason, you need an Internet connection to
                                 run this demo. Furthermore, sometimes the IFS API will not return the requested data; in such case try again a few seconds later.
                                 
                                 For each time series, this app downloads the *nominal* values in local currency and computes a *real* time series by dividing by the GDP deflator. The several filters are then 
                                  applied to the *logarithm* of the resulting time series. 
                                  
                                 Countries shown in the dropdown menu are those for which there is data available in IFS.
                                 """)]),
                             ]),
                 ]),
             ]),
    make_bottom_banner('macrodemos.filters( )', width=20)
],
    style={'backgroundColor': colors['background']})


"""==========================================================================================================
This block defines how the app responds to all inputs and states
"""
initial_data = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'CRI-initial-data.csv')
DATA = {'original': pd.read_csv(initial_data, parse_dates=True, index_col=0)}


@app.callback(
    [Output('datatype-selector', 'children')],
    [Input('country', 'value')])
def show_datatypes(country):
    iso = get_iso(country)
    temp = AVAILABLE_COUNTRIES.loc[iso]
    disponibles = temp[temp==True].index.to_list()
    if 'Seasonally Adjusted' in disponibles:
        disponible_inicial = 'Seasonally Adjusted'
    else:
        disponible_inicial = 'Original'
    return [app_choose_parameter('Adjusted', 'datatype', disponibles, disponible_inicial)]


@app.callback(
    [Output('select-indicator', 'children')],
    [Input('country', 'value'),
     Input('datatype', 'value'),],
)
def show_indicators(country, datatype):
    try:
        data = get_data(country, datatype)
        indicators = data.columns
        DATA['original'] = data
    except:
        indicators = DATA['original']
    return [app_choose_parameter('Series', 'indicator', indicators, indicators[0])]



@app.callback(
    [Output('plot-trend', 'figure'),
     Output('plot-cycle', 'figure'),
     Output('plot-comovement', 'figure'),
     ],
    [Input('execute', 'n_clicks'),
     Input('indicator', 'value'),
     Input('what-to-plot', 'value'),
     ],
    [State('lambda', 'value'),
     State('K', 'value'),
     State('pL', 'value'),
     State('pH', 'value'),
     State('cfpL', 'value'),
     State('cfpH', 'value'),
     State('undrift', 'value'),
     State('h', 'value'),
     State('p', 'value'),
     State('country', 'value')
     ]
)
def update_plots(n_clicks, indicator, whichFilters, lambda_, K, pL, pH, cfpL, cfpH, undrift, h, p, country):
    params = parse_parameters(lambda_, K, pL, pH, cfpL, cfpH, undrift, h, p)
    trend = go.Figure()
    cycle = go.Figure()
    comovement_data = dict()

    trend.add_trace(go.Scatter(x=DATA['original'].index, y=DATA['original'][indicator], name="data"))

    for filtro in whichFilters:
        add_filtered_data_to_plots(filtro, trend, cycle, comovement_data, indicator, *params[filtro])

    if whichFilters:
        comovement_data2 = pd.concat(comovement_data.values(), keys=comovement_data.keys())
        comovement_data2.index.names = ['Filter', 'dates']
        comovement_data2 = comovement_data2.reset_index().dropna(how='any')
        dates = [f'{z.year}-Q{z.quarter}' for z in comovement_data2['dates']] #.astype(str)
        comovement = px.scatter(comovement_data2,
                                x=DATA['original'].columns[0],
                                y=indicator,
                                color='Filter',
                                trendline='ols',
                                hover_name=dates)
    else:
        comovement = go.Figure()

    trend.update_layout(title_text=f'Trend: {indicator} in {country}', xaxis_rangeslider_visible=True, height=700)
    cycle.update_layout(title_text=f'Cycle: {indicator} in {country}', xaxis_rangeslider_visible=True, height=700, yaxis_title="% deviation from trend")
    comovement.update_layout(title_text=f'Comovement: {indicator} in {country}', height=700)

    return trend, cycle, comovement



"""==========================================================================================================
This block executes the app
"""

def filters(colab=False):
    if colab:
        app.run_server(mode='external')
    else:
        webbrowser.open('http://127.0.0.1:8050/')
        app.run_server(debug=False)

filters_demo = filters # kept for backward compatibility

if __name__ == '__main__':
    filters()

