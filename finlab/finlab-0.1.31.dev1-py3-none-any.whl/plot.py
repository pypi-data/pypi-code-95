import pandas as pd
from finlab import data
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
from talib import abstract
import numpy as np

"""
Candles
"""


def average(series, n):
    return series.rolling(n, min_periods=int(n / 2)).mean()


def create_bias_df(df, ma_value=20, bias_multiple=2):
    bias_df = pd.DataFrame()
    ma_col_name = f'ma{ma_value}'
    bias_df[ma_col_name] = average(df['close'], ma_value)
    std = df['close'].rolling(ma_value, min_periods=int(ma_value / 2)).std()
    bias_df['up_band'] = bias_df[ma_col_name] + std * bias_multiple
    bias_df['down_band'] = bias_df[ma_col_name] - std * bias_multiple
    return bias_df


def create_stoch_df(df, **kwargs):
    kd = abstract.STOCH(df['high'], df['low'], df['close'], **kwargs)
    kd = pd.DataFrame({'k': kd[0], 'd': kd[1]}, index=df.index)
    return kd


def plot_candles(stock_id, close, open_, high, low, volume, recent_days=400, resample='D', overlay_func=None,
                 technical_func=None):
    volume = volume.iloc[-recent_days:]
    if stock_id not in volume.columns:
        print('stock_id is not existed')
        return None
    else:
        volume = volume[stock_id]

    if resample.upper() != 'D':
        close = close.resample(resample).last()
        open_ = open_.resample(resample).first()
        high = high.resample(resample).max()
        low = low.resample(resample).min()
        volume = volume.resample(resample).sum()
    index_value = close.index
    df = pd.DataFrame({'close': close.ffill(), 'open': open_.ffill(), 'high': high.ffill(), 'low': low.ffill(),
                       'volume': volume.ffill()}, index=index_value)

    if overlay_func is None:
        overlay_ind = create_bias_df(df)
    else:
        overlay_ind = pd.DataFrame(index=df.index)
        for overlay_name, overlay_lambda in overlay_func.items():
            overlay_ind[overlay_name] = overlay_lambda(df)

    if technical_func is None:
        tech_ind = create_stoch_df(df)
    else:
        tech_ind = pd.DataFrame(index=df.index)
        for tech_name, tech_lambda in technical_func.items():
            tech_ind[tech_name] = tech_lambda(df)

    # plot
    fig = make_subplots(
        rows=3,
        specs=[[{"rowspan": 2, "secondary_y": True}],
               [None],
               [{}]],
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=(f'{stock_id} Candle Plot', "Technical Plot"))

    fig.add_trace(
        go.Bar(x=index_value, y=volume, marker_color='orange', opacity=0.4, name="volume"),
        row=1, col=1
    )

    fig.add_trace(go.Candlestick(x=close.index,
                                 open=open_,
                                 high=high,
                                 low=low,
                                 close=close,
                                 increasing_line_color='#ff5050',
                                 decreasing_line_color='#009900',
                                 name="candle",
                                 ), row=1, col=1, secondary_y=True)

    # overlay plot
    fig_overlay = px.line(overlay_ind)
    for o in fig_overlay.data:
        fig.add_trace(go.Scatter(x=o['x'], y=o['y'], name=o['name'], line=dict(color=o['line']['color'], width=1.5)),
                      row=1, col=1, secondary_y=True)

    # tech plot
    fig_tech = px.line(tech_ind)
    for t in fig_tech.data:
        fig.add_trace(go.Scatter(x=t['x'], y=t['y'], name=t['name'], line=dict(color=t['line']['color'], width=1.5)),
                      row=3, col=1)

    # hide holiday
    if resample.upper() == 'D':
        dt_all = pd.date_range(start=index_value[0], end=index_value[-1])
        # retrieve the dates that ARE in the original datset
        dt_obs = [d.strftime("%Y-%m-%d") for d in pd.to_datetime(index_value)]
        # define dates with missing values
        dt_breaks = [d for d in dt_all.strftime("%Y-%m-%d").tolist() if d not in dt_obs]
        # hide dates with no values
        fig.update_xaxes(rangebreaks=[dict(values=dt_breaks)])

    fig.update_layout(
        height=800,
        xaxis2=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label="1m",
                         step="month",
                         stepmode="backward"),
                    dict(count=3,
                         label="3m",
                         step="month",
                         stepmode="backward"),
                    dict(count=6,
                         label="6m",
                         step="month",
                         stepmode="backward"),
                    dict(count=1,
                         label="1y",
                         step="year",
                         stepmode="backward"),
                    dict(count=1,
                         label="YTD",
                         step="year",
                         stepmode="todate"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(
                visible=True,
                thickness=0.1,
                bgcolor='gainsboro'
            ),
            type="date",
        ),

        yaxis=dict(
            title="vol",
            titlefont=dict(
                color="#ff9000"
            ),
            tickfont=dict(
                color="#ff9000"
            )
        ),
        yaxis2=dict(
            title="price",
            titlefont=dict(
                color="#d62728"
            ),
            tickfont=dict(
                color="#d62728"
            ),
            showgrid=False
        ),
        hovermode='x unified',
    )

    fig.update_traces(xaxis='x2')
    fig.update_xaxes(showspikes=True)
    fig.update_yaxes(showspikes=True)
    return fig.show()


def plot_tw_stock_candles(stock_id, recent_days=400, adjust_price=False, resample='D', overlay_func=None,
                          technical_func=None):
    """Plot candle_plot for tw_stock
    Args:
      stock_id(str): Target id in tw stock market ex:2330.
      recent_days(int):The length of the data you want to see before today.
      adjust_price(bool):Control to use adjust_price.
      resample(str): Data freq.
      overlay_func(dict): Add additional data series to overlay on top of pricing.
                          ex: {
                                'ema_5':lambda df:abstract.EMA(df['close'],timeperiod=5),
                                'ema_10':lambda df:abstract.EMA(df['close'],timeperiod=10),
                                'ema_20':lambda df:abstract.EMA(df['close'],timeperiod=20),
                                'ema_60':lambda df:abstract.EMA(df['close'],timeperiod=60),
                                  }
      technical_func(dict): Add additional technical indicator series as subplot.
                            ex: {
                                  'rsi_10':lambda df:abstract.RSI(df['close'],timeperiod=10),
                                  'rsi_20':lambda df:abstract.RSI(df['close'],timeperiod=20),
                                  }
    Returns:
        subplot:Candle subplot and technical indicator subplot
    """
    if adjust_price:
        close = data.get('etl:adj_close').iloc[-recent_days:][stock_id]
        open_ = data.get('etl:adj_open').iloc[-recent_days:][stock_id]
        high = data.get('etl:adj_high').iloc[-recent_days:][stock_id]
        low = data.get('etl:adj_low').iloc[-recent_days:][stock_id]
    else:
        close = data.get('price:收盤價').iloc[-recent_days:][stock_id]
        open_ = data.get('price:開盤價').iloc[-recent_days:][stock_id]
        high = data.get('price:最高價').iloc[-recent_days:][stock_id]
        low = data.get('price:最低價').iloc[-recent_days:][stock_id]
    volume = data.get('price:成交股數').iloc[-recent_days:]

    return plot_candles(stock_id, close, open_, high, low, volume, recent_days=recent_days, resample=resample,
                        overlay_func=overlay_func, technical_func=technical_func)


"""
Treemap
"""


def df_date_filter(df, start=None, end=None):
    if start:
        df = df[df.index >= start]
    if end:
        df = df[df.index <= end]
    return df


