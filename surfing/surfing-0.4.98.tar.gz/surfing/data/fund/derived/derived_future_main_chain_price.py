
from string import digits
from ...api.research_api import *
from ...api.raw import *
from .derived_data_helper import DerivedDataHelper

class FutureTypeProcessor:

    future_type_dic = {
        '股指期货':['中证500股指期货','沪深300股指期货','上证50股指期货'],
        '国债期货':['5年期国债期货','10年期国债期货','2年期国债期货',],
        '贵金属':['沪银','沪金'],
        '有色金属':['沪铜','沪铝','沪锌','沪铅','镍','锡'],
        '黑色金属':['螺纹钢','铁矿石','热卷','不锈钢','线材','硅铁','锰硅'],
        '能源化工':['橡胶','20号胶','塑料','PTA','短纤','PVC','乙二醇','苯乙烯','尿素','纯碱','胶合板','沥青','纤维板','玻璃','燃油','甲醇','液化石油气','聚丙烯','中质含硫原油','纸浆','焦炭','焦煤','线材','低硫燃料油','郑煤'],
        '农产品':['豆粕','玉米','豆一','玉米淀粉','强麦','普麦','粳米','早籼','晚籼','苹果','豆二','郑棉','红枣','棉纱','生猪','菜油','棕榈','花生','菜粕','菜籽','白糖','鸡蛋','粳稻','豆油',],        
    }

    def __init__(self, data_helper = DerivedDataHelper()):
        self._data_helper = data_helper
        self.raw_api =  RawDataApi()
        self.derived_api = DerivedDataApi()
        self.research_api = ResearchApi()

    def init(self):
        self.future_info = self.raw_api.get_em_future_info()
        self.future_type = {vi : k  for k, v in self.future_type_dic.items() for vi in v}

    def remove_digit(self, s):
        remove_digits = str.maketrans('', '', digits)
        return s.translate(remove_digits)

    def process(self):
        result = []
        for product_i, type_i in self.future_type.items():
            trading_code = self.future_info[self.future_info.trans_type == product_i].trading_code.values[-5]
            trading_code = self.remove_digit(trading_code)
            dic = {
                'future_type_id': trading_code,
                'desc_name': product_i,
                'product_type':type_i,
            }
            result.append(dic)
        df = pd.DataFrame(result)   
        df.to_sql('future_type_classification', DerivedDatabaseConnector().get_engine(), index=False, if_exists='append')
    
