"""
私募基金估值表持仓入库
"""
import os
import pandas as pd
from hbshare.asset_allocation.macro_index.util import create_table, delete_duplicate_records, WriteToDB


class HoldingExtractor:
    def __init__(self, data_path, table_name, fund_name, is_increment=1):
        self.data_path = data_path
        self.table_name = table_name
        self.fund_name = fund_name
        self.is_increment = is_increment

    def _load_portfolio_weight(self):
        filenames = os.listdir(self.data_path)
        filenames = [x for x in filenames if x.split('.')[-1] == 'xls']

        portfolio_weight_list = []
        for name in filenames:
            date = name.split('_')[-2]
            data = pd.read_excel(os.path.join(self.data_path, name), sheet_name=0, header=3)
            sh = data[data['科目代码'].str.startswith('11020101')]
            sz = data[data['科目代码'].str.startswith('11023101')]
            cyb = data[data['科目代码'].str.startswith('11024101')]
            kcb = data[data['科目代码'].str.startswith('1102C101')]
            df = pd.concat([sh, sz, cyb, kcb], axis=0).dropna()
            df['ticker'] = df['科目代码'].apply(lambda x: x[-6:])
            df.rename(columns={"科目名称": "sec_name", "市值占净值%": "weight"}, inplace=True)
            df['trade_date'] = date
            portfolio_weight_list.append(df[['trade_date', 'ticker', 'sec_name', 'weight']])

        portfolio_weight_df = pd.concat(portfolio_weight_list)
        portfolio_weight_df['fund_name'] = self.fund_name

        return portfolio_weight_df

    def writeToDB(self):
        if self.is_increment == 1:
            data = self._load_portfolio_weight()
            trading_day_list = data['trade_date'].unique().tolist()
            sql_script = "delete from {} where trade_date in ({}) and fund_name = '{}'".format(
                self.table_name, ','.join(trading_day_list), self.fund_name)
            # delete first
            delete_duplicate_records(sql_script)
            # add new records
            WriteToDB().write_to_db(data, self.table_name)
        else:
            sql_script = """
                create table mac_inflation(
                id int auto_increment primary key,
                trade_date date not null unique,
                CPI_yoy decimal(4, 2),
                PPI_yoy decimal(4, 2),
                LME decimal(7, 2)) 
            """
            create_table(self.table_name, sql_script)
            data = self._load_portfolio_weight()
            WriteToDB().write_to_db(data, self.table_name)


if __name__ == '__main__':
    HoldingExtractor(data_path='D:\\研究基地\\机器学习类\\因诺\\聚配500估值表及绩效报告',
                     table_name="private", fund_name="因诺聚配中证500指数增强").writeToDB()