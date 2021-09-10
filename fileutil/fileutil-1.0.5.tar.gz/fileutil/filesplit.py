import csv
import re
from math import ceil
from pathlib import Path
import numpy as np
import pandas as pd
from .common import replace_invalid_char, input_data
from . import common
from .filetransform import excel_to_csv


# pd.set_option('max_columns', 1000, 'max_rows', 100, 'expand_frame_repr', False)


def split_by_row(save_path, file_path, row_num, skiprows=0, header=False):
    save_path, file_path = Path(save_path), Path(file_path)
    istrans = False
    if '.xls' in file_path.suffix:
        file_path = excel_to_csv(save_path, file_path)
        istrans = True
    else:
        file_path = [file_path]
    result = []
    for file in file_path:
        result.extend(_split_by_row_engine(save_path, file, row_num, skiprows, header))
    if istrans:
        [f.unlink() for f in file_path]
    return result


def split_by_size(save_path, file_path, size, skiprows=0, header=0):
    save_path, file_path = Path(save_path), Path(file_path)
    istrans = False
    if '.xls' in file_path.suffix:
        file_path = excel_to_csv(file_path.parent, file_path)
        istrans = True
    else:
        file_path = [file_path]
    result = []
    for file in file_path:
        result.extend(_split_by_size_engine(save_path, file, size, skiprows, header))
    if istrans:
        [f.unlink() for f in file_path]
    return result


def split_by_column(save_path, file_path, split_column, encoding='gbk', **kwargs):
    save_path, file_path = Path(save_path), Path(file_path)
    istrans = False
    if '.xls' in file_path.suffix:
        file_path = excel_to_csv(file_path.parent, file_path)
        istrans = True
    else:
        file_path = [file_path]
    result = []
    for file in file_path:
        result.append(_split_by_column_engine(save_path, file, split_column, encoding, **kwargs))
    if istrans:
        [f.unlink() for f in file_path]
    return result


def mml_split_file(file_path, encoding='gbk'):
    '''
    对mml文件进行分割，主要考虑因素：
    1、如果是excel类型文件，则按照sheet转换为csv文件
    2、如果第一行不是表头，则需要跳过n行，直到表头出现
    3、mml脚本基站数量限制1000个以内
    4、mml脚本大小限制5M以内
    :param file_path: mml文件路径
    :return: None
    '''
    skiprows = input_data('int', f'mml文件跳过行数')
    site_num = input_data('int', f'mml文件基站数量')
    file_size = input_data('int', f'mml文件大小(mb)') * 1024 * 1024
    file_path = Path(file_path)
    keep_file = True  # 最后需要将excel转csv的文件删除
    if '.xls' in file_path.suffix:
        files = excel_to_csv(file_path.parent, file_path)  # 将excel转换成csv
        keep_file = False
    else:
        files = [file_path]
    result_file = []
    for file in files:
        fpath, fname = file.parent, file.stem
        title = common.read_title(file, skiprows)  # 读取title
        common.print_list_formating(title)  # 打印title
        split_key = input_data('str', '请依次输入[分组索引],[网元名称索引],[脚本索引]')  # 输入分割参数
        split_columns = __get_split_columns(split_key, title)  # 通过正则将分割参数转为list
        # groupby_column:需要分组的列，sitename_column：基站名称列，用于计算基站数量，mml_column：mml脚本列，用于输出mml脚本
        groupby_column, sitename_column, mml_column = split_columns
        print(f'>>>开始分割文件"{file}"')
        tb = pd.read_csv(file, encoding=encoding, skiprows=skiprows, error_bad_lines=False,
                         low_memory=False)
        grouper = tb.groupby(by=groupby_column, as_index=False, sort=False)  # 按照分组列分组
        print(f'>>>文件"{file}"按照"{"_".join(groupby_column)}"共可分割成{len(grouper)}组')
        for key, value in grouper:
            fid = 0
            save_name_tail = key if isinstance(key, str) else '_'.join(key)
            save_name_tail = replace_invalid_char(save_name_tail)
            sitename = value[sitename_column].drop_duplicates()  # 分组后读取基站名称，并去重
            sitename.reset_index(inplace=True, drop=True)  # 重设index，目的是后边按index分组cut
            bins = [x * site_num for x in range(ceil(len(sitename) / site_num) + 1)]  # 设置cut区间
            if len(bins) > 2:
                sitename['cut'] = pd.cut(sitename.index, bins, right=False)  # 填充cut区间列
                cut_value = sitename.groupby('cut', sort=False, as_index=False)  # 按照cut分组，取其中的sitename，series类型
                for k, names in cut_value:
                    fid += 1
                    save_path = fpath / f'{fname}_{save_name_tail}_{fid}.txt'
                    print(f'>>>生成文件:{save_path}...')
                    result_file.append(save_path)
                    names = names[sitename_column[0]]
                    _tb = value.loc[value[sitename_column[0]].isin(names)]  # 按照cut后sitename，在value中提取数据
                    for mml in mml_column:
                        c = _tb[mml].replace(r'^\s*$', value=np.nan, regex=True).dropna()  # 去除空白元素
                        c.to_csv(save_path, index=False, encoding='gbk', mode='a', header=False, sep='\n',
                                 quoting=csv.QUOTE_NONE)  # quoting=csv.QUOTE_NONE，不添加引号，sep='\n',换行符作为分隔符
            else:
                fid += 1
                save_path = fpath / f'{fname}_{save_name_tail}_{fid}.txt'
                print(f'>>>生成文件:{save_path}...')
                result_file.append(save_path)
                for mml in mml_column:
                    c = value[mml].replace(r'^\s*$', value=np.nan, regex=True).dropna()
                    c.to_csv(save_path, index=False, encoding='gbk', mode='a', header=False, sep='\n',
                             quoting=csv.QUOTE_NONE)  # quoting=csv.QUOTE_NONE，不添加引号，sep='\n',换行符作为分隔符
    for f in result_file:
        if f.stat().st_size > file_size:
            split_by_size(f.parent, f, file_size, keep_file=False)  # 将文件大小超过file_size的文件进行再次分割
    if not keep_file: [f.unlink() for f in files]


