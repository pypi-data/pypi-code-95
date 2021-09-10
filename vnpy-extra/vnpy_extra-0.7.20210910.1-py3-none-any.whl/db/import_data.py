#! /usr/bin/env python3
"""
@author  : MG
@Time    : 2021/1/26 下午10:13
@File    : import_data.py
@contact : mmmaaaggg@163.com
@desc    : 用于将办公室与家里的数据通过邮件方式进行同步
"""
import logging
import os
import tarfile
from datetime import date
from io import BytesIO, StringIO
from typing import Iterator

import pandas as pd
from peewee import IntegrityError

from vnpy_extra.db.orm import database
from vnpy_extra.utils.get_email import download_email_attachment

logger = logging.getLogger(__name__)


@database.atomic()
def import_data_2_tables(email_title, password, ignore_error=True):
    attachment_dic = download_email_attachment(email_title, password=password)

    tio = BytesIO()
    keys = sorted(attachment_dic.keys())
    if len(keys) == 0:
        logger.warning("%s 没有附件", email_title)
        return

    for key in keys:
        tio.write(attachment_dic[key].read())
    tio.seek(0)
    tar = tarfile.open(fileobj=tio)
    # use "tar" as a regular TarFile object
    dir_name = f'data/{date.today()}'
    os.makedirs(dir_name, exist_ok=True)
    tar.extractall(path=dir_name)
    data_len = len(os.listdir(dir_name))
    num = 0
    for file_name in os.listdir(dir_name):
        error_count = 0
        table_name = file_name.split('.')[0]
        num = num + 1
        table_path = os.path.join(dir_name, file_name)  # 将路径与文件名结合起来就是每个文件的完整路径
        df = pd.read_csv(table_path)
        fields = list(df.columns)
        fields_str = "`" + "`,`".join(fields) + "`"
        values_str = ",".join(["%s" for _ in fields])
        update_str = ",".join([f"{_}=%s" for _ in fields])
        sql_str = f"insert into {table_name} ({fields_str}) values({values_str}) " \
                  f"on duplicate key update {update_str}"
        for row in df.to_dict(orient='record'):
            if 'id_name' in fields and pd.isna(row['id_name']):
                # some dirty data has to be clean
                continue
            param = [None if pd.isna(row[_]) else row[_] for _ in fields]
            param.extend([None if pd.isna(row[_]) else row[_] for _ in fields])
            try:
                database.execute_sql(sql_str, params=param)
            except IntegrityError as exp:
                if ignore_error:
                    error_count += 1
                else:
                    raise exp from exp

        logger.info("%d/%d) %s 同步完成 %d 条数据。%s",
                    num, data_len, table_name, df.shape[0],
                    "" if error_count == 0 else f"{error_count} 条记录冲突"
                    )


def csv_split_chunk(file_name, csv_split_chunk_size=1024 * 1024 * 8) -> Iterator[StringIO]:
    """按照尺寸将csv文件切割成为N组字符流"""
    with open(file_name) as f:
        first_line = f.readline()
        line = f.readline()
        stream = None
        while line != "":
            # 初始化 steam
            if stream is None:
                stream = StringIO()
                stream.writelines([first_line, line])
                cur_size = len(first_line) + len(line)
            else:
                # 填充数据到 steam
                stream.write(line)

            cur_size += len(line)
            if cur_size >= csv_split_chunk_size:
                # 返回 steam
                stream.seek(0)
                yield stream
                stream = None

            line = f.readline()

        if stream is not None:
            stream.seek(0)
            yield stream


@database.atomic()
def csv_2_tables(dir_path, ignore_error=True, csv_split_chunk_size=1024 * 1024 * 8):
    file_name_list = os.listdir(dir_path)
    data_len = len(file_name_list)
    for num, file_name in enumerate(file_name_list, start=1):
        error_count = 0
        table_name, ext = os.path.splitext(file_name)
        if ext != '.csv':
            continue
        data_count = 0
        for stream in csv_split_chunk(os.path.join(dir_path, file_name), csv_split_chunk_size):
            df = pd.read_csv(stream)
            data_count += df.shape[0]
            fields = list(df.columns)
            fields_str = "`" + "`,`".join(fields) + "`"
            values_str = ",".join(["%s" for _ in fields])
            update_str = ",".join([f"{_}=%s" for _ in fields])
            sql_str = f"insert into {table_name} ({fields_str}) values({values_str}) " \
                      f"on duplicate key update {update_str}"
            for row in df.to_dict(orient='record'):
                if 'id_name' in fields and pd.isna(row['id_name']):
                    # some dirty data has to be clean
                    continue
                param = [None if pd.isna(row[_]) else row[_] for _ in fields]
                param.extend([None if pd.isna(row[_]) else row[_] for _ in fields])
                try:
                    database.execute_sql(sql_str, params=param)
                except IntegrityError as exp:
                    if ignore_error:
                        error_count += 1
                    else:
                        raise exp from exp

        logger.info("%d/%d) %s 同步完成 %d 条数据。%s",
                    num, data_len, table_name, data_count,
                    "" if error_count == 0 else f"{error_count} 条记录冲突"
                    )


if __name__ == "__main__":
    # import_data_2_tables('exports 2021-02-26', '****')
    csv_2_tables(r'C:\Users\zerenhe-lqb\Downloads\tt')
