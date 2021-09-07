#  The MIT License (MIT)
#
#  Copyright (c) 2021. Scott Lau
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

import logging
import os

import pandas as pd
from pandas import ExcelWriter

from ..utils import ConfigUtils


class PointsAnalyzer:
    """
    积分分析类
    """

    def __init__(self):
        # 业务类型
        self._business_type = "周周赛"
        self._key_enabled = "weekly.enabled"
        self._read_config()

    def _enabled(self):
        """
        是否启用分析
        :return: 是否启用分析
        """
        config = ConfigUtils.get_config()
        # 配置不存在默认不启用分析
        enabled_config = config.get(self._key_enabled)
        return False if enabled_config is None else enabled_config

    def get_business_type(self) -> str:
        """
        业务类型
        :return: 业务类型
        """
        return self._business_type

    def _read_config(self):
        """
        读取配置，初始化相关变量
        """
        config = ConfigUtils.get_config()
        # 生成的目标Excel文件存放路径
        self._target_directory = config.get("weekly.target_directory")
        # 待分析文件路径
        self._source_file_path = config.get("weekly.source_file_path")
        self._sheet_name = config.get("weekly.sheet_name")
        self._header_row = config.get("weekly.sheet_config.header_row")
        # 目标文件名称
        self._target_filename = config.get("weekly.target_filename")
        self._target_filename_full_path = os.path.join(self._target_directory, self._target_filename)
        # 周积分名称
        self._weekly_summary_name = config.get("weekly.weekly_summary_name")
        # 月积分名称
        self._monthly_summary_name = config.get("weekly.monthly_summary_name")
        # 年积分名称
        self._yearly_summary_name = config.get("weekly.yearly_summary_name")
        # 主管经理汇总
        self._manager_summary_name = config.get("weekly.manager_summary_name")
        # 对公指标
        self._corporate_name = config.get("weekly.corporate.name")
        # 普惠指标
        self._finance_name = config.get("weekly.finance.name")
        # 零售指标
        self._retail_name = config.get("weekly.retail.name")
        # 对公指标
        self._corporate_point_config = config.get("weekly.corporate.point_config")
        # 普惠指标
        self._finance_point_config = config.get("weekly.finance.point_config")
        # 零售指标
        self._retail_point_config = config.get("weekly.retail.point_config")
        # 机构归属配置
        self._attribution_mapping = config.get("branch.attribution_mapping")
        # 主管排序规则
        self._manager_order = config.get("branch.manager_order")
        self._key_point_value = 'point_value'

    def _read_src_file(self) -> pd.DataFrame:
        """
        读取Excel或CSV文件，获取DataFrame
        :return: DataFrame
        """
        logging.getLogger(__name__).info("读取源文件：{}".format(self._source_file_path))
        data = pd.read_excel(self._source_file_path, sheet_name=self._sheet_name, header=self._header_row)
        # 没有业绩的显示0
        data.fillna(0, inplace=True)
        self._team_column_name = data.columns[0]
        return data

    def analysis(self) -> int:
        """
        主分析流程分析

        :return: 分析结果
        """
        # 如果未启用，则直接返回花名册数据
        if not self._enabled():
            logging.getLogger(__name__).info("{} 分析未启用".format(self._business_type))
            return 0
        logging.getLogger(__name__).info("开始分析 {} 数据".format(self._business_type))
        logging.getLogger(__name__).info("输出文件：{} ".format(self._target_filename_full_path))
        with ExcelWriter(self._target_filename_full_path) as excel_writer:
            # 读取Excel或CSV文件，获取DataFrame
            data = self._read_src_file()
            data = self._calculate_weekly_points(data)
            data = self._calculate_monthly_points(data)
            data = self._calculate_yearly_points(data)
            self._write_weekly_reports(excel_writer, data)
            self._write_manager_reports(excel_writer, data)
        logging.getLogger(__name__).info("完成分析 {} 数据".format(self._business_type))
        return 0

    def _calculate_weekly_points(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算周积分

        :param data: 原始数据
        :return: 分析后数据
        """
        self._weekly_target_columns = list()
        # 团队列
        self._weekly_target_columns.append(self._team_column_name)
        # 对公周积分
        weekly_corporate_points_column = self._corporate_name + self._weekly_summary_name
        # 普惠周积分
        weekly_finance_points_column = self._finance_name + self._weekly_summary_name
        # 零售周积分
        weekly_retail_points_column = self._retail_name + self._weekly_summary_name
        # 对公周积分
        data[weekly_corporate_points_column] = 0
        for key, value_and_unique in self._corporate_point_config.items():
            self._weekly_target_columns.append(key)
            point_value = value_and_unique[self._key_point_value]
            add_value = data[key] * point_value
            data[weekly_corporate_points_column] = data[weekly_corporate_points_column] + add_value
        self._weekly_target_columns.append(weekly_corporate_points_column)

        # 普惠周积分
        data[weekly_finance_points_column] = 0
        for key, value_and_unique in self._finance_point_config.items():
            self._weekly_target_columns.append(key)
            point_value = value_and_unique[self._key_point_value]
            add_value = data[key] * point_value
            data[weekly_finance_points_column] = data[weekly_finance_points_column] + add_value
        self._weekly_target_columns.append(weekly_finance_points_column)

        # 对公周积分
        data[weekly_retail_points_column] = 0
        for key, value_and_unique in self._retail_point_config.items():
            self._weekly_target_columns.append(key)
            point_value = value_and_unique[self._key_point_value]
            add_value = data[key] * point_value
            data[weekly_retail_points_column] = data[weekly_retail_points_column] + add_value
        self._weekly_target_columns.append(weekly_retail_points_column)

        data[self._weekly_summary_name] = 0
        data[self._weekly_summary_name] = data[self._weekly_summary_name] + data[weekly_corporate_points_column]
        data[self._weekly_summary_name] = data[self._weekly_summary_name] + data[weekly_finance_points_column]
        data[self._weekly_summary_name] = data[self._weekly_summary_name] + data[weekly_retail_points_column]
        # 输出列
        self._weekly_target_columns.append(self._weekly_summary_name)
        # 添加主管行长列
        data[self._manager_summary_name] = data[self._team_column_name]
        data = data.replace({self._manager_summary_name: self._attribution_mapping})
        return data

    def _calculate_monthly_points(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算月积分

        :param data: 原始数据
        :return: 分析后数据
        """
        # 对公月积分
        monthly_corporate_points_column = self._corporate_name + self._monthly_summary_name
        # 普惠月积分
        monthly_finance_points_column = self._finance_name + self._monthly_summary_name
        # 零售月积分
        monthly_retail_points_column = self._retail_name + self._monthly_summary_name
        data[self._monthly_summary_name] = 0
        data[self._monthly_summary_name] = data[self._monthly_summary_name] + data[monthly_corporate_points_column]
        data[self._monthly_summary_name] = data[self._monthly_summary_name] + data[monthly_finance_points_column]
        data[self._monthly_summary_name] = data[self._monthly_summary_name] + data[monthly_retail_points_column]
        # 输出列
        self._weekly_target_columns.append(self._monthly_summary_name)
        return data

    def _calculate_yearly_points(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算年积分

        :param data: 原始数据
        :return: 分析后数据
        """
        # 对公年积分
        yearly_corporate_points_column = self._corporate_name + self._yearly_summary_name
        # 普惠年积分
        yearly_finance_points_column = self._finance_name + self._yearly_summary_name
        # 零售年积分
        yearly_retail_points_column = self._retail_name + self._yearly_summary_name
        data[self._yearly_summary_name] = 0
        data[self._yearly_summary_name] = data[self._yearly_summary_name] + data[yearly_corporate_points_column]
        data[self._yearly_summary_name] = data[self._yearly_summary_name] + data[yearly_finance_points_column]
        data[self._yearly_summary_name] = data[self._yearly_summary_name] + data[yearly_retail_points_column]
        # 输出列
        self._weekly_target_columns.append(self._yearly_summary_name)
        return data

    def _write_weekly_reports(self, excel_writer: ExcelWriter, data: pd.DataFrame) -> None:
        """
        写周积分报表

        :param excel_writer: excel操作类
        :param data: 原始数据
        :return:
        """
        # 选择输出列
        result = data[self._weekly_target_columns]
        # 按月积分排序
        result = result.sort_values(by=self._monthly_summary_name, ascending=False)
        result.to_excel(excel_writer=excel_writer, index=False, sheet_name=self._weekly_summary_name)

    def _write_manager_reports(self, excel_writer: ExcelWriter, data: pd.DataFrame) -> None:
        """
        写主管经理积分报表

        :param excel_writer: excel操作类
        :param data: 原始数据
        :return:
        """
        result = pd.pivot_table(
            data=data,
            index=[self._team_column_name, self._manager_summary_name],
            values=[self._weekly_summary_name, self._monthly_summary_name, self._yearly_summary_name],
            fill_value=0,
        )
        result.reset_index(inplace=True)
        # 添加周积分合计（按主管行长）
        weekly_group_sum_by_manager = result.groupby(
            by=self._manager_summary_name
        )[self._weekly_summary_name].sum().to_dict()
        weekly_sum_by_manager_col = self._weekly_summary_name + "合计（按{}）".format(self._manager_summary_name)
        result[weekly_sum_by_manager_col] = result[self._manager_summary_name].map(weekly_group_sum_by_manager)
        # 添加周积分平均值（按主管行长
        weekly_group_avg_by_manager = result.groupby(
            by=self._manager_summary_name
        )[self._weekly_summary_name].mean().to_dict()
        weekly_avg_by_manager_col = self._weekly_summary_name + "平均值（按{}）".format(self._manager_summary_name)
        result[weekly_avg_by_manager_col] = result[self._manager_summary_name].map(weekly_group_avg_by_manager)

        # 添加月积分合计（按主管行长）
        monthly_group_sum_by_manager = result.groupby(
            by=self._manager_summary_name
        )[self._monthly_summary_name].sum().to_dict()
        monthly_sum_by_manager_col = self._monthly_summary_name + "合计（按{}）".format(self._manager_summary_name)
        result[monthly_sum_by_manager_col] = result[self._manager_summary_name].map(monthly_group_sum_by_manager)

        # 添加月积分平均值（按主管行长）
        monthly_group_avg_by_manager = result.groupby(
            by=self._manager_summary_name
        )[self._monthly_summary_name].mean().to_dict()
        monthly_avg_by_manager_col = self._monthly_summary_name + "平均值（按{}）".format(self._manager_summary_name)
        result[monthly_avg_by_manager_col] = result[self._manager_summary_name].map(monthly_group_avg_by_manager)

        # 添加周积分合计（按主管行长）
        yearly_group_sum_by_manager = result.groupby(
            by=self._manager_summary_name
        )[self._yearly_summary_name].sum().to_dict()
        yearly_sum_by_manager_col = self._yearly_summary_name + "合计（按{}）".format(self._manager_summary_name)
        result[yearly_sum_by_manager_col] = result[self._manager_summary_name].map(yearly_group_sum_by_manager)

        # 是否使用升序排序
        ascending = False
        # 主管按升序排序
        manager_order = dict(sorted(self._manager_order.items(), key=lambda d: d[1], reverse=not ascending))
        result[self._manager_summary_name] = pd.Categorical(result[self._manager_summary_name], manager_order.keys())

        # 按周积分排序
        result = result.sort_values(
            by=[self._manager_summary_name, self._weekly_summary_name],
            # 周积分按降序排序
            ascending=ascending,
        )
        result = result[[
            self._manager_summary_name,
            self._team_column_name,
            self._weekly_summary_name,
            weekly_sum_by_manager_col,
            weekly_avg_by_manager_col,
            self._monthly_summary_name,
            monthly_sum_by_manager_col,
            monthly_avg_by_manager_col,
            self._yearly_summary_name,
            yearly_sum_by_manager_col,
        ]]
        result.to_excel(excel_writer=excel_writer, index=False, sheet_name=self._manager_summary_name)
