"""
@author  : MG
@Time    : 2021/6/9 9:02
@File    : generate_md.py
@contact : mmmaaaggg@163.com
@desc    : 用于自动生成 MD 文件中的内容
"""
import logging
import os

import numpy as np
import pandas as pd
from vnpy_extra.utils.symbol import get_instrument_type_and_exchange


def generate_md_by_xls_files(dir_path: str, output_file_name=None):
    """根据xlsx文件的内容，生成MD文件中的表格及图片"""
    if output_file_name is None:
        output_file_name = dir_path.split(os.sep)[-2]
    if os.path.splitext(output_file_name)[1].lower() != '.md':
        output_file_name = f'{output_file_name}.md'
    os.makedirs('output', exist_ok=True)
    output_file = os.path.join('output', output_file_name)
    md_table_last_column = '收益损失比'
    with open(output_file, mode='w', encoding='utf-8') as f:
        for num, file_name in enumerate(os.listdir(dir_path), start=1):
            _, ext = os.path.splitext(file_name)

            for _ in file_name.split('_')[1:]:
                instrument_type, _ = get_instrument_type_and_exchange(_)
                if instrument_type is not None:
                    break

            if instrument_type is None:
                instrument_type = file_name

            # 写文件头
            f.write(f'#### {num}) {instrument_type}\n\n')

            # 读取文件
            if ext.lower() == '.csv':
                df = pd.read_csv(os.path.join(dir_path, file_name))
            else:
                df = pd.read_excel(os.path.join(dir_path, file_name))
            # 数据整理
            df['收益损失比'] = np.round(df['收益损失比'], 2)
            # 从第一列到 ‘收益损失比’ 全部列出来
            md_table_columns = []
            for _ in df.columns:
                if _.strip() == '' or _.startswith('Unnamed:') or _.startswith('列'):
                    continue
                md_table_columns.append(_)
                if _ == md_table_last_column:
                    break

            df = df[df['backtest_status'] > 0]
            df[md_table_columns].to_markdown(f, index=False)

            lines = [f'{url}\n' for _, url in df['图片地址'].items()]
            lines.insert(0, '\n\n')
            lines.append('\n')
            f.writelines(lines)

    logging.info("output file name: %s", output_file_name)


def _run_generate_md_by_xls_files():
    dir_path = r'd:\github\quant_vnpy\strategies\trandition\period_resonance\pr_2021_04_02_two_signals\reports\MacpKdjPr20210402And\output\available'
    generate_md_by_xls_files(dir_path)


if __name__ == "__main__":
    _run_generate_md_by_xls_files()