class FutureMainForcePrice:

    def __init__(self, data_helper = DerivedDataHelper()):
        self._data_helper = data_helper
        self.raw_api = RawDataApi()
        self.derived_api =  DerivedDataApi()
        self.research_api = ResearchApi()   

    def init(self):
        self.future_info = self.raw_api.get_em_future_info()
        self.future_type = self.derived_api.get_future_type_classification()
        self.future_price = self.research_api.get_future_quote()
        self.trade_dates = np.array(self.research_api.get_tdates())
        self.trade_dates_wti = np.array(self.research_api.get_tdates(exch='nyse'))

    def get_main_ticker(self, x):
        # 获取东财主力连续代码
        return x + '0'
        
    def fill_main_future(self, col_name, df):
        l = df[df[col_name] < df[col_name].shift(1)].index.tolist()
        df.loc[l] = None
        df = df.ffill()   
        return df

    def get_main_force(self, future_name, future_type_id, amount_over_days, switch_days):
        # 用收益率做主力连续合约
        ## 去掉东财主连代码
        future_info_i = self.future_info[self.future_info.trans_type == future_name]
        s = future_info_i.trading_code.values[0]
        main_type_name = self.get_main_ticker(future_name)
        future_info_i = future_info_i[future_info_i.trading_code != main_type_name]

        ## 去掉东财股指期货主连
        future_info_i = future_info_i[~future_info_i.trading_code.isin(['ICM','IC00C1','IC00C2','IC00C3','IC00C4','IFM','IF00C1','IF00C2','IF00C3','IF00C4','IHM','IH00C1','IH00C2','IH00C3','IH00C4','CL00Y'])]
        em_id_list = future_info_i.em_id.tolist()
        size = future_info_i[future_info_i.trans_type == future_name].contract_mul.values[0]

        ## 主连合约不允许更改远期合约到近期合约
        future_price_i = self.future_price[self.future_price.em_id.isin(em_id_list)].copy()
        future_price_i['vwap'] = future_price_i['uni_amount'] / future_price_i['uni_volume'] / size
        future_volume = future_price_i.pivot_table(index='datetime', columns='em_id', values='uni_volume')
        main_ticker_df = future_volume.idxmax(axis=1).to_frame()
        col_name = 'main_ticker'
        main_ticker_df.columns = [col_name]
        main_ticker_df = self.fill_main_future(col_name, main_ticker_df)
        main_ticker_df = self.fill_main_future(col_name, main_ticker_df)

        ## 设置交易量连续超过几天后更换合约
        main_ticker_df.loc[:,'last_days_main_ticker'] = main_ticker_df.main_ticker.shift(amount_over_days-1)
        res = []
        for r in main_ticker_df.itertuples():
            dic = {'datetime':r.Index}
            if r.last_days_main_ticker is np.nan or r.last_days_main_ticker == r.main_ticker:
                dic['ticker'] = r.main_ticker
            elif r.last_days_main_ticker != r.main_ticker:
                dic['ticker'] = r.last_days_main_ticker
            res.append(dic)
        ticker_info = pd.DataFrame(res)

        ## 次主力合约不允许更改远期合约到近期合约
        _future_volume = future_volume.copy()
        for r in ticker_info.itertuples():
            _future_volume.loc[r.datetime,r.ticker] = 0
        sub_main_ticker_df = _future_volume.idxmax(axis=1).to_frame()
        col_name = 'sub_ticker'
        sub_main_ticker_df.columns = [col_name]
        sub_main_ticker_df = self.fill_main_future(col_name, sub_main_ticker_df)
        sub_main_ticker_df = self.fill_main_future(col_name, sub_main_ticker_df)
        sub_main_ticker_df = self.fill_main_future(col_name, sub_main_ticker_df)

        ## 设置更换主连后多少天之后更换新收益率 含下一日主力合约
        future_close = future_price_i.pivot_table(index='datetime', columns='em_id', values='close')
        ticker_info = ticker_info.set_index('datetime').join(sub_main_ticker_df).reset_index()
        if future_type_id != 'CL':
            next_dt = self.trade_dates[self.trade_dates>ticker_info.datetime.values[-1]][0]
            _trade_dates = self.trade_dates[(self.trade_dates >= ticker_info.datetime.values[0]) & (self.trade_dates <= ticker_info.datetime.values[-1])]
        
        else:
            next_dt = self.trade_dates_wti[self.trade_dates_wti>ticker_info.datetime.values[-1]][0]
            _trade_dates = self.trade_dates_wti[(self.trade_dates_wti >= ticker_info.datetime.values[0]) & (self.trade_dates_wti <= ticker_info.datetime.values[-1])]
        ticker_info = ticker_info.append(pd.DataFrame([{'datetime':next_dt}])).reset_index(drop=True)
        ticker_info.ticker = ticker_info.ticker.shift(switch_days)
        ticker_info = ticker_info.set_index('datetime').reindex(_trade_dates).ffill().reset_index()
        ticker_info = ticker_info.dropna()
        ## 填充收益率
        future_ret = future_close.pct_change(periods=1,fill_method=None)
        for r in ticker_info.itertuples():
            if r.datetime in future_ret.index:
                ticker_info.loc[r.Index,'ret'] = future_ret.loc[r.datetime,r.ticker]
                ticker_info.loc[r.Index,'sub_ret'] = future_ret.loc[r.datetime,r.sub_ticker]
        ticker_info['future_type_id'] = future_type_id
        return ticker_info

    def process(self):
        try:
            self.init()
            result = []
            amount_over_days = 1
            switch_days = 1
            for r in self.future_type.itertuples():
                try:
                    future_name = r.desc_name
                    future_type_id = r.future_type_id
                    result_i = self.get_main_force(future_name, future_type_id, amount_over_days, switch_days)
                    result.append(result_i)
                except:
                    print(future_name, future_type_id, 'boom')
            result_df = pd.concat(result)
           
            # 删除库主力收益和次主力收益为空的
            self.derived_api.delete_null_future_ret()
            # 增量更新
            exsited_df = self.derived_api.get_future_main_chain_ret()
            result_df_doubleidx = result_df.set_index(['datetime','future_type_id'])
            exsited_df_doubleidx = exsited_df.set_index(['datetime','future_type_id'])
            diff = result_df_doubleidx.index.difference(exsited_df_doubleidx.index)
            df_result = result_df_doubleidx.loc[diff].reset_index()
            tds = pd.to_datetime(df_result.datetime)
            tds = [i.date() for i in tds]
            df_result.datetime = tds
            if not df_result.empty:
                df_result.to_sql('future_main_chain_ret', DerivedDatabaseConnector().get_engine(), index=False, if_exists='append')
            return True
        except:
            return False