def create_treemap_data(start, end, item):
    close = data.get('price:收盤價')
    basic_info = data.get('company_basic_info')
    turnover = data.get('price:成交金額')
    close_data = df_date_filter(close, start, end)
    turnover_data = df_date_filter(turnover, start, end).iloc[1:].sum() / 100000000
    return_ratio = (close_data.iloc[-1] / close_data.iloc[0]).dropna().replace(np.inf, 0)
    return_ratio = round((return_ratio - 1) * 100, 2)

    concat_list = [close_data.iloc[-1], turnover_data, return_ratio]
    col_names = ['stock_id', 'close', 'turnover', 'return_ratio']
    if item not in ["return_ratio", "turnover_ratio"]:
        custom_item = df_date_filter(data.get(item), start, end).iloc[-1]
        concat_list.append(custom_item)
        col_names.append(item)

    df = pd.concat(concat_list, axis=1).dropna()
    df = df.reset_index()
    df.columns = col_names

    basic_info_df = basic_info.copy()
    basic_info_df['stock_id_name'] = basic_info_df['stock_id']
    basic_info_df['stock_id'] = basic_info_df['stock_id'].apply(lambda s: s[:s.index(' ')])

    df = df.merge(basic_info_df[['stock_id', 'stock_id_name', '產業類別', '市場別', '實收資本額(元)']], how='left',
                  on='stock_id')
    df = df.rename(columns={'產業類別': 'category', '市場別': 'market', '實收資本額(元)': 'base'})
    df = df.dropna(thresh=5)
    df['market_value'] = round(df['base'] / 10 * df['close'] / 100000000, 2)
    df['turnover_ratio'] = df['turnover'] / (df['turnover'].sum()) * 100
    df['country'] = 'TW-Stock'
    return df


def plot_tw_stock_treemap(start=None, end=None, area_ind='market_value', item='return_ratio', color_scales='Temps'):
    """Plot treemap chart for tw_stock

    Treemap charts visualize hierarchical data using nested rectangles,
    it is good for judging the overall market dynamics.

    Args:
      start(str): The date of data start point.ex:2021-01-02
      end(str):The date of data end point.ex:2021-01-05
      area_ind(str):The indicator to control treemap area size .
                    Select range is in ["market_value","turnover","turnover_ratio"]
      item(str): The indicator to control treemap area color .
                 Select range is in ["return_ratio", "turnover_ratio"]
                 or use the other customized data which you could find from finlab database page,
                 ex:'price_earning_ratio:本益比'
      color_scales(str):Used for the built-in named continuous
                        (sequential, diverging and cyclical) color scales in Plotly
                        Ref:https://plotly.com/python/builtin-colorscales/
    Returns:
        Treemap figure
    """
    df = create_treemap_data(start, end, item)

    if area_ind not in ["market_value", "turnover", "turnover_ratio"]:
        return None

    if item in ['return_ratio']:
        color_continuous_midpoint = 0
    else:
        color_continuous_midpoint = np.average(df[item], weights=df[area_ind])

    fig = px.treemap(df,
                     path=['country', 'market', 'category', 'stock_id_name'],
                     values=area_ind,
                     color=item,
                     color_continuous_scale=color_scales,
                     color_continuous_midpoint=color_continuous_midpoint,
                     custom_data=[item, 'close', 'turnover'],
                     title=f'TW-Stock Market TreeMap({start}~{end})'
                           f'---area_ind:{area_ind}---item:{item}',
                     width=1600,
                     height=800)

    fig.update_traces(textposition='middle center',
                      textfont_size=24,
                      texttemplate="%{label}(%{customdata[1]})<br>%{customdata[0]}",
                      )
    return fig.show()


"""
Radar
"""


def plot_radar(df, mode='line_polar', line_polar_fill=None, title=None):
    args = dict(data_frame=df, r="value", theta="variable", color="stock_id", line_close=True,
                color_discrete_sequence=px.colors.sequential.Plasma_r,
                template="plotly_dark")
    if mode is not 'line_polar':
        args.pop('line_close')

    fig = getattr(px, mode)(**args)
    if title is None:
        title = 'Features Radar'
    fig.update_layout(
        title={
            'text': title,
            'x': 0.49,
            'y': 0.99,
            'xanchor': 'center',
            'yanchor': 'top'},
        paper_bgcolor='rgb(41, 30, 109)',
        width=1200,
        height=600)
    if mode is 'line_polar':
        # None,toself,tonext
        fig.update_traces(fill=line_polar_fill)
    return fig.show()


def get_rank(item: str, iloc_num=-1, cut_bins=10):
    df = data.get(item)
    df_rank = df.iloc[iloc_num].dropna().rank(pct=True)
    df_rank = pd.cut(x=df_rank, bins=cut_bins, labels=[i for i in range(1, cut_bins + 1)])
    return df_rank


def get_rank_df(feats: list, iloc_num=-1, cut_bins=10):
    df = pd.concat([get_rank(f, iloc_num, cut_bins) for f in feats], axis=1)
    columns_name = [f[f.index(':') + 1:] for f in feats]
    df = df.fillna(1)
    df.columns = columns_name
    df.index.name = 'stock_id'
    return df


def plot_tw_stock_radar(df=None, feats=None, select_targets=None, mode='line_polar', line_polar_fill=None,
                        cut_bins=10, title=None):
    """Plot radar chart for tw_stock

    A polar chart represents data along radial and angular axes.
    It is good for comparing features values.

    Args:
      df(dataframe):Customized indicator dataframe,the values are rank int values,
                    recommend to operate data by pandas rank and cut functions
                    in order to display on polar charts axes ,
                    format like:
                                營業毛利率	營業利益率	稅後淨利率
                    stock_id
                    1101	          6	        9	      9
                    1102	          6	        9	      9
                    1103	          1	        1	      1
                    1104	          4	        7	      8
                    1108	          3	        6	      5
                    If it is None, used finlab database feats to generate dataframe.
      feats(list):The list of database method name on finlab database web.
                      Default list is 20 fundamental_features from last data.
                  ex:['fundamental_features:營業毛利率','fundamental_features:營業利益率'].
      select_targets(list):The targets in order to display data .
                           ex:['1101','1102'].
      mode(str): Could use 3 modes ,ex:'line_polar','bar_polar','scatter_polar'.
                 Ref:https://plotly.com/python-api-reference/generated/plotly.express.html
      line_polar_fill(str): Could use 3 modes ,ex:None,'toself','tonext'.
                            Ref:see fill arg description from
                                https://plotly.github.io/plotly.py-docs/generated/plotly.graph_objects.Scatterpolar.html
      cut_bins(int):Control rank group.
      title(str):Set figure title.
    Returns:
        Polar figure
    """
    if df is None:
        if feats is None:
            feats = ['fundamental_features:營業毛利率', 'fundamental_features:營業利益率', 'fundamental_features:稅後淨利率',
                     'fundamental_features:ROA綜合損益', 'fundamental_features:ROE綜合損益',
                     'fundamental_features:業外收支營收率', 'fundamental_features:貝里比率', 'fundamental_features:研究發展費用率',
                     'fundamental_features:現金流量比率', 'fundamental_features:負債比率',
                     'fundamental_features:流動比率', 'fundamental_features:速動比率', 'fundamental_features:存貨週轉率',
                     'fundamental_features:營收成長率', 'fundamental_features:營業毛利成長率',
                     'fundamental_features:營業利益成長率', 'fundamental_features:稅前淨利成長率', 'fundamental_features:稅後淨利成長率',
                     'fundamental_features:資產總額成長率', 'fundamental_features:淨值成長率'
                     ]
        df = get_rank_df(feats, cut_bins=cut_bins)

    col_name = df.columns
    if select_targets is None:
        select_targets = df.index[:2]
    df = df.loc[select_targets]
    df = df.reset_index()
    df = pd.melt(df, id_vars=['stock_id'], value_vars=col_name)
    fig = plot_radar(df=df, mode=mode, line_polar_fill=line_polar_fill, title=title)
    return fig
