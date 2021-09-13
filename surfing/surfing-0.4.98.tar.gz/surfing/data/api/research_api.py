import time
import json

from ...constant import FOFTradeStatus, HoldingAssetType
from .raw import *
from .basic import *
from .derived import *
from ..view.TL_models import *
from ..wrapper.mysql import TLDatabaseConnector, TestDatabaseConnector
from ..view.test_models import *
class ResearchApi(metaclass=Singleton):
    
    def get_index_quote(self,start_date,end_date, index_ids):
        """指数行情查询接口"""
        try:
            with BasicDatabaseConnector().managed_session() as db_session:
                rename_dic = {
                    'total_turnover': 'amount',
                }
                query = db_session.query(
                        IndexPrice.index_id,
                        IndexPrice.datetime,
                        IndexPrice.open,
                        IndexPrice.high,
                        IndexPrice.low,
                        IndexPrice.close,
                        IndexPrice.volume,
                        IndexPrice.total_turnover
                        
                    ).filter(
                        IndexPrice.index_id.in_(index_ids),
                        IndexPrice.datetime >= start_date, #根据日期筛选数据
                        IndexPrice.datetime <= end_date
                    )           
                df1 = pd.read_sql(query.statement, query.session.bind).rename(columns=rename_dic)
                
            with RawDatabaseConnector().managed_session() as db_session:
                rename_dic = {
                    'index_date':'datetime',
                }
                query = db_session.query(
                        HFIndexPrice.index_id,
                        HFIndexPrice.index_date,
                        HFIndexPrice.close
                    ).filter(
                        HFIndexPrice.index_id.in_(index_ids),
                        HFIndexPrice.index_date >= start_date, #根据日期筛选数据
                        HFIndexPrice.index_date <= end_date
                    )
                df2 = pd.read_sql(query.statement, query.session.bind).rename(columns=rename_dic) 
                
            with TestDatabaseConnector().managed_session() as db_session:
                query = db_session.query(
                        PfIndexPrice.index_id,
                        PfIndexPrice.datetime,
                        PfIndexPrice.close
                    ).filter(
                        PfIndexPrice.index_id.in_(index_ids),
                        PfIndexPrice.datetime >= start_date, #根据日期筛选数据
                        PfIndexPrice.datetime <= end_date
                    )
                df3 = pd.read_sql(query.statement, query.session.bind).rename(columns=rename_dic) 
            df = pd.concat([df1, df2, df3])
            return df
        except Exception as e:
            print('Failed to get data <err_msg> {}'.format(e) + ' from BasicDataApi.get_index_price')
            return None
            
    def get_index_info(self, desc_name:list=[]):
        '''指数基本信息模糊查询接口'''
        try:
            with BasicDatabaseConnector().managed_session() as db_session:
                query = db_session.query(
                            IndexInfo.index_id,
                            IndexInfo.desc_name,
                            IndexInfo.em_id,
                        )
                for name_i in desc_name:
                    query = query.filter(
                            IndexInfo.desc_name.like(f'%{name_i}%')
                        )
                df1 = pd.read_sql(query.statement, query.session.bind)
                dic = {
                    'real_id':'index_id',
                    'real_name':'desc_name',
                    'asset_id':'em_id',
                }
                query = db_session.query(
                            AssetInfo.asset_id,
                            AssetInfo.real_name,
                            AssetInfo.real_id,
                )
                for name_i in desc_name:
                    query = query.filter(
                            AssetInfo.real_name.like(f'%{name_i}%')
                        )
                df2 = pd.read_sql(query.statement, query.session.bind)
                df2 = df2.rename(columns=dic)[dic.values()]
                
            with TestDatabaseConnector().managed_session() as db_session:
                query = db_session.query(
                            PfIndexInfo.index_id,
                            PfIndexInfo.desc_name,       
                )
                for name_i in desc_name:
                    query = query.filter(
                            PfIndexInfo.desc_name.like(f'%{name_i}%')
                        )
                df3 = pd.read_sql(query.statement, query.session.bind)
                df = pd.concat([df1,df2,df3])
                return df
                
        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from {ResearchApi.get_index_info}')

    def get_index_info_by_id(self, index_list:list=[]):
        '''指数基本信息查询接口'''
        try:
            with BasicDatabaseConnector().managed_session() as db_session:
                query = db_session.query(
                            IndexInfo.index_id,
                            IndexInfo.desc_name,
                            IndexInfo.em_id,
                        ).filter(
                            IndexInfo.index_id.in_(index_list)
                        )
                df1 = pd.read_sql(query.statement, query.session.bind)
                dic = {
                    'real_id':'index_id',
                    'real_name':'desc_name',
                    'asset_id':'em_id',
                }
                query = db_session.query(
                            AssetInfo.asset_id,
                            AssetInfo.real_name,
                            AssetInfo.real_id,
                        ).filter(
                            AssetInfo.real_id.in_(index_list)
                        )
                df2 = pd.read_sql(query.statement, query.session.bind)
                df2 = df2.rename(columns=dic)[dic.values()]
                
            with TestDatabaseConnector().managed_session() as db_session:
                query = db_session.query(
                            PfIndexInfo.index_id,
                            PfIndexInfo.desc_name,       
                        ).filter(
                            PfIndexInfo.index_id.in_(index_list)
                        )
                df3 = pd.read_sql(query.statement, query.session.bind)
            df = pd.concat([df1,df2,df3])
            return df
                
        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from {ResearchApi.get_index_info}')


    def get_index_component(self,index_id,start_date,end_date):
        '''指数成分股查询'''
        with RawDatabaseConnector().managed_session() as db_session:
            try: 
                    query = db_session.query(
                        EmIndexComponent
                    ).filter(
                        EmIndexComponent.index_id.in_([index_id]),
                        EmIndexComponent.datetime <= end_date, 
                        EmIndexComponent.datetime >= start_date
                        )
                    index_stocks = pd.read_sql(query.statement, query.session.bind)
                    return index_stocks                  
            except Exception as e:
                    print(f'Failed to get data <err_msg> {e} from {ResearchApi.get_index_component}')

    def get_index_fac(self, start_date, end_date, index_ids:list=[]):
        '''指数衍生数据查询接口'''
        with DerivedDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                            IndexValuationLongTerm.index_id,
                            IndexValuationLongTerm.datetime,
                            IndexValuationLongTerm.pb_mrq,
                            IndexValuationLongTerm.pe_ttm,
                            IndexValuationLongTerm.roe,
                            IndexValuationLongTerm.ps_ttm,
                            IndexValuationLongTerm.dy,
                            IndexValuationLongTerm.pcf_ttm,
                            IndexValuationLongTerm.est_peg,
                            IndexValuationLongTerm.eps_ttm,
                    )
 
                if index_ids:
                    query = query.filter(
                        IndexValuationLongTerm.index_id.in_(index_ids),
                    )
                if start_date:
                    query = query.filter(
                        IndexValuationLongTerm.datetime >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        IndexValuationLongTerm.datetime <= end_date,
                    )
                df = pd.read_sql(query.statement, query.session.bind)
                return df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {ResearchApi.get_index_valuation_long_term}')                    
                    
    def get_fund_nav(self , start_date , end_date , fund_id_list):
        '''公募净值查询接口'''
        try:
            with BasicDatabaseConnector().managed_session() as db_session:
                rename_dic = {
                    'adjusted_net_value': 'unitnav',
                    'acc_net_value':'cumnav',
                    'adjusted_net_value':'adjnav',
                    'daily_profit':'mmf_unityield',
                    'PURCHSTATUS':'purchase_status',
                    'REDEMSTATUS':'redeem_status',
                }
                query = db_session.query(
                    FundNav.fund_id,
                    FundNav.datetime,
                    FundNav.adjusted_net_value,
                    FundNav.unit_net_value,
                    FundNav.acc_net_value,
                    FundNav.daily_profit,
                ).filter(
                    FundNav.fund_id.in_(fund_id_list),
                    FundNav.datetime >= start_date,
                    FundNav.datetime <= end_date,
                )
                df = pd.read_sql(query.statement, query.session.bind)
                res = []
                for fund_id in fund_id_list:
                    df_i = df[df.fund_id == fund_id].copy()
                    df_i.loc[:,'ret'] = df_i.adjusted_net_value.pct_change(1)
                    res.append(df_i)
                df = pd.concat(res).rename(columns=rename_dic).reset_index(drop=True)
                fund_ids = df.fund_id.unique().tolist()
                fund_ids = [fund_id.split('!')[0] for fund_id in fund_ids]

            with RawDatabaseConnector().managed_session() as db_session:     

                query = db_session.query(
                        EmFundStatus.CODES,
                        EmFundStatus.DATES,
                        EmFundStatus.PURCHSTATUS,
                        EmFundStatus.REDEMSTATUS
                    )
                cons = (EmFundStatus.CODES.like(f'%{fund_id}%') for fund_id in fund_ids)
                query = query.filter(or_(cons))
                fund_status = pd.read_sql(query.statement, query.session.bind)
                df.loc[:,'_fund_id'] = df.fund_id.map(lambda x :x.split('!')[0]) 
                fund_status.loc[:,'_fund_id'] = fund_status.CODES.map(lambda x: x.split('.')[0])
                fund_ids = df._fund_id.unique().tolist()
                res = []
                for fund_id in fund_ids:
                    df_x = df[df._fund_id == fund_id].copy()
                    df_y = fund_status[fund_status._fund_id == fund_id].copy().rename(columns={'DATES':'datetime'})[['datetime','PURCHSTATUS','REDEMSTATUS']]
                    df_i = pd.merge(df_x, df_y, on='datetime',how='outer').set_index('datetime').sort_index()
                    df_i[['PURCHSTATUS','REDEMSTATUS']] = df_i[['PURCHSTATUS','REDEMSTATUS']].ffill()
                    df_i = df_i.dropna(subset=['fund_id']).drop(labels=['_fund_id'], axis=1)
                    res.append(df_i)
                df = pd.concat(res).rename(columns=rename_dic).reset_index()
                return df
        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from ResearchApi.get_fund_nav')
    
    def get_fund_asset_alloc(self , start_date , end_date , fund_id_list):
        '''公募基金持仓资产查询接口'''
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FundHoldAsset.fund_id,
                    FundHoldAsset.datetime,
                    FundHoldAsset.stock_nav_ratio,
                    FundHoldAsset.bond_nav_ratio,
                    FundHoldAsset.fund_nav_ratio,
                    FundHoldAsset.cash_nav_ratio,
                    FundHoldAsset.other_nav_ratio,
                    FundHoldAsset.first_repo_to_nav,
                    FundHoldAsset.avg_ptm,
                    FundHoldAsset._update_time,
                ).filter(
                    FundHoldAsset.fund_id.in_(fund_id_list),
                    FundHoldAsset.datetime >= start_date,
                    FundHoldAsset.datetime <= end_date,
                )
                df = pd.read_sql(query.statement, query.session.bind)
                dts = pd.to_datetime(df._update_time)
                dts = [i.date() for i in dts]
                df['publish_date'] = dts
                df = df.drop(labels=['_update_time'], axis=1)
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from ResearchApi.get_fund_hold_asset')
                
    def get_fund_hold_stock(self , start_date , end_date , fund_id_list):
        '''公募基金持仓股票查询接口'''
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FundHoldStock
                ).filter(
                    FundHoldStock.fund_id.in_(fund_id_list),
                    FundHoldStock.datetime >= start_date,
                    FundHoldStock.datetime <= end_date,
                )
                df = pd.read_sql(query.statement, query.session.bind).drop(columns = ["_update_time"])
                df = df.dropna(subset=['rank1_stock']).reset_index(drop=True)
                common_cols = ['fund_id','datetime']
                res = []
                for idx in df.index:
                    for i in range(1,11):
                        rank_cols = [f'rank{i}_stock',f'rank{i}_stock_code',f'rank{i}_stockval',f'rank{i}_stockweight']
                        rank_dic = {_i:_i.replace(str(i),'') for _i in rank_cols}
                        _df = df.loc[[idx]][common_cols+rank_cols].rename(columns=rank_dic).copy()
                        _df['rank'] = str(i)
                        res.append(_df)
                df = pd.concat(res)
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from ResearchApi.get_fund_hold_stock')

    def get_fund_info(self, fund_id = None ,desc_name = None ,wind_class_1 = None ,wind_class_2 = None ,
                  company_id = None, start_date = None ,size = None ,manager_id = None):
        """公募产品基本信息查询接口"""
        
        def obscure_return(Connector,list_,col_name,que):
            """
            支持模糊查询的方法
            Connector : databse managed session
            list_ : 一个含有模糊或者准确信息字符组成的list
            col_name: 筛选条件对应在databse的columns name
            return 一个含有准确信息字符串组成的list
            """
            with Connector as db_session:
                            query = db_session.query(
                                    que
                                )       
                            df = pd.read_sql(query.statement, query.session.bind)
            bool_df = pd.DataFrame()
            for str_ in list_:
                bool_df[str_] = (df[col_name].str.contains(str_))
            result = list(set(df[bool_df.any(axis = 1)][col_name].values.tolist()))
            return result
    
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query_size = db_session.query(
                                Fund_size_and_hold_rate.size,
                                Fund_size_and_hold_rate.fund_id                           
                            )
                df_size = pd.read_sql(query_size.statement, query_size.session.bind)
                query = db_session.query(
                            FundInfo.fund_id,
                            FundInfo.desc_name,
                            FundInfo.wind_class_1,
                            FundInfo.wind_class_2,
                            FundInfo.company_id,
                            FundInfo.start_date,
                            FundInfo.manager_id, 
                            FundInfo.end_date,
                        )
                if(fund_id != None):
                    query = query.filter(
                        FundInfo.fund_id.in_(fund_id),
                    )
                if(desc_name != None):
                    desc_name = obscure_return(BasicDatabaseConnector().managed_session(),desc_name,
                                                       "desc_name",FundInfo.desc_name)#模糊查询
                    query = query.filter(
                        FundInfo.desc_name.in_(desc_name),
                    )
                if(wind_class_1 != None):
                    wind_class_1 = obscure_return(BasicDatabaseConnector().managed_session(),wind_class_1,
                                                       "wind_class_1",FundInfo.wind_class_1)
                    query = query.filter(
                        FundInfo.wind_class_1.in_(wind_class_1),
                    )
                if(wind_class_2 != None):
                    wind_class_2 = obscure_return(BasicDatabaseConnector().managed_session(),wind_class_2,
                                                       "wind_class_2",FundInfo.wind_class_2)
                    query = query.filter(
                        FundInfo.wind_class_2.in_(wind_class_2),
                    )
                if(company_id != None):
                    company_id = obscure_return(BasicDatabaseConnector().managed_session(),company_id,
                                                      "company_id",FundInfo.company_id)#模糊查询
                    query = query.filter(
                        FundInfo.company_id.in_(company_id),
                    )
                if(start_date != None):
                    query = query.filter(
                        FundInfo.start_date >= start_date
                    )
                if(manager_id != None):
                    manager_id = obscure_return(BasicDatabaseConnector().managed_session(),manager_id,
                                                      "manager_id",FundInfo.manager_id)#模糊查询
                    query = query.filter(
                        FundInfo.manager_id.in_(manager_id),
                    )
                    
                df = pd.read_sql(query.statement, query.session.bind)
                df_size = df_size.dropna(subset=['size'],axis = 0)
                df_size = df_size.drop_duplicates(subset='fund_id', keep="last")#这里选取最新的基金规模             
                result_df = pd.merge(df,df_size,how = 'left',on = 'fund_id') 
                if (size != None):
                    result_df = result_df[(result_df['size'] > size[0]) & (result_df['size'] < size[1])]
                return result_df
            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e) + " get_fund_info()")
                return None

    def get_stock_quote(self , start_date , end_date , stock_id_list):
        '''股票行情查询接口'''
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                #EmStockPrice
                post = 'post_'
                rename_dic = {
                    'open':f'{post}open',
                    'close':f'{post}close',
                    'high':f'{post}high',
                    'low':f'{post}low',
                }
                query = db_session.query(
                    EmStockPostPrice.CODES,
                    EmStockPostPrice.DATES,
                    EmStockPostPrice.OPEN,
                    EmStockPostPrice.CLOSE,
                    EmStockPostPrice.HIGH,
                    EmStockPostPrice.LOW,
                    EmStockPostPrice.TRADESTATUS
                ).filter(
                    EmStockPostPrice.CODES.in_(stock_id_list),
                    EmStockPostPrice.DATES >= start_date-datetime.timedelta(days=30),
                    EmStockPostPrice.DATES <= end_date,
                )
                df = pd.read_sql(query.statement, query.session.bind).set_index('datetime')
                df = df.rename(columns=rename_dic)
                query = db_session.query(
                    EmStockPrice.CODES,
                    EmStockPrice.DATES,
                    EmStockPrice.OPEN,
                    EmStockPrice.CLOSE,
                    EmStockPrice.HIGH,
                    EmStockPrice.LOW,
                    EmStockPrice.VOLUME,
                    EmStockPrice.AMOUNT,
                ).filter(
                    EmStockPrice.CODES.in_(stock_id_list),
                    EmStockPrice.DATES >= start_date,
                    EmStockPrice.DATES <= end_date,
                )
                _df = pd.read_sql(query.statement, query.session.bind).set_index('datetime')

                res = []
                for code in df.stock_id.unique():
                    df_i = df[df.stock_id == code].copy()
                    df_i['ret'] = df_i.post_close.pct_change(1)
                    df_i = df_i.loc[start_date:]
                    _df_i = _df[_df.stock_id == code][['open','close','high','low','volume','amount']]
                    df_i = df_i.join(_df_i).reset_index()
                    res.append(df_i)
                df = pd.concat(res)
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from ResearchApi.get_stock_quote')
                
    def get_stock_post_price(self,start_date=None,end_date=None,stock_list=None):
         with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmStockPostPrice.CODES,
                    EmStockPostPrice.DATES,
                    EmStockPostPrice.OPEN,
                    EmStockPostPrice.CLOSE,
                    EmStockPostPrice.HIGH,
                    EmStockPostPrice.LOW,
                    EmStockPostPrice.TRADESTATUS
                )
                if start_date:
                    query = query.filter(EmStockPostPrice.DATES >= start_date)
                if end_date:
                    query = query.filter(EmStockPostPrice.DATES <= end_date)
                if stock_list:
                    query = query.filter(EmStockPostPrice.CODES.in_(stock_list))
                df = pd.read_sql(query.statement, query.session.bind).set_index('datetime')
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from ResearchApi.get_stock_post_price')

    def get_macro_value(self, code_list, start_date, end_date):
        '''宏观数据获取'''
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                        EmMacroEconomicMonthly.codes,
                        EmMacroEconomicMonthly.datetime,
                        EmMacroEconomicMonthly.value,
                    ).filter(
                        EmMacroEconomicMonthly.codes.in_(code_list),
                        EmMacroEconomicMonthly.datetime >= start_date,
                        EmMacroEconomicMonthly.datetime <= end_date,
                    )
                df1 = pd.read_sql(query.statement, query.session.bind).drop(columns = "_update_time", errors='ignore')
                query = db_session.query(
                        EmMacroEconomicDaily.codes,
                        EmMacroEconomicDaily.datetime,
                        EmMacroEconomicDaily.value,
                    ).filter(
                        EmMacroEconomicDaily.codes.in_(code_list),
                        EmMacroEconomicDaily.datetime >= start_date,
                        EmMacroEconomicDaily.datetime <= end_date,
                    )
                df2 = pd.read_sql(query.statement, query.session.bind).drop(columns = "_update_time", errors='ignore')
                df = pd.concat([df1, df2])
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from ResearchApi.get_macro_value')

    def get_macro_info(self, code_list=None, desc_list=None):
        '''宏观信息'''
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                        EmMacroEconomicInfo.codes,
                        EmMacroEconomicInfo.desc_name,
                    )
                if code_list:
                    query = query.filter(
                            EmMacroEconomicInfo.codes.in_(code_list),   
                        )
                if desc_list:    
                    for i in desc_list:
                        query = query.filter(
                            EmMacroEconomicInfo.desc_name.like(f'%{i}%')
                        )
                df = pd.read_sql(query.statement, query.session.bind)
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from ResearchApi.get_macro_info')

    def get_future_info(self, future_ids=None, trans_type_list=None):
        '''期货信息'''
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                        EmFutureInfoDetail.EMCODE,
                        EmFutureInfoDetail.TRADINGCODE,
                        EmFutureInfoDetail.FTTRANSTYPE,
                        EmFutureInfoDetail.CONTRACTMUL,
                        EmFutureInfoDetail.NAME,
                        )
                if future_ids:
                    query = query.filter(
                            EmFutureInfoDetail.EMCODE.in_(future_ids),   
                        )
                if trans_type_list:    
                    for i in trans_type_list:
                        query = query.filter(
                            EmFutureInfoDetail.FTTRANSTYPE.like(f'%{i}%')
                        )
                df = pd.read_sql(query.statement, query.session.bind)
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from ResearchApi.get_future_info')



    def get_future_quote(self, future_ids=None, start_date=None, end_date=None):
        '''期货行情'''
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                        EmFuturePriceDetail.CODES,
                        EmFuturePriceDetail.DATES,
                        EmFuturePriceDetail.OPEN,
                        EmFuturePriceDetail.HIGH,
                        EmFuturePriceDetail.LOW,
                        EmFuturePriceDetail.CLOSE,
                        EmFuturePriceDetail.PRECLOSE,
                        EmFuturePriceDetail.AVERAGE,
                        EmFuturePriceDetail.VOLUME,
                        EmFuturePriceDetail.AMOUNT,
                        EmFuturePriceDetail.HQOI,
                        EmFuturePriceDetail.CLEAR,
                        EmFuturePriceDetail.PRECLEAR,
                    )
                if future_ids:
                    query = query.filter(
                        EmFuturePriceDetail.CODES.in_(future_ids),
                    )
                if start_date:
                    query = query.filter(
                        EmFuturePriceDetail.DATES >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        EmFuturePriceDetail.DATES <= end_date,
                    )
                df = pd.read_sql(query.statement, query.session.bind).drop(columns = "_update_time", errors='ignore')
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from ResearchApi.get_macro_value')

    def get_industry_info(self, industry_class):
        '''行业分类详情查询接口'''
        try:
            if industry_class == "sw":
                with RawDatabaseConnector().managed_session() as db_session:
                    query = db_session.query(
                        EmIndustryInfo
                    ).filter(
                    )
                    df = pd.read_sql(query.statement, query.session.bind).drop(columns = "_update_time", errors='ignore')
                with BasicDatabaseConnector().managed_session() as db_session:
                    query = db_session.query(
                        IndexInfo.em_id,
                        IndexInfo.index_id
                    ).filter(
                        IndexInfo.em_id.in_(df.em_id)
                    )
                    df_1 = pd.read_sql(query.statement, query.session.bind).drop(columns = "_update_time", errors='ignore')
                    df = pd.merge(df, df_1, on='em_id')
                    return df
        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from ResearchApi.get_industry_info')
            
    def get_stock_info_concept(self, stock_id_list=None):
        '''股票申万\中信行业分类查询接口'''
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmStockConceptInfo
                )
                if stock_id_list:
                    query = query.filter(
                        EmStockConceptInfo.codes.in_(stock_id_list),
                    )
                df = pd.read_sql(query.statement, query.session.bind).drop(columns = "_update_time").set_index("codes")
                
                query = db_session.query(
                    EmStockInfo
                )
                if stock_id_list:
                    query = query.filter(
                        EmStockInfo.CODES.in_(stock_id_list),
                    )
                df = df.join(pd.read_sql(query.statement, query.session.bind).drop(columns = "_update_time").set_index("stock_id")[["bl_sws_ind_code"]])
                df['bl_sws_ind_code'] = df['bl_sws_ind_code'].map(lambda x: x.split('-') if isinstance(x, str) else None)
                df = df.explode('bl_sws_ind_code')
                query = db_session.query(
                    EmIndustryInfo.em_id,
                    EmIndustryInfo.ind_name,
                ).filter(
                    EmIndustryInfo.em_id.in_(df.bl_sws_ind_code.unique().tolist())
                )
                _df = pd.read_sql(query.statement, query.session.bind).rename(columns={'em_id':'bl_sws_ind_code'})
                df = pd.merge(df.reset_index(),_df,on='bl_sws_ind_code')
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from ResearchApi.get_stock_info_concept')
                
    def get_stock_fin(self , start_date , end_date , stock_id_list):
        '''股票财务数据查询接口'''
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmStockFinFac.CODES,
                    EmStockFinFac.DATES,
                    EmStockFinFac.ROEAVG,
                    EmStockFinFac.EPSDILUTED,
                    EmStockFinFac.BPS,
                    EmStockFinFac._update_time,
                ).filter(
                    EmStockFinFac.DATES >= start_date,
                    EmStockFinFac.DATES <= end_date,
                    EmStockFinFac.CODES.in_(stock_id_list),
                )
                df = pd.read_sql(query.statement, query.session.bind)
                dts = pd.to_datetime(df._update_time)
                dts = [i.date() for i in dts]
                df['publish_date'] = dts
                df = df.drop(labels=['_update_time'], axis=1)
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from ResearchApi.get_stock_price')
                
                
    def get_stock_fin_fac(self , start_date , end_date , stock_id_list):
        '''股票衍生数据查询接口'''
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmStockDailyInfo.CODES,
                    EmStockDailyInfo.DATES,
                    EmStockDailyInfo.PETTMDEDUCTED,
                    EmStockDailyInfo.PBLYRN,
                    EmStockDailyInfo.PSTTM,
                    EmStockDailyInfo.ESTPEG,
                    EmStockDailyInfo.EVWITHOUTCASH,
                ).filter(
                    EmStockDailyInfo.CODES.in_(stock_id_list),
                    EmStockDailyInfo.DATES >= start_date,
                    EmStockDailyInfo.DATES <= end_date,
                )
                df = pd.read_sql(query.statement, query.session.bind)#.drop(columns = "_update_time")
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from ResearchApi.get_stock_price')
                
                
    def get_capital_north_south(self , capital_class , start_date , end_date):
        '''北上\南下资金数据查询接口'''
        if capital_class == "south":
            with RawDatabaseConnector().managed_session() as db_session:
                try:
                    query = db_session.query(
                        EMSouthCapital
                    ).filter(
                        EMSouthCapital.datetime >= start_date,
                        EMSouthCapital.datetime <= end_date,
                    )
                    df = pd.read_sql(query.statement, query.session.bind).drop(columns = "_update_time")
                    return df
                except Exception as e:
                    print(f'Failed to get data <err_msg> {e} from ResearchApi.get_stock_price')
        else:
            with RawDatabaseConnector().managed_session() as db_session:
                try:
                    query = db_session.query(
                        EMNorthCapital
                    ).filter(
                        EMNorthCapital.datetime >= start_date,
                        EMNorthCapital.datetime <= end_date,
                    )
                    df = pd.read_sql(query.statement, query.session.bind).drop(columns = "_update_time")
                    return df
                except Exception as e:
                    print(f'Failed to get data <err_msg> {e} from ResearchApi.get_stock_price')
                
    
    def get_pf_info(self,
                    record_cd=None, 
                    name_list=None, 
                    stg_name=None, 
                    stg_child=None, 
                    company_name=None,
                    start_date=None,
                    mng_name=None):
        '''私募产品基本信息查询接口'''
        with TLDatabaseConnector().managed_session() as db_session:
            # 主策略对应
            main_type_name = '私募基金投资策略' 
            _query = db_session.query(
                SysCode.VALUE_NAME_CN,
                SysCode.VALUE_NUM_CD,
            ).filter(
                SysCode.CODE_TYPE_NAME == main_type_name
            )
            df = pd.read_sql(_query.statement, _query.session.bind)
            main_stg_dic = df.set_index('VALUE_NAME_CN')['VALUE_NUM_CD'].to_dict()
            main_stg_dic_re = df.set_index('VALUE_NUM_CD')['VALUE_NAME_CN'].to_dict()
            # 子策略对应
            child_type_name = '私募基金投资子策略'
            query = db_session.query(
                SysCode.VALUE_NAME_CN,
                SysCode.VALUE_NUM_CD,
            ).filter(
                SysCode.CODE_TYPE_NAME == child_type_name
            )
            df = pd.read_sql(query.statement, query.session.bind)
            child_stg_dic = df.set_index('VALUE_NAME_CN')['VALUE_NUM_CD'].to_dict()
            child_stg_dic_re = df.set_index('VALUE_NUM_CD')['VALUE_NAME_CN'].to_dict()

            # 返回字段
            query = db_session.query(
                Pfund.RECORD_CD,
                Pfund.INVEST_STRATEGY,
                Pfund.INVEST_STRATEGY_CHILD,
                Pfund.INVEST_CONSULTANT,
                Pfund.ESTABLISH_DATE,
                Pfund.END_DATE,
                Pfund.MANAGER,
                Pfund.STATUS,
                Pfund.SECURITY_ID,
            )
            # 按照备案号
            if record_cd:
                query = query.filter(
                    Pfund.RECORD_CD.in_(record_cd),
                )
            # 按照关键字搜索
            if name_list:
                _query = db_session.query(
                    MdSecurity.SECURITY_ID,
                    MdSecurity.SEC_SHORT_NAME,
                ).filter(MdSecurity.ASSET_CLASS=='FP')
                for i in name_list:
                    _query = _query.filter(
                        MdSecurity.SEC_SHORT_NAME.like(f'%{i}%')
                    )
                asset_info_df = pd.read_sql(_query.statement, _query.session.bind)
                query = query.filter(
                    Pfund.SECURITY_ID.in_(asset_info_df.SECURITY_ID),
                )
            # 按照主策略
            if stg_name:

                stg_list = [main_stg_dic.get(i) for i in stg_name]
                query = query.filter(
                    Pfund.INVEST_STRATEGY.in_(stg_list),
                )
            # 按照子策略
            if stg_child:

                stg_list = [child_stg_dic.get(i) for i in stg_child]
                query = query.filter(
                    Pfund.INVEST_STRATEGY_CHILD.in_(stg_list),
                )
            # 按照公司名搜索
            if company_name:
                _query = db_session.query(
                    MdInstitution.PARTY_ID,
                    MdInstitution.PARTY_SHORT_NAME,
                )
                for i in company_name:
                    _query = _query.filter(
                        MdInstitution.PARTY_SHORT_NAME.like(f'%{i}%')
                    )
                asset_info_df = pd.read_sql(_query.statement, _query.session.bind)
                query = query.filter(
                    Pfund.INVEST_CONSULTANT.in_(asset_info_df.PARTY_ID.dropna().unique()),
                )    
            # 按照成立日期
            if start_date:
                query = query.filter(
                    Pfund.ESTABLISH_DATE > start_date,
                ) 
            # 按照基金经理
            if mng_name:
                cons = (Pfund.MANAGER.like(f'%{i}%') for i in mng_name)
                query = query.filter(or_(cons))
            df = pd.read_sql(query.statement, query.session.bind).dropna(subset=['RECORD_CD'])
            df.loc[:,'INVEST_STRATEGY'] = df.INVEST_STRATEGY.map(main_stg_dic_re)
            df.loc[:,'INVEST_STRATEGY_CHILD'] = df.INVEST_STRATEGY_CHILD.map(child_stg_dic_re)
            # 替换机构名
            _query = db_session.query(
                MdInstitution.PARTY_ID,
                MdInstitution.PARTY_SHORT_NAME,
            ).filter(MdInstitution.PARTY_ID.in_(df.INVEST_CONSULTANT))
            _df = pd.read_sql(_query.statement, _query.session.bind).dropna(subset=['PARTY_ID'])
            _df['PARTY_ID'] = _df['PARTY_ID'].astype(str)
            company_dic = _df.set_index('PARTY_ID')['PARTY_SHORT_NAME'].to_dict()
            df.loc[:,'INVEST_CONSULTANT'] = df.INVEST_CONSULTANT.map(lambda x: company_dic.get(x))

            # 替换基金全名
            _query = db_session.query(
                MdSecurity.SECURITY_ID,
                MdSecurity.SEC_SHORT_NAME,
            ).filter(MdSecurity.SECURITY_ID.in_(df.SECURITY_ID))
            _df = pd.read_sql(_query.statement, _query.session.bind)
            name_dic = _df.set_index('SECURITY_ID')['SEC_SHORT_NAME'].to_dict()
            df.loc[:,'SEC_FULL_NAME'] = df.SECURITY_ID.map(name_dic)
            df = df.drop(columns=['SECURITY_ID'])

            # 替换运作状态
            _query = db_session.query(
                SysCode.VALUE_NUM_CD,
                SysCode.VALUE_NAME_CN,
            ).filter(SysCode.CODE_TYPE_ID == '40034' )
            _df = pd.read_sql(_query.statement, _query.session.bind)
            name_dic = _df.set_index('VALUE_NUM_CD')['VALUE_NAME_CN'].to_dict()
            df['STATUS'] = df.STATUS.map(name_dic)
            return df

    def get_pf_info2(self, record_cd):
        '''私募产品要素查询接口''' 
        with TLDatabaseConnector().managed_session() as db_session:    
            # 返回字段
            query = db_session.query(
                Pfund.RECORD_CD,
                Pfund.INVEST_CONSULTANT,
                Pfund.CUSTODIAN,
                Pfund.SUBSCRIPTION_START_POINT,
                Pfund.MIN_ADD,
                Pfund.STOP_LOSS_LINE,
                Pfund.WARN_LINE,
                Pfund.ISSUE_FEE,
                Pfund.REDEEM_FEE,
                Pfund.MANAGEMENT_FEE,
                Pfund.PERFORMANECE_RETURN,
                Pfund.APPLY_FEE,
                Pfund.CUSTODY_FEE,
                Pfund.SECURITY_ID,
            ).filter(
                Pfund.RECORD_CD.in_(record_cd),
            )
            df = pd.read_sql(query.statement, query.session.bind)
            _query = db_session.query(
                MdSecurity.SECURITY_ID,
                MdSecurity.SEC_SHORT_NAME,
            ).filter(MdSecurity.SECURITY_ID.in_(df.SECURITY_ID))
            _df = pd.read_sql(_query.statement, _query.session.bind)
            name_dic = _df.set_index('SECURITY_ID')['SEC_SHORT_NAME'].to_dict()
            df.loc[:,'SEC_FULL_NAME'] = df.SECURITY_ID.map(name_dic)
            df = df.drop(columns=['SECURITY_ID'])
            return df

    def search_pf_info(self, record_cd=None,start_date=None,info_items=None,with_detail=False):
        '''私募信息搜索 '''
        try:
            res = [self.get_pf_info(record_cd=record_cd,name_list=info_i,start_date=start_date) for info_i in info_items ]
            df_name = pd.concat(res).drop_duplicates()

            res = [self.get_pf_info(record_cd=record_cd,stg_name=info_i,start_date=start_date) for info_i in info_items ]
            df_stg = pd.concat(res).drop_duplicates()

            res = [self.get_pf_info(record_cd=record_cd,stg_child=info_i,start_date=start_date) for info_i in info_items ]
            df_stg_chd = pd.concat(res).drop_duplicates()

            time.sleep(1) # 搜索量大， 抱错
            res = [self.get_pf_info(record_cd=record_cd,company_name=info_i,start_date=start_date) for info_i in info_items ]
            df_stg_cpy = pd.concat(res).drop_duplicates()

            res = [self.get_pf_info(record_cd=record_cd,mng_name=info_i,start_date=start_date) for info_i in info_items ]
            df_stg_mng = pd.concat(res).drop_duplicates()

            df = pd.concat([df_name,df_stg,df_stg_chd,df_stg_cpy,df_stg_mng]).drop_duplicates().reset_index(drop=True)
            if with_detail:
                _df = self.get_pf_info2(df.RECORD_CD)
                df = pd.merge(df, _df, on='RECORD_CD', how='outer')
            return df
        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from ResearchApi.search_pf_info')

    def get_pf_inst_info(self, reg_cd=None,inst_name=None,key_person=None,scale_list=None):
        '''私募投顾基本信息查询接口'''
        inst_info_df = None
        inst_scale_df = None
        # 返回字段
        with TLDatabaseConnector().managed_session() as db_session:    
            # 返回字段
            query = db_session.query(
                PfundInstInfo.REG_CD,
                PfundInstInfo.PROFILE,
                PfundInstInfo.IDEA_STRATEGY,
                PfundInstInfo.KEY_PERSON,
                PfundInstInfo.PARTY_ID,
            )
        # 按照备案号
        if reg_cd:
            query = query.filter(
                PfundInstInfo.REG_CD.in_(reg_cd),
            )
        # 按照投顾名
        if inst_name:
            _query = db_session.query(
                PfundInstScaleAmac.PARTY_ID,
                PfundInstScaleAmac.PARTY_FULL_NAME,
            )
            for i in inst_name:
                _query = _query.filter(
                    PfundInstScaleAmac.PARTY_FULL_NAME.like(f'%{i}%')
                )
            inst_info_df = pd.read_sql(_query.statement, _query.session.bind)
            query = query.filter(
                PfundInstInfo.PARTY_ID.in_(inst_info_df.PARTY_ID.dropna().unique()),
            )    
        # 核心人物
        if key_person:
            for i in key_person:
                query = query.filter(
                    PfundInstInfo.KEY_PERSON.like(f'%{i}%'),
                )
        # 按照规模
        if scale_list:
            _query = db_session.query(
                PfundInstScaleAmac.PARTY_ID,
                PfundInstScaleAmac.SCALE,
            ).filter(
                PfundInstScaleAmac.SCALE.in_(scale_list)
            )
            inst_scale_df = pd.read_sql(_query.statement, _query.session.bind)
            query = query.filter(
                PfundInstInfo.PARTY_ID.in_(inst_scale_df.PARTY_ID.dropna().unique()),
            )    
        df = pd.read_sql(query.statement, query.session.bind)
        # 添加机构名
        if inst_info_df is None:
            _query = db_session.query(
                PfundInstScaleAmac.PARTY_ID,
                PfundInstScaleAmac.PARTY_FULL_NAME,
            ).filter(
                    PfundInstScaleAmac.PARTY_ID.in_(df.PARTY_ID.dropna().unique())
            )
            inst_info_df = pd.read_sql(_query.statement, _query.session.bind)
        full_name_dic = inst_info_df.dropna(subset=['PARTY_ID']).set_index('PARTY_ID')['PARTY_FULL_NAME'].to_dict()
        df.loc[:,'PARTY_FULL_NAME'] = df.PARTY_ID.map(full_name_dic)
        
        # 添加规模
        if inst_scale_df is None:
            _query = db_session.query(
                PfundInstScaleAmac.PARTY_ID,
                PfundInstScaleAmac.SCALE,
            ).filter(
                    PfundInstScaleAmac.PARTY_ID.in_(df.PARTY_ID.dropna().unique())
            )
            inst_scale_df = pd.read_sql(_query.statement, _query.session.bind)
        scale_dic = inst_scale_df.dropna(subset=['PARTY_ID']).set_index('PARTY_ID')['SCALE'].to_dict()
        df.loc[:,'SCALE'] = df.PARTY_ID.map(scale_dic)
        # 主策略统计
        main_type_name = '私募基金投资策略' 
        _query = db_session.query(
            SysCode.VALUE_NAME_CN,
            SysCode.VALUE_NUM_CD,
        ).filter(
            SysCode.CODE_TYPE_NAME == main_type_name
        )
        sys_df = pd.read_sql(_query.statement, _query.session.bind)
        #main_stg_dic = _df.set_index('VALUE_NAME_CN')['VALUE_NUM_CD'].to_dict()
        main_stg_dic_re = sys_df.set_index('VALUE_NUM_CD')['VALUE_NAME_CN'].to_dict()
        query = db_session.query(
                Pfund.RECORD_CD,
                Pfund.INVEST_STRATEGY,    
            ).filter(
            Pfund.INVEST_CONSULTANT.in_(df.PARTY_ID.unique()),
        )    
        _df = pd.read_sql(query.statement, query.session.bind)
        _df.loc[:,'VALUE_NAME_CN'] = _df.INVEST_STRATEGY.map(main_stg_dic_re)
        if not df.empty:
            main_stg = _df.groupby('VALUE_NAME_CN').count().sort_values('RECORD_CD').index[-1]
            df.loc[:,'MAIN_FUND_TYPE'] = main_stg
        else:
            df['MAIN_FUND_TYPE'] = ''
        return df

    def get_pf_nav(self, start_date=None, end_date=None, record_cds:list=[], source='tl'):
        '''私募净值查询接口'''
        try:
            # 通联
            if source == 'tl':
                with TLDatabaseConnector().managed_session() as db_session:                
                    query1 = db_session.query(
                        Pfund.SECURITY_ID,
                        Pfund.RECORD_CD,
                        ).filter(
                        Pfund.RECORD_CD.in_(record_cds)
                        )           
                    df1 = pd.read_sql(query1.statement, query1.session.bind)
                    security_ids = df1['SECURITY_ID'].values.tolist()
                    query = db_session.query(
                            PfundNav.END_DATE,
                            PfundNav.NAV,
                            PfundNav.ADJ_NAV,
                            PfundNav.ACCUM_NAV,
                            PfundNav.SECURITY_ID
                        )
                    if record_cds:
                        query = query.filter(
                            PfundNav.SECURITY_ID.in_(security_ids),
                        )
                    if start_date:
                        query = query.filter(
                            PfundNav.END_DATE >= start_date,
                        )
                    if end_date:
                        query = query.filter(
                            PfundNav.END_DATE <= end_date,
                        )
                    df = pd.read_sql(query.statement, query.session.bind)
                    df = pd.merge(df1, df, left_on='SECURITY_ID', right_on='SECURITY_ID')
            # 自己计算
            elif source == 'py_calc':
                with TLDatabaseConnector().managed_session() as db_session:                
                    query1 = db_session.query(
                        Pfund.SECURITY_ID,
                        Pfund.RECORD_CD,
                        ).filter(
                        Pfund.RECORD_CD.in_(record_cds)
                        )           
                    df1 = pd.read_sql(query1.statement, query1.session.bind)
                    security_id_dic = df1.set_index('RECORD_CD')['SECURITY_ID'].to_dict()
                with DerivedDatabaseConnector().managed_session() as db_session:
                    name_dic = {
                        's_id':'SECURITY_ID',
                        'fof_id':'RECORD_CD',
                        'datetime':'END_DATE',
                        'nav':'NAV',
                        'adjusted_nav':'ADJ_NAV',
                        'acc_net_value':'ACCUM_NAV',
                    }
                    query = db_session.query(
                            FOFNavCalc.fof_id,
                            FOFNavCalc.datetime,
                            FOFNavCalc.nav,
                            FOFNavCalc.acc_net_value,
                            FOFNavCalc.adjusted_nav,
                        ).filter(
                            FOFNavCalc.fof_id.in_(record_cds),
                            FOFNavCalc.manager_id == "py1",
                        )
                    if start_date:
                        query = query.filter(
                            FOFNavCalc.datetime >= start_date,
                        )
                    if end_date:
                        query = query.filter(
                            FOFNavCalc.datetime <= end_date,
                        )
                    df = pd.read_sql(query.statement, query.session.bind)
                    df.loc[:,'s_id'] = df.fof_id.map(security_id_dic)
                    df = df.rename(columns=name_dic)[name_dic.values()]
            # 客服发送
            elif source == 'py':
                with TLDatabaseConnector().managed_session() as db_session:                
                    query1 = db_session.query(
                        Pfund.SECURITY_ID,
                        Pfund.RECORD_CD,
                        ).filter(
                        Pfund.RECORD_CD.in_(record_cds)
                        )           
                    df1 = pd.read_sql(query1.statement, query1.session.bind)
                    security_id_dic = df1.set_index('RECORD_CD')['SECURITY_ID'].to_dict()
                with DerivedDatabaseConnector().managed_session() as db_session:
                    name_dic = {
                        's_id':'SECURITY_ID',
                        'fof_id':'RECORD_CD',
                        'datetime':'END_DATE',
                        'nav':'NAV',
                        'adjusted_nav':'ADJ_NAV',
                        'acc_net_value':'ACCUM_NAV',
                    }
                    query = db_session.query(
                            FOFNav.fof_id,
                            FOFNav.datetime,
                            FOFNav.nav,
                            FOFNav.acc_net_value,
                            FOFNav.adjusted_nav,
                        ).filter(
                            FOFNav.fof_id.in_(record_cds),
                            FOFNav.manager_id == "py1",
                        )
                    if start_date:
                        query = query.filter(
                            FOFNav.datetime >= start_date,
                        )
                    if end_date:
                        query = query.filter(
                            FOFNav.datetime <= end_date,
                        )
                    df = pd.read_sql(query.statement, query.session.bind)
                    df.loc[:,'s_id'] = df.fof_id.map(security_id_dic)
                    df = df.rename(columns=name_dic)[name_dic.values()]
            return df

        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from {ResearchApi.get_pfund_nav}')

    def get_pf_info_mixed(self, manager_id: str, fof_id: str) -> pd.DataFrame:
        '''汇总数据库中私募基金的信息表'''

        # self.get_pf_info(record_cd=fund_id_list)
        aa = self.get_pf_asset_allocation(manager_id, fof_id)
        fund_id_list = list(aa[aa.asset_type == HoldingAssetType.HEDGE].fund_id.unique()) + [fof_id]
        fof_info = BasicDataApi().get_fof_info(manager_id=manager_id, fof_id_list=fund_id_list)
        fof_info = fof_info[['fof_id', 'fof_name', 'admin', 'strategy_type']].rename(columns={'fof_id': 'fund_id'})
        fof_info['fof_id'] = fof_id
        return fof_info

    def get_pf_nav_mixed(self, manager_id: str, fof_id: str) -> pd.DataFrame:
        '获取私募基金的各类净值数据'

        def _filter_nav_with_min_max_date(x, min_max_date):
            try:
                return x[~x.datetime.between(min_max_date.at[x.fof_id.array[0], 'min_date'], min_max_date.at[x.fof_id.array[0], 'max_date'])]
            except KeyError:
                return x

        aa = self.get_pf_asset_allocation(manager_id, fof_id)
        fund_id_list = list(aa[aa.asset_type == HoldingAssetType.HEDGE].fund_id.unique()) + [fof_id]
        fof_nav_public = DerivedDataApi().get_fof_nav_public(fund_id_list)
        fof_nav_tl = ResearchApi().get_pf_nav(record_cds=fund_id_list, source='tl')
        if fof_nav_public is None or fof_nav_public.empty:
            fof_nav_public = fof_nav_tl
        else:
            fof_nav_public = fof_nav_public.drop(columns=['update_time', 'create_time', 'is_deleted'])
            if fof_nav_tl is not None:
                fof_nav_tl = fof_nav_tl[['RECORD_CD', 'END_DATE', 'NAV', 'ADJ_NAV', 'ACCUM_NAV']].rename(columns={
                    'RECORD_CD': 'fof_id',
                    'END_DATE': 'datetime',
                    'NAV': 'nav',
                    'ACCUM_NAV': 'acc_net_value',
                    'ADJ_NAV': 'adjusted_nav',
                })
                fof_nav_min_max_date = fof_nav_public.groupby(by='fof_id', sort=False).apply(lambda x: pd.Series({'min_date': x.datetime.min(), 'max_date': x.datetime.max()}))
                fof_nav_tl = fof_nav_tl.groupby(by='fof_id', sort=False, group_keys=False).apply(_filter_nav_with_min_max_date, min_max_date=fof_nav_min_max_date)
                fof_nav_public = pd.concat([fof_nav_public, fof_nav_tl], ignore_index=True).sort_values(by=['fof_id', 'datetime'])
        fof_nav_public['manager_id'] = manager_id
        fof_nav = DerivedDataApi().get_fof_nav(manager_id, fund_id_list)
        if fof_nav is None or fof_nav.empty:
            fof_nav = fof_nav_public
        else:
            fof_nav = fof_nav.drop(columns=['update_time', 'create_time', 'is_deleted'])
            if fof_nav_public is not None:
                fof_nav_min_max_date = fof_nav.groupby(by='fof_id', sort=False).apply(lambda x: pd.Series({'min_date': x.datetime.min(), 'max_date': x.datetime.max()}))
                fof_nav_public = fof_nav_public.groupby(by='fof_id', sort=False, group_keys=False).apply(_filter_nav_with_min_max_date, min_max_date=fof_nav_min_max_date)
                fof_nav = pd.concat([fof_nav, fof_nav_public], ignore_index=True).sort_values(by=['manager_id', 'fof_id', 'datetime'])
        fof_nav = fof_nav[['fof_id', 'datetime', 'nav', 'acc_net_value', 'adjusted_nav']].set_index(['fof_id', 'datetime'])
        fof_nav['v_nav'] = BasicDataApi().get_hedge_fund_email_raw(manager_id, fof_id, fund_id_list).set_index(['fund_id', 'datetime'])['v_nav']
        return fof_nav.reset_index()

    def get_pf_asset_allocation(self, manager_id: str, fof_id: str) -> pd.DataFrame:
        '''获取私募基金的交易记录'''

        df = BasicDataApi().get_fof_asset_allocation(manager_id, [fof_id])
        return df[['fof_id', 'datetime', 'fund_id', 'amount', 'share', 'nav', 'asset_type', 'event_type']]

    def get_pf_positions_detail(self, manager_id: str, fof_id: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        '''获取私募基金每日持仓市值'''

        fof_nav = DerivedDataApi().get_fof_nav(manager_id, [fof_id]).set_index('datetime').sort_index()['nav']
        trading_days = self.get_trading_date(start_date=fof_nav.index.array[0], end_date=fof_nav.index.array[-1])
        fof_nav = fof_nav.reindex(index=trading_days.datetime)
        fof_sa = DerivedDataApi().get_hedge_fund_investor_pur_redemp(manager_id, [fof_id]).set_index('datetime')
        fof_sa_sub = fof_sa.loc[fof_sa.event_type.isin([FOFTradeStatus.PURCHASE, FOFTradeStatus.SUBSCRIBE])]
        fof_sa_redemp = fof_sa.loc[fof_sa.event_type.isin([FOFTradeStatus.REDEEM,])]

        cumshares = fof_sa_sub.share_changed.fillna(0).add(fof_sa_redemp.share_changed.fillna(0), fill_value=0)
        cumshares = cumshares.groupby('datetime').sum().cumsum()

        # fof MV
        fof_mv = cumshares.reindex(fof_nav.index.union(cumshares.index)).ffill() * fof_nav
        pos_df = DerivedDataApi().get_fof_position(manager_id, [fof_id]).set_index('datetime').reindex(index=trading_days.datetime)
        sub_asset_mv = {}
        sub_asset_share = {}

        def _calc_sub_asset_mv(x):
            pos = json.loads(x.position)
            df = pd.DataFrame(pos)
            if df.empty:
                return
            df = df.set_index('fund_id')
            df = df[df.asset_type == HoldingAssetType.HEDGE]
            sub_asset_mv[x.name] = df.share * df.nav
            sub_asset_share[x.name] = df.share
            return

        pos_df[['position']].apply(_calc_sub_asset_mv, axis=1)

        # 子产品MV
        sub_asset_mv_df = pd.DataFrame.from_dict(sub_asset_mv, orient='index')
        sub_asset_mv_df = sub_asset_mv_df.reindex(fof_mv.index.union(sub_asset_mv_df.index))
        sub_asset_mv_df['others_mv'] = fof_mv - sub_asset_mv_df.sum(axis=1)

        # 子产品share
        # sub_asset_share_df = pd.DataFrame.from_dict(sub_asset_share, orient='index')
        # sub_asset_share_df = sub_asset_share_df.reindex(fof_mv.index.union(sub_asset_share_df.index))

        # 子产品损益 = MV + 赎回给的现金 + 分红的现金 - 每次投入的成本
        fof_aa = BasicDataApi().get_fof_asset_allocation(manager_id, [fof_id])
        fof_aa = fof_aa[fof_aa.asset_type == HoldingAssetType.HEDGE].drop(columns='fof_id')

        # 赎回得到的现金
        cash_redemp = fof_aa.loc[fof_aa.event_type == FOFTradeStatus.REDEEM, ['datetime', 'fund_id', 'amount']]
        cash_redemp = cash_redemp.pivot_table(index='datetime', columns='fund_id', values='amount', aggfunc=np.sum)
        cash_redemp = cash_redemp.reindex(fof_nav.index).cumsum().ffill()

        # 成本
        cost = fof_aa.loc[fof_aa.event_type.isin([FOFTradeStatus.PURCHASE, FOFTradeStatus.SUBSCRIBE]), ['datetime', 'fund_id', 'amount']]
        cost = cost.pivot_table(index='datetime', columns='fund_id', values='amount', aggfunc=np.sum).cumsum().reindex(fof_nav.index).ffill()

        # 现金分红
        cash_dividend = fof_aa.loc[fof_aa.event_type==FOFTradeStatus.DIVIDEND_CASH, ['datetime', 'fund_id', 'amount']]
        if cash_dividend.empty:
            cash_dividend = None
        else:
            cash_dividend = cost.pivot_table(index='datetime', columns='fund_id', values='amount', aggfunc=np.sum).cumsum().reindex(fof_nav.index).ffill()

        if not cash_redemp.empty:
            sub_asset_pal_fixed = sub_asset_mv_df.add(cash_redemp.fillna(0), fill_value=0)
        else:
            sub_asset_pal_fixed = sub_asset_mv_df

        if cash_dividend is not None and not cash_redemp.empty:
            sub_asset_pal_fixed = sub_asset_pal_fixed.add(cash_dividend.fillna(0), fill_value=0).sub(cost.fillna(0), fill_value=0)
        else:
            sub_asset_pal_fixed = sub_asset_pal_fixed.sub(cost.fillna(0), fill_value=0)
        return sub_asset_mv_df, sub_asset_pal_fixed

    def get_trading_date(self, asset_type='cn_stock', start_date=None, end_date=None):
        from .basic import TradingDayList
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                        TradingDayList
                    )
                if start_date:
                    query = query.filter(
                        TradingDayList.datetime >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        TradingDayList.datetime <= end_date,
                    )
                tag_df = pd.read_sql(query.statement, query.session.bind)
                return tag_df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {TradingDayList.__tablename__}')


    def get_main_ticker(self, start_date=None,end_date=None,prod_list=None):
        try:
            with DerivedDatabaseConnector().managed_session() as db_session:
                query = db_session.query(
                    FutureMainChainRet.datetime,
                    FutureMainChainRet.future_type_id,
                    FutureMainChainRet.ticker,
                )
                if prod_list:
                    _prod_list = [_.lower() for _ in prod_list]
                    prod_list = prod_list + _prod_list
                    query = query.filter(
                        FutureMainChainRet.future_type_id.in_(prod_list),
                    )
                if start_date:
                    query = query.filter(
                        FutureMainChainRet.datetime >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        FutureMainChainRet.datetime <= end_date,
                    )
                return pd.read_sql(query.statement, query.session.bind)
        
        except Exception as e:
            print(f'failed to get_future_main_chain_ret <err_msg> {e} from {FutureTypeClassification.__tablename__}')

    def get_future_and_spot_quote(self,start_date=None,end_date=None,prod_list=None):
        try:
            main_ticker_info = self.get_main_ticker(start_date=start_date,end_date=end_date,prod_list=prod_list)
            close_price = self.get_future_quote(future_ids=main_ticker_info.ticker.unique().tolist(),start_date=start_date,end_date=end_date)
            close_price = close_price.pivot_table(index='datetime',columns='em_id',values='close')
            close_price.columns.name = 'ticker'
            _close_price = close_price.unstack().rename('close').to_frame()
            future_list = main_ticker_info.future_type_id.unique().tolist()
            result = []
            for future_i in future_list:
                # 双重index对齐
                _df = main_ticker_info[main_ticker_info.future_type_id == future_i].sort_values('datetime')
                _df = _df.set_index(['ticker','datetime'])
                _df = _df.join(_close_price).reset_index() 
                spot_info = RawDataApi().get_em_future_spot_info(future_type=[future_i])
                spot_df = RawDataApi().get_em_future_spot_price(spot_ids=spot_info.spot_id.tolist(),start_date=start_date,end_date=end_date)
                spot_df = spot_df.set_index('datetime')[['price']].rename(columns={'price':'spot_price'})
                _df = _df.set_index('datetime').join(spot_df)
                result.append(_df)
            result = pd.concat(result)
            return result
        except Exception as e:
            print(f'failed to get_future_and_spot_quote <err_msg> {e} from {FutureTypeClassification.__tablename__}')

    def get_main_price_with_em_id(self, begin_date=None, end_date=None, future_id_list=[]):
        '''
        获取期货主连数据 id em_id
        '''
        try:
            with DerivedDatabaseConnector().managed_session() as db_session:
                query = db_session.query(
                    FutureMainChainRet)
                if future_id_list:
                    query = query.filter(
                        FutureMainChainRet.future_type_id.in_(future_id_list),
                    )
                if begin_date:
                    query = query.filter(
                        FutureMainChainRet.datetime >= begin_date,
                    )
                if end_date:
                    query = query.filter(
                        FutureMainChainRet.datetime <= end_date,
                    )

                return pd.read_sql(query.statement, query.session.bind).drop(columns=['_update_time'])
           
        except Exception as e:
            print(f'failed to get_main_price_with_em_id <err_msg> {e}')


    def get_main_price(self,tps=None,start_date=None,end_date=None):
        '''
        获取期货主连数据及所属主力合约行情
        tps 品种类别
        id trading_id
        '''
        try:
            with DerivedDatabaseConnector().managed_session() as db_session:
                query = db_session.query(
                    FutureMainChainRet.datetime,
                    FutureMainChainRet.future_type_id,
                    FutureMainChainRet.ticker,
                    FutureMainChainRet.ret,
                )
                if tps:
                    query = query.filter(
                        FutureMainChainRet.future_type_id.in_(tps),
                    )
                if start_date:
                    query = query.filter(
                        FutureMainChainRet.datetime >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        FutureMainChainRet.datetime <= end_date,
                    )
                df = pd.read_sql(query.statement, query.session.bind)
                future_id_list = df.ticker.unique().tolist()

            with RawDatabaseConnector().managed_session() as db_session:
                query = db_session.query(
                    EmFutureInfoDetail.EMCODE,
                    EmFutureInfoDetail.TRADINGCODE,
                )
                if tps:
                    query = query.filter(
                        EmFutureInfoDetail.EMCODE.in_(future_id_list)
                )
                future_info = pd.read_sql(query.statement, query.session.bind)
                future_id_list = df.ticker.unique().tolist()
                dic = future_info.set_index('em_id')['trading_code'].to_dict()
                df['ticker'] = df.ticker.map(dic)
            df = df.set_index(['datetime','ticker'])
            future_price = self.get_future_price(tps=tps,start_date=start_date,end_date=end_date)
            future_price = future_price.set_index(['datetime','ticker'])
            df = df.join(future_price).reset_index()
            tds = pd.to_datetime(df.datetime)
            tds = [i.date() for i in tds]
            df.datetime = tds
            df = df.drop(columns=['future_type_id'])
            return df

        except Exception as e:
            print(f'failed to get_main_price <err_msg> {e}')

    def get_future_price(self,tps=None,start_date=None,end_date=None):
        '''
        获取期货行情数据
        '''
        try:
            # 获取期货品种名称
            with DerivedDatabaseConnector().managed_session() as db_session:
                query = db_session.query(
                    FutureTypeClassification.future_type_id,
                    FutureTypeClassification.desc_name,
                )
                if tps:
                    query = query.filter(
                        FutureTypeClassification.future_type_id.in_(tps),
                    )
                future_type_df = pd.read_sql(query.statement, query.session.bind)
                desc_name_list = future_type_df.desc_name.unique().tolist()

            # 获取期货合约代码
            with RawDatabaseConnector().managed_session() as db_session:
                query = db_session.query(
                    EmFutureInfoDetail.EMCODE,
                    EmFutureInfoDetail.FTTRANSTYPE,
                    EmFutureInfoDetail.TRADINGCODE,
                )
                if tps:
                    query = query.filter(
                        EmFutureInfoDetail.FTTRANSTYPE.in_(desc_name_list)
                )
                dic = future_type_df.set_index('desc_name')['future_type_id'].to_dict()
                future_info = pd.read_sql(query.statement, query.session.bind)
                future_info['future_type_id'] = future_info.trans_type.map(dic)
                
                future_ids = future_info.em_id.tolist()
                query = db_session.query(
                        EmFuturePriceDetail.CODES,
                        EmFuturePriceDetail.DATES,
                        EmFuturePriceDetail.OPEN,
                        EmFuturePriceDetail.HIGH,
                        EmFuturePriceDetail.LOW,
                        EmFuturePriceDetail.CLOSE,
                        EmFuturePriceDetail.PRECLOSE,
                        EmFuturePriceDetail.AVERAGE,
                        EmFuturePriceDetail.VOLUME,
                        EmFuturePriceDetail.AMOUNT,
                        EmFuturePriceDetail.HQOI,
                        EmFuturePriceDetail.CLEAR,
                        EmFuturePriceDetail.PRECLEAR,
                    ).filter(EmFuturePriceDetail.CODES.in_(future_ids))
                if start_date:
                    query = query.filter(EmFuturePriceDetail.DATES >= start_date)
                if end_date:
                    query = query.filter(EmFuturePriceDetail.DATES <= end_date)
                df = pd.read_sql(query.statement, query.session.bind).drop(columns = "_update_time", errors='ignore')
                df['ticker'] = df.em_id.map(future_info.set_index('em_id')['trading_code'].to_dict())
                df['product'] = df.em_id.map(future_info.set_index('em_id')['future_type_id'].to_dict())

                l = df.columns.tolist()
                target_cols = ['ticker','product']
                cols = target_cols + [i for i in l if i not in target_cols]
                df = df[cols]
            return df.drop(columns=['em_id'])

        except Exception as e:
            print(f'failed to get_future_price <err_msg> {e}')

    def get_holidays(self):
        '''
            func: 读取节假日序列
            e.g. hol = get_holidays()
            out: dict, hol['sse']是上交所节假日序列
        '''
        with BasicDatabaseConnector().managed_session() as db_session:
            query = db_session.query(
                    ExchangeHoliday
                )
            data = pd.read_sql(query.statement, query.session.bind)
                    
        hol = {}
        for exch in data['exch_id'].unique():
            hol[exch] = list(data.loc[data['exch_id']==exch, 'datetime'])
        
        return hol

    def is_trading_day(self, T, exch='sse'):
        '''
            func: 判断是否交易日
            exch: 'sse', 'szse', 'nyse', 'lse', 'tse', 'hkex', 'fse'
            e.g. tmp = is_trading_day(dt.date(2020,3,11), 'sse')
            out: True or False

        '''
        return T in self.get_tdates(start_date=T, end_date=T)

    def prev_tdate(self,T, exch='sse'):
        '''
            func: 计算前一个交易日
            exch: 'sse', 'szse', 'nyse', 'lse', 'tse', 'hkex', 'fse'
            e.g. T1 = prev_tdate(dt.date(2020,3,11), 'sse')
            out: dt.date

        '''
        # 检查输入参数
        assert(exch in ['sse', 'szse', 'nyse', 'lse', 'tse', 'hkex', 'fse'])
        T1 = T + datetime.timedelta(days=-1)
        hol = self.get_holidays()
        while ((T1 in hol[exch]) or (T1.weekday() in [5, 6])):
            T1 = T1 + datetime.timedelta(days=-1)
        return T1

    def next_tdate(self, T, exch='sse'):
        '''
            func: 计算后一个交易日
            exch: 'sse', 'szse', 'nyse', 'lse', 'tse', 'hkex', 'fse'
            e.g. T1 = next_tdate(dt.date(2020,3,11), 'sse')
            out: dt.date

        '''
        # 检查输入参数
        assert(exch in ['sse', 'szse', 'nyse', 'lse', 'tse', 'hkex', 'fse'])
        hol = self.get_holidays()
        T1 = T + datetime.timedelta(days=1)
        while((T1 in hol[exch]) or (T1.weekday() in [5, 6])):
            T1 = T1 + datetime.timedelta(days=1)
        return T1

    def tdate_shift(self, T, N, exch='sse'):
        '''
            func: 前寻或后寻第N个交易日
            T: 'yyyy-mm-dd' or dt.date
            N: 整数，负数表示向前（过去）寻找，正数表示向后（未来）寻找
            exch: 'sse', 'szse', 'nyse', 'lse', 'tse', 'hkex', 'fse'
            e.g. T1 = tdate_shift(dt.date(2020,3,11), 2, 'sse')
            out: dt.date
        '''

        # 检查输入参数
        if type(T) == str:
            T = datetime.datetime.strptime(T,'%Y-%m-%d').date()
        assert(type(N)==int)
        assert(exch in ['sse', 'szse', 'nyse', 'lse', 'tse', 'hkex', 'fse'])
        # 计算后一交易日
        T1 = T
        for n in range(abs(N)):
            T1 = self.prev_tdate(T1, exch) if N<0 else self.next_tdate(T1, exch)
        return T1


    def get_tdates(self, start_date=None, end_date=None, exch='sse'):
        '''
            func: 生成交易日序列
            start_date: 'yyyy-mm-dd' or dt.date
            end_date: 'yyyy-mm-dd' or dt.date
            exch: 'sse', 'szse', 'nyse', 'lse', 'tse', 'hkex', 'fse'
            e.g. dates = get_tdates('2020-1-1', '2020-3-1', 'sse')
            out: list of dt.date
            bug: 如果start_date太早，会因为没有holidays记录，而取出过多的交易日序列
        '''

        # 检查输入参数
        if start_date is None:
            start_date = datetime.date(1991,1,1)
        if end_date is None: #TODO 假期数据截止到2021年当年
            end_date = datetime.date(2022,1,1)
        start_date = pd.to_datetime(start_date).date()
        end_date = pd.to_datetime(end_date).date()
        if start_date > end_date:
            return []
        assert(exch in ['sse', 'szse', 'nyse', 'lse', 'tse', 'hkex', 'fse'])
        # 计算自然日序列
        dates = [start_date]
        while(dates[-1] < end_date):
            dates.append(dates[-1] + datetime.timedelta(days=1))
        hol = self.get_holidays()
        # 剔除节假日和周六日
        dates = [d for d in dates if ((d not in hol[exch]) and (d.weekday() not in [5, 6]))]
        return dates


if __name__ == '__main__':
    start_date = datetime.date(2019,1,1)
    end_date = datetime.date(2021,2,1)

    # 私募 信息 
    record_cd = ['SE1387','SE1383']
    #name_list = ['黑翼','CTA']
    #stg_name = ['股票策略']
    #stg_child = ['主观套利','指数增强']
    #company_name = ['黑翼']
    #start_date = datetime.date(2020,1,1)
    #mng_name = ['蒋彤','蒋锦志']
    # 选填
    ResearchApi().get_pf_info(record_cd=record_cd)

    # 私募净值
    record_cds = ['SE1387','SE1383']
    df = ResearchApi().get_pf_nav(record_cds=record_cds,
                                start_date=start_date,
                                end_date=end_date)
                            