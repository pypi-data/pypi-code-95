import glob
import os
import shutil
import threading
import zipfile

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import ticker


class FileToolBox:
    @staticmethod
    def save_csv(record_path, df_data, index=False):
        """
        保存DataFrame对象到指定地址
        :param index:
        :param df_data:
        :param record_path:
        """
        try:
            record_deep_dir = os.path.dirname(record_path)
            if not os.path.exists(record_deep_dir):
                os.makedirs(record_deep_dir)

            if os.path.exists(record_path):
                os.remove(record_path)

            print('save_csv:{0}'.format(record_path))
            df_data.to_csv(record_path, encoding='utf-8', index=index)
        except Exception as e:
            print(str(e))

    @staticmethod
    def save_excel(record_path, **kwargs):
        """
        保存Excel
        :param record_path:
        :param kwargs:
        """
        try:
            record_deep_dir = os.path.dirname(record_path)
            if not os.path.exists(record_deep_dir):
                os.makedirs(record_deep_dir)

            if os.path.exists(record_path):
                os.remove(record_path)

            writer = pd.ExcelWriter(record_path)
            for key in kwargs.keys():
                sheet_name = key
                df_data = kwargs[key]
                df_data.to_excel(excel_writer=writer, sheet_name=sheet_name, index=False)
            writer.save()
            writer.close()
            print('save_excel:{0}'.format(record_path))
        except Exception as e:
            print(str(e))

    @staticmethod
    def append_excel(record_path, **kwargs):
        """
        保存Excel
        :param record_path:
        :param kwargs:
        """
        try:
            record_deep_dir = os.path.dirname(record_path)
            if not os.path.exists(record_deep_dir):
                os.makedirs(record_deep_dir)

            if os.path.exists(record_path):
                writer = pd.ExcelWriter(record_path, mode='a')
            else:
                writer = pd.ExcelWriter(record_path)

            for key in kwargs.keys():
                sheet_name = key
                df_data = kwargs[key]
                df_data.to_excel(excel_writer=writer, sheet_name=sheet_name, index=False)
            writer.save()
            writer.close()
            print('append_excel:{0}'.format(record_path))
        except Exception as e:
            print(str(e))

    @staticmethod
    def save_fig(record_path, df_data, x_column, y_columns):
        """
        保存图片
        :param record_path:保存图片路径
        :param df_data:保存的图片的数据
        :param x_column:X轴的列
        :param y_columns:Y轴的列合集
        :return:
        """
        try:
            x_date_key_list = ['datetime64[ns]']
            x_data = df_data[x_column]
            fig = plt.figure(figsize=(15, 8))
            ax = fig.add_subplot(1, 1, 1)

            if x_data.dtypes.name in x_date_key_list:
                N = len(x_data)
                ind = np.arange(N)  # the evenly spaced plot indices

                def format_date(x, pos=None):  # 保证下标不越界,很重要,越界会导致最终plot坐标轴label无显示
                    this_ind = np.clip(int(x + 0.5), 0, N - 1)
                    return df_data[x_column].iat[this_ind]

                for column in y_columns:
                    ax.plot(ind, df_data[column])
                ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
            else:
                for column in y_columns:
                    ax.plot(x_data, df_data[column])

            plt.legend()

            title_name = os.path.basename(record_path)
            plt.title(title_name)

            record_deep_dir = os.path.dirname(record_path)
            if not os.path.exists(record_deep_dir):
                os.makedirs(record_deep_dir)

            if os.path.exists(record_path):
                os.remove(record_path)

            plt.savefig(record_path)
            plt.close(fig)
            print('save_fig:{0}'.format(record_path))
        except Exception as e:
            print(str(e))

    @staticmethod
    def save_twins_fig(record_path, df_data, x_column, main_y_column, secondary_y_column):
        """
        双Y轴绘图保存
        :param record_path:
        :param df_data:
        :param x_column:
        :param main_y_column:
        :param secondary_y_column:
        :return:
        """
        try:
            x_date_key_list = ['datetime64[ns]']
            x_data = df_data[x_column]
            fig = plt.figure(figsize=(15, 8))
            ax = fig.add_subplot(1, 1, 1)

            if x_data.dtypes.name in x_date_key_list:
                N = len(x_data)
                ind = np.arange(N)  # the evenly spaced plot indices

                def format_date(x, pos=None):  # 保证下标不越界,很重要,越界会导致最终plot坐标轴label无显示
                    this_ind = np.clip(int(x + 0.5), 0, N - 1)
                    return df_data[x_column].iat[this_ind]

                ax.plot(ind, df_data[main_y_column])
                ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
                ax2 = ax.twinx()  # 用次y轴画图
                ax2.plot(ind, df_data[secondary_y_column])
            else:
                ax.plot(x_data, df_data[main_y_column])
                ax2 = ax.twinx()  # 用次y轴画图
                ax2.plot(x_data, df_data[secondary_y_column])

            plt.legend()

            title_name = os.path.basename(record_path)
            plt.title(title_name)

            record_deep_dir = os.path.dirname(record_path)
            if not os.path.exists(record_deep_dir):
                os.makedirs(record_deep_dir)

            if os.path.exists(record_path):
                os.remove(record_path)

            plt.savefig(record_path)
            plt.close(fig)
            print('save_fig:{0}'.format(record_path))
        except Exception as e:
            print(str(e))

    @staticmethod
    def save_txt(record_path, msg):
        """
        保存txt
        :param record_path:
        :param msg:
        """
        record_deep_dir = os.path.dirname(record_path)
        if not os.path.exists(record_deep_dir):
            os.makedirs(record_deep_dir)

        if os.path.exists(record_path):
            os.remove(record_path)

        with open(record_path, 'w+') as f:
            f.write(msg)

    @staticmethod
    def recursion_copy(root_path, destination_path, include_dir=None, exclude_dir=None, suffix=None):
        """
        获取py文件的路径
        :param suffix:
        :param include_dir:
        :param include_dir:
        :param root_path: 根路径
        :param destination_path: 目标路径
        :param exclude_dir: 排除文件（当前文件不是目标文件）
        :return: py文件的迭代器
        """
        # 返回所有文件夹绝对路径
        try:
            if exclude_dir is None:
                exclude_dir = []
            # 返回指定的文件夹包含的文件或文件夹的名字的列表
            for file_name in os.listdir(root_path):
                if 'MANIFEST.in' in file_name:
                    continue
                file_path = os.path.join(root_path, file_name)
                if os.path.isdir(file_path) and file_name not in exclude_dir:
                    if include_dir is not None and file_name in include_dir:
                        # 循环遍历文件夹
                        if not os.path.exists(os.path.join(destination_path, file_name)):
                            os.makedirs(os.path.join(destination_path, file_name))
                        FileToolBox.recursion_copy(os.path.join(root_path, file_name), os.path.join(destination_path, file_name), include_dir, exclude_dir, suffix)
                elif os.path.isfile(file_path):
                    # 文件不是排除文件  且不是'.pyc' '.pyx'文件
                    if suffix is not None and os.path.splitext(file_name)[1] in suffix:
                        shutil.copy(os.path.join(root_path, file_name), os.path.join(destination_path, file_name))
                    else:
                        shutil.copy(os.path.join(root_path, file_name), os.path.join(destination_path, file_name))
                else:
                    pass
        except Exception as e:
            print(str(e))

    @staticmethod
    def zip_dir(dir_path, zip_path):
        zip_file = zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED)
        print('[{0}]:压缩:{1}'.format(threading.currentThread().ident, dir_path))
        for root, dir_names, file_names in os.walk(dir_path):
            file_path = root.replace(dir_path, '')  # 去掉根路径，只对目标文件夹下的文件及文件夹进行压缩
            # 循环出一个个文件名
            for file_name in file_names:
                zip_file.write(os.path.join(root, file_name), os.path.join(file_path, file_name))
        zip_file.close()

    @staticmethod
    def unzip_file(dir_path, unzip_file_path):
        # 找到压缩文件夹
        dir_list = glob.glob(dir_path)
        if dir_list:
            # 循环zip文件夹
            for dir_zip in dir_list:
                # 以读的方式打开
                with zipfile.ZipFile(dir_zip, 'r') as f:
                    for file in f.namelist():
                        f.extract(file, path=unzip_file_path)
                os.remove(dir_zip)