def __get_split_columns(split_key, title):
    para_list = []  # 记录将输入字符串转化成list，例如[[1,2],[3,4],[5,6]]
    sp = re.findall(r'\[(.+?)\]', split_key)  # 按照[]拆分成list
    for i in range(len(sp)):
        if '-' not in sp[i]:
            para_list.append(eval('[' + sp[i] + ']'))
        else:
            sp1 = sp[i].split(',')
            lst = []
            for _sp in sp1:
                if _sp.isdigit():
                    lst.append(int(_sp))
                elif '-' in _sp:
                    start, end = _sp.split('-')
                    lst += [x for x in range(int(start), int(end) + 1)]
            lst = list(set(lst))
            para_list.append(lst)

    result_column = []
    for p in para_list:
        result_column.append([title[i - 1] for i in p])
    return result_column


def _split_by_row_engine(save_path, file, row_num, skiprows=0, header=0):
    file = Path(file)
    stem, suffix = file.stem, file.suffix
    print('{:-^70}'.format(f'正在分割文件:{file.name}'))
    fid = 0
    mew_file_list = []
    with open(file, mode='rb') as fobj:
        for i in range(skiprows):
            fobj.readline()
        if not header is False:
            if header > 0:
                for _ in range(header):
                    fobj.readline()
            title = fobj.readline()
        while True:
            line = fobj.readline()
            if not line: break
            fid += 1
            _save_path = Path(save_path) / f'{stem}_{fid}{suffix}'
            sub_obj = open(_save_path, mode='wb')
            if not header is False: sub_obj.write(title)
            sub_obj.write(line)
            for i in range(row_num - 1):
                line = fobj.readline()
                if not line:
                    break
                sub_obj.write(line)
            sub_obj.close()
            mew_file_list.append(_save_path)
            print(f'>>>生成文件:{_save_path}')
    return mew_file_list


def _split_by_size_engine(save_path, file, split_size, skiprows=0, header=0):
    stem, suffix = file.stem, file.suffix
    chunksize = 10 * 1024 * 1024  # 每次读取10mb
    fsize = file.stat().st_size  # 文件总大小
    split_size = int(split_size)
    currentsize = 0  # 当前已读取的大小
    new_file_list = []
    fid = 1
    print('{:-^70}'.format(f'文件转换:将{file}转换为csv格式'))
    with open(file, mode='rb') as fobj:
        if skiprows:
            for i in range(0, skiprows):
                currentsize += len(fobj.readline())
        if not header is False:
            if header > 0:
                for _ in range(header):
                    currentsize += len(fobj.readline())
            title = fobj.readline()
            currentsize += len(title)
        fsize -= currentsize
        chunknum = ceil(split_size / chunksize)  # 计算每个文件需要chunk次数
        havechunk = 0
        while havechunk < fsize:
            _save_path = save_path / f'{stem}_{fid}{suffix}'
            with open(_save_path, mode='wb') as subobj:
                if not header is False: subobj.write(title)
                for j in range(chunknum):
                    if chunknum < chunknum - 1:
                        subobj.write(fobj.read(chunksize))
                        havechunk += chunksize
                    else:
                        _chunksize = split_size - chunksize * j
                        subobj.write(fobj.read(_chunksize))
                        havechunk += _chunksize
                endline = fobj.readline()
                subobj.write(endline)
                havechunk += len(endline)
                fid += 1
            print(_save_path)
            new_file_list.append(_save_path)
    return new_file_list


def _split_by_column_engine(save_path, file, split_column, encoding, **kwargs):
    stem, suffix = file.stem, file.suffix
    tbs = pd.read_csv(file, encoding=encoding, chunksize=100000, keep_default_na=False, low_memory=False, **kwargs)
    print('{:-^70}'.format(f'文件分割:将{file}按照{",".join(split_column)}'))
    new_file_list = []
    for tb in tbs:
        group = tb.groupby(split_column)
        for index, value in group:
            savename_tail = str(index) if len(split_column) == 1 else '_'.join(
                [str(x) for x in index])
            savename_tail = replace_invalid_char(savename_tail)
            _save_path = save_path / f'{stem}_{savename_tail}{suffix}'

            header = not _save_path.exists()
            if header: print(f'>>>生成文件：{_save_path}')
            value.to_csv(_save_path, index=False, encoding=encoding, mode='a', header=header)
            new_file_list.append(_save_path)
    return list(set(new_file_list))
