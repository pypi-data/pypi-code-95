#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : nesc.
# @File         : extract4ddl
# @Time         : 2021/9/6 下午12:28
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  :

from meutils.pipe import *
from meutils.decorators.catch import wecom_catch, wecom_hook


@wecom_catch()
def sheet2df(df, sheet=''):
    df = df.dropna(how='all').dropna(1, how='all')

    dfs = []
    col_map = {}

    for r in df.fillna(method='ffill').itertuples():
        if r._1 == '对象号':
            if col_map:
                dfs.append(
                    pd.DataFrame(col_map))  # {'对象号': '530500', '表名': 'v_his_businesstotal', '所在数据库': 'V8.11.2.0'}
                col_map = {}

            col_map.setdefault('对象号', r._2)

        if r._1 == '表名':
            col_map.setdefault('表名', r._2)

            if r._5 == '所在数据库':
                col_map.setdefault('所在数据库', r._6)

        if r._1 == '中文名':
            col_map.setdefault('中文名', r._2)

        if r._1 == '字段' and r._2 != '字段名':
            col_map.setdefault('字段名', []).append(r._2)
            col_map.setdefault('字段类型', []).append(r._3)
            col_map.setdefault('字段说明', []).append(r._5)

        if r._2.strip().startswith('idx_'):
            col_map['索引名称'] = col_map.get('索引名称', '') + ' ' + r._2
            col_map['索引字段'] = col_map.get('索引字段', '') + ' ' + r._5

    dfs.append(pd.DataFrame(col_map))
    df = pd.concat(dfs, ignore_index=True)
    df.insert(0, '表结构名', sheet)

    logger.info(f"{sheet}: {len(dfs)}个表")
    return df


def main(ipath, opath=None):
    p = Path(ipath)
    if opath is None:
        opath = p.parent / f"{p.name}.tsv"

    df_map = pd.read_excel(
        p,
        header=0,
        sheet_name=None,
    )

    logger.debug(f"文件名: {p.name} 有{len(df_map)}个sheet")

    sheet_list = []
    for sheet, df in tqdm(df_map.items()):
        sheet = sheet.strip()
        if sheet in ('数据库目录', '模块信息'):
            continue

        sheet_df = sheet2df(df, sheet)
        if sheet_df is None:
            logger.error(f"{p.name}__{sheet}解析错误！！！")
        else:
            sheet_list.append(sheet_df)

    df_all = pd.concat(sheet_list, ignore_index=True)

    df_all.insert(0, '文件名', p.name)

    df_all.to_csv(opath, '\t', index=False)

    logger.info(f"结果文件: {opath}")

    logger.info(bjson(dict(zip(df_all.nunique().index, df_all.nunique()))))


if __name__ == '__main__':
    main("/Users/yuanjie/Downloads/UF20表结构/UF20表结构/UF20表信息.xls")