# lst_data = [[datetime.datetime(2019, 1, 1), '1', '2', '3'],
#             [datetime.datetime(2019, 1, 2), '2', '3', '4'],
#             [datetime.datetime(2019, 1, 3), '3', '4', '4'],
#             [datetime.datetime(2019, 1, 4), '4', '3', '4'],
#             [datetime.datetime(2019, 1, 5), '5', '5', '2'],
#             [datetime.datetime(2019, 1, 6), '6', '2', '2'],
#             [datetime.datetime(2019, 1, 7), '7', '8', '2'],
#             [datetime.datetime(2019, 1, 8), '8', '9', '5'],
#             [datetime.datetime(2019, 1, 9), '9', '4', '5'],
#             [datetime.datetime(2019, 1, 10), '10', '2', '4'],
#             [datetime.datetime(2019, 1, 11), '11', '8', '7'],
#             [datetime.datetime(2019, 1, 12), '12', '2', '7'],
#             [datetime.datetime(2019, 1, 13), '13', '1', '7'],
#             [datetime.datetime(2019, 1, 14), '14', '0', '4'],]
# df_data = pd.DataFrame(lst_data, columns=['date', 'value1', 'value2', 'value3'])
# record_path = 'D:/a.png'
# FileToolBox.save_fig(record_path, df_data, 'value1', ['value2', 'value3'])
