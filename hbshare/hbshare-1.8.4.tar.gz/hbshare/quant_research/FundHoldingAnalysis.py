"""
基于估值表的持仓分析
"""
import pandas as pd
import os
import hbshare as hbs
from hbshare.rm_associated.util.config import style_name, industry_name
import matplotlib.pyplot as plt

plt.style.use('seaborn')
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


class HoldingAnalysor:
    def __init__(self, path, benchmark_id):
        self.path = path
        self.benchmark_id = benchmark_id
        self._load_data()

    def _load_portfolio_weight(self):
        filenames = os.listdir(self.path)
        filenames = [x for x in filenames if x.split('.')[-1] == 'xls']

        portfolio_weight_series_dict = dict()
        for name in filenames:
            date = name.split('_')[-2]
            data = pd.read_excel(os.path.join(self.path, name), sheet_name=0, header=3)
            sh = data[data['科目代码'].str.startswith('11020101')]
            sz = data[data['科目代码'].str.startswith('11023101')]
            cyb = data[data['科目代码'].str.startswith('11024101')]
            kcb = data[data['科目代码'].str.startswith('1102C101')]
            df = pd.concat([sh, sz, cyb, kcb], axis=0).dropna()
            df['ticker'] = df['科目代码'].apply(lambda x: x[-6:])
            weight = df.rename(columns={"市值占净值%": "weight"}).set_index('ticker')['weight'] / 100.
            portfolio_weight_series_dict[date] = weight
            print(len(weight))

        return portfolio_weight_series_dict

    def _load_benchmark_weight(self, portfolio_weight_series_dict):
        date_list = sorted(portfolio_weight_series_dict.keys())

        sql_script = "SELECT * FROM hsjy_gg.SecuMain where SecuCategory = 4 and SecuCode = '{}'".format(
            self.benchmark_id)
        res = hbs.db_data_query('readonly', sql_script)
        index_info = pd.DataFrame(res['data'])
        inner_code = index_info.set_index('SECUCODE').loc[self.benchmark_id, 'INNERCODE']
        benchmark_weight_series_dict = dict()
        for date in date_list:
            sql_script = "SELECT (select a.SecuCode from hsjy_gp.SecuMain a where a.InnerCode = b.InnerCode and " \
                         "rownum = 1) SecuCode, b.EndDate, b.Weight FROM hsjy_gg.LC_IndexComponentsWeight b WHERE " \
                         "b.IndexCode = '{}' and b.EndDate = to_date('{}', 'yyyymmdd')".format(inner_code, date)
            data = pd.DataFrame(hbs.db_data_query('readonly', sql_script)['data'])
            weight_df = data.rename(
                columns={"SECUCODE": "consTickerSymbol", "ENDDATE": "effDate", "WEIGHT": "weight"})
            benchmark_weight_series_dict[date] = weight_df.set_index(
                'consTickerSymbol')['weight'] / 100.

        return benchmark_weight_series_dict

    @staticmethod
    def _load_style_exposure(portfolio_weight_series_dict):
        date_list = sorted(portfolio_weight_series_dict.keys())

        style_factor_exposure_series_dict = dict()
        for date in date_list:
            # data_path = os.path.join(path, r'zzqz_sw\style_factor')
            # exposure_df = pd.read_csv(
            #     os.path.join(data_path, '{0}.csv'.format(date)), dtype={"ticker": str}).set_index(
            #     'ticker')[style_name_list]
            sql_script = "SELECT * FROM st_ashare.r_st_barra_style_factor where TRADE_DATE = '{}'".format(date)
            res = hbs.db_data_query('alluser', sql_script, page_size=5000)
            exposure_df = pd.DataFrame(res['data']).set_index('ticker')
            ind_names = [x.lower() for x in industry_name['sw'].values()]
            style_factor_exposure_series_dict[date] = exposure_df[style_name + ind_names]

        return style_factor_exposure_series_dict

    def _load_data(self):
        portfolio_weight_series_dict = self._load_portfolio_weight()
        benchmark_weight_series_dict = self._load_benchmark_weight(portfolio_weight_series_dict)
        style_factor_exposure_series_dict = self._load_style_exposure(portfolio_weight_series_dict)

        data_param = {
            "portfolio_weight_series_dict": portfolio_weight_series_dict,
            "benchmark_weight_series_dict": benchmark_weight_series_dict,
            "style_factor_exposure_series_dict": style_factor_exposure_series_dict
        }

        self.data_param = data_param

    def get_construct_result(self):
        portfolio_weight_series_dict = self.data_param.get('portfolio_weight_series_dict')
        benchmark_weight_series_dict = self.data_param.get('benchmark_weight_series_dict')
        style_factor_exposure_series_dict = self.data_param.get('style_factor_exposure_series_dict')

        for date in portfolio_weight_series_dict.keys():
            portfolio_weight_series = portfolio_weight_series_dict[date]
            benchmark_weight_series = benchmark_weight_series_dict[date]
            style_factor_exposure_series = style_factor_exposure_series_dict[date]

            idx = portfolio_weight_series.index.union(benchmark_weight_series.index).intersection(
                style_factor_exposure_series.index)

            portfolio_weight_series = portfolio_weight_series.reindex(idx).fillna(0.)
            benchmark_weight_series = benchmark_weight_series.reindex(idx).fillna(0.)
            style_factor_exposure_series = style_factor_exposure_series.reindex(idx).astype(float)

            portfolio_expo = style_factor_exposure_series.T.dot(portfolio_weight_series)
            benchmark_expo = style_factor_exposure_series.T.dot(benchmark_weight_series)
            style_expo = pd.concat([portfolio_expo.to_frame('port'), benchmark_expo.to_frame('bm')], axis=1)
            style_expo['active'] = style_expo['port'] - style_expo['bm']

            reverse_ind = dict([(value.lower(), key) for (key, value) in industry_name['sw'].items()])

            ax1 = style_expo[['port', 'bm']].rename(
                columns={"port": "因诺聚配中证500指增", "bm": "中证500"}).loc[style_name].plot.bar(
                rot=0, fontsize=12, title="{}期风格暴露比较".format(date), figsize=(18, 12))

            tmp = style_expo[['port', 'bm']].rename(
                columns={"port": "因诺聚配中证500指增", "bm": "中证500"}).iloc[10:]
            tmp.index = [reverse_ind[x] for x in tmp.index]
            ax2 = tmp.plot.bar(fontsize=12, title="{}期行业暴露比较".format(date), figsize=(18, 8))
            fig = ax1.get_figure()
            fig.savefig(os.path.join(self.path, '{}_风格.png'.format(date)))
            fig = ax2.get_figure()
            fig.savefig(os.path.join(self.path, '{}_行业.png'.format(date)))


if __name__ == '__main__':
    HoldingAnalysor(path='D:\\研究基地\\机器学习类\\因诺\\聚配500估值表及绩效报告', benchmark_id='000905').get_construct_result()