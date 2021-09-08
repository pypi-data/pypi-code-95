import os

import pandas as pd

from SapphireQuant.Lib.FileToolBox import FileToolBox


class MongoHelper:
    """
    MongoDbHelper
    """

    @staticmethod
    def export_factor_record(db_client, target_dir, factor_id):
        """
        根据因子ID、合约编号导出指定的数据集合，从min_factor库中
        :param target_dir:导出目录
        :param factor_id:因子ID
        :param db_client: Mongo客户端
        """
        factor_record_db = db_client.min_factor
        factor_record_collection = factor_record_db[str(factor_id)]
        factor_record_list = factor_record_collection.find()
        for factor_record in factor_record_list:
            df_asset = pd.DataFrame(factor_record['asset'])
            df_trade = pd.DataFrame(factor_record['trade'])
            df_summary = pd.DataFrame([factor_record['summary']])
            df_param = pd.DataFrame([factor_record['param']]).T
            account_id = factor_record['account_id']

            try:
                excel_record_path = '{0}/{1}/{2}.xlsx'.format(target_dir, factor_id, account_id)
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)

                dic_data = {
                    'Asset': df_asset,
                    'Trade': df_trade,
                    'Summary': df_summary,
                    'Param': df_param,
                }
                FileToolBox.save_excel(excel_record_path, **dic_data)
                fig_record_path = os.path.join(target_dir, factor_id, '{0}.png'.format(account_id))
                df_asset['累计收益率(%)'] = df_asset['累计收益率'].str.strip('%').astype(float) / 100
                FileToolBox.save_fig(fig_record_path, df_asset, '日期', ['累计收益率(%)'])
            except Exception as e:
                print(str(e))

    @staticmethod
    def export_factor_record_by_instrument_id(db_client, target_dir, factor_id, instrument_id):
        """
        根据因子ID、合约编号导出指定的数据集合，从min_factor库中
        :param target_dir:导出目录
        :param factor_id:因子ID
        :param instrument_id:合约编号
        :param db_client: Mongo客户端
        """
        factor_record_db = db_client.min_factor
        factor_record_collection = factor_record_db[str(factor_id)]
        factor_record_list = factor_record_collection.find({'instrument_id': str(instrument_id)})
        for factor_record in factor_record_list:
            df_asset = pd.DataFrame(factor_record['asset'])
            df_trade = pd.DataFrame(factor_record['trade'])
            df_summary = pd.DataFrame([factor_record['summary']])
            df_param = pd.DataFrame([factor_record['param']]).T
            account_id = factor_record['account_id']

            try:
                excel_record_path = '{0}/{1}/{2}.xlsx'.format(target_dir, factor_id, account_id)
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)

                dic_data = {
                    'Asset': df_asset,
                    'Trade': df_trade,
                    'Summary': df_summary,
                    'Param': df_param,
                }
                FileToolBox.save_excel(excel_record_path, **dic_data)
                fig_record_path = os.path.join(target_dir, factor_id, '{0}.png'.format(account_id))
                df_asset['累计收益率(%)'] = df_asset['累计收益率'].str.strip('%').astype(float) / 100
                FileToolBox.save_fig(fig_record_path, df_asset, '日期', ['累计收益率(%)'])
            except Exception as e:
                print(str(e))

    @staticmethod
    def export_factor_record_by_account_id(db_client, target_dir, factor_id, account_id):
        """
        根据因子ID、合约编号导出指定的数据集合
        :param db_client:
        :param account_id:
        :param target_dir:导出目录
        :param factor_id:因子ID
        """
        factor_record_db = db_client.min_factor
        factor_record_collection = factor_record_db[str(factor_id)]
        factor_record_list = factor_record_collection.find({'account_id': str(account_id)})
        for factor_record in factor_record_list:
            df_asset = pd.DataFrame(factor_record['asset'])
            df_trade = pd.DataFrame(factor_record['trade'])
            df_summary = pd.DataFrame([factor_record['summary']])
            df_param = pd.DataFrame([factor_record['param']]).T
            account_id = factor_record['account_id']

            try:
                excel_record_path = '{0}/{1}/{2}.xlsx'.format(target_dir, factor_id, account_id)
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)

                dic_data = {
                    'Asset': df_asset,
                    'Trade': df_trade,
                    'Summary': df_summary,
                    'Param': df_param,
                }
                FileToolBox.save_excel(excel_record_path, **dic_data)
                fig_record_path = os.path.join(target_dir, factor_id, '{0}.png'.format(account_id))
                df_asset['累计收益率(%)'] = df_asset['累计收益率'].str.strip('%').astype(float) / 100
                FileToolBox.save_fig(fig_record_path, df_asset, '日期', ['累计收益率(%)'])
            except Exception as e:
                print(str(e))

    @staticmethod
    def export_factor_record_net_fig(db_client, target_dir, factor_id, instrument_id):
        """
        根据因子ID、合约编号导出指定的净值走势
        :param db_client:
        :param target_dir:导出目录
        :param factor_id:因子ID
        :param instrument_id:合约编号
        """
        factor_record_db = db_client.min_factor
        factor_record_collection = factor_record_db[str(factor_id)]
        factor_record_list = factor_record_collection.find({'instrument_id': str(instrument_id)})
        for factor_record in factor_record_list:
            df_asset = pd.DataFrame(factor_record['asset'])
            account_id = factor_record['account_id']
            try:
                fig_record_path = os.path.join(target_dir, '{0}.png'.format(account_id))
                df_asset['累计收益率(%)'] = df_asset['累计收益率'].str.strip('%').astype(float) / 100
                FileToolBox.save_fig(fig_record_path, df_asset, '日期', ['累计收益率(%)'])
            except Exception as e:
                print(str(e))

    @staticmethod
    def export_factor_record_net_fig_by_account_id(db_client, target_dir, factor_id, account_id):
        """
        根据因子ID、合约编号导出指定的净值走势
        :param db_client:
        :param factor_id:
        :param target_dir:导出目录
        :param account_id:
        """
        factor_record_db = db_client.min_factor
        factor_record_collection = factor_record_db[str(factor_id)]
        factor_record_list = factor_record_collection.find({'account_id': str(account_id)})
        for factor_record in factor_record_list:
            df_asset = pd.DataFrame(factor_record['asset'])
            account_id = factor_record['account_id']
            try:
                fig_record_path = os.path.join(target_dir, '{0}.png'.format(account_id))
                df_asset['累计收益率(%)'] = df_asset['累计收益率'].str.strip('%').astype(float) / 100
                FileToolBox.save_fig(fig_record_path, df_asset, '日期', ['累计收益率(%)'])
            except Exception as e:
                print(str(e))

    @staticmethod
    def get_summary_year_by_account_id(db_client, account_id):
        """
        根据因子ID、合约编号导出指定的数据集合
        :param db_client:
        :param account_id:
        """
        factor_filter_db = db_client.summary_by_year
        factor_filter_collection = factor_filter_db['min']
        factor_filter_list = factor_filter_collection.find({'account_id': account_id})
        df_all_summary = None
        for factor_filter in factor_filter_list:
            df_summary = pd.DataFrame([factor_filter['summary']])
            if df_all_summary is None:
                df_all_summary = df_summary
            else:
                df_all_summary = df_all_summary.append(df_summary)

        return df_all_summary

    @staticmethod
    def export_factor_filter_record(db_client, target_dir):
        """
        根据因子ID、合约编号导出指定的数据集合
        :param db_client:
        :param target_dir:导出目录
        """
        factor_filter_db = db_client.summary_filter
        factor_filter_collection = factor_filter_db['min']
        factor_filter_list = factor_filter_collection.find()
        df_all_summary = None
        df_all_summary_by_year = None
        for factor_filter in factor_filter_list:
            df_summary = pd.DataFrame([factor_filter['summary']])
            if df_all_summary is None:
                df_all_summary = df_summary
            else:
                df_all_summary = df_all_summary.append(df_summary)
            factor_id = factor_filter['summary']['FactorId']
            account_id = factor_filter['account_id']

            MongoHelper.export_factor_record_by_account_id(db_client, os.path.join(target_dir, 'MinFactor'), factor_id, account_id)
            df_summary_by_year = MongoHelper.get_summary_year_by_account_id(db_client, account_id)
            if df_all_summary_by_year is None:
                df_all_summary_by_year = df_summary_by_year
            else:
                df_all_summary_by_year = df_all_summary_by_year.append(df_summary_by_year)
        FileToolBox.save_csv(df_all_summary, os.path.join(target_dir, 'AllSummary.csv'))
        FileToolBox.save_csv(df_all_summary_by_year, os.path.join(target_dir, 'AllSummaryByYear.csv'))

# db_host = 'mongodb://admin:123456@192.168.1.202:27017/'
# export_dir = 'D:/MongodbRecord'
# client = MongoClient(db_host)
# MongoHelper.export_factor_filter_record(os.path.join(export_dir, 'FactorFilter'))
# MongoHelper.export_factor_record_by_instrument_id(os.path.join(export_dir, 'MinFactor'))
