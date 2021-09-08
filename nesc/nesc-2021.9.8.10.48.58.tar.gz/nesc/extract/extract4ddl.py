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


def extract_data(p, encoding='utf-8', start_func=lambda x: x.startswith('create table'),
                 end_func=lambda x: x.startswith('tablespace')):
    flag = False
    data_map = {}
    with open(p, encoding=encoding) as f:
        for r in tqdm(f):
            if flag:  # 左开右闭
                data_map.setdefault(table, []).append(r.strip())

            if start_func(r):
                table = r.strip().split()[-1]
                flag = True

            if end_func(r):
                flag = False
    return data_map


def main(ipath, opath=None, encoding='GB18030'):
    p = Path(ipath)
    if opath is None:
        opath = p.parent / f"{p.name}.tsv"

    logger.info(f"输入路径: {p}")
    logger.info(f"输出路径: {opath}")

    d = extract_data(p, encoding)
    dd = {i: j[1:-2] for i, j in d.items()}

    df = pd.DataFrame(dd.items(), columns=['表名', '字段名'])
    df = df.explode('字段名', True)

    df.to_parquet(p.parent / 'ddl解析中间文件.parquet')

    # 解析过程
    s = df['字段名'].str.strip().str.strip(',').str.strip('not null').str.strip()
    df['字段名'] = s.str.split().str[0]
    df['数据类型'] = s.str.split('(').str[0].str.split().str[1]
    df['数据长度'] = s.str.split('(').str[1].str.split(')').str[0]
    df['字段说明'] = s.str.split('-+').str[1]  # .str.strip()

    df.to_csv(opath, '\t', index=False)

    logger.info(bjson(dict(zip(df.nunique().index, df.nunique()))))


if __name__ == '__main__':
    main('/Users/yuanjie/Desktop/mot_.sql')
