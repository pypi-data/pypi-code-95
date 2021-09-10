import time
from pathlib import Path
from .common import get_files, read_title
from .filetransform import excel_to_csv, _excel_trans_sheet_engine, _csv_trans_excel_engine
import pandas as pd


def _normal_union_engine(save_path, files, **kwargs):
    save_path = save_path / f'UnionResult{time.strftime("%Y%m%d%H%M%S", time.localtime())}.csv'
    title = False
    chunksize = 10 * 1024 * 1024  # 每次读取10m
    header = kwargs.get('header', False)
    if header is None:
        header = False
    elif header is True:
        header = 0
    skiprows = kwargs.get('skiprows', 0)
    print('{:-^70}'.format(f'正在合并文件，共需合并{len(files)}个文件'))
    with open(save_path, mode='w', encoding=kwargs.get('encoding', 'gbk')) as fobj:
        if len(files) > 1:
            for index, file in enumerate(files):
                with open(file, mode='r', encoding=kwargs.get('encoding', 'gbk')) as subobj:
                    for i in range(skiprows):
                        subobj.readline()
                    if not header is False:
                        for _ in range(header):
                            subobj.readline()
                        if not title:
                            title = True
                            fobj.write(subobj.readline())
                        else:
                            subobj.readline()
                    while True:
                        chunk = subobj.read(chunksize)
                        if not chunk:
                            break
                        else:
                            fobj.write(chunk)
                print(f'>>>已合并第{index + 1}/{len(files)}个文件:{file}...')
    return save_path


def _pandas_union_engine(save_path, files, **kwargs):
    save_path = save_path / f'UnionResult_{time.strftime("%Y%m%d%H%M%S", time.localtime())}.csv'
    print('{:-^70}'.format(f'正在合并文件，共需合并{len(files)}个文件'))
    title = []
    if not kwargs.get('header') is None:
        for file in files:
            _title = read_title(file, **kwargs)
            title += [t for t in _title if t not in title]
        base = pd.DataFrame(columns=title)
    else:
        base = pd.DataFrame()
    for index, file in enumerate(files):
        tbs = pd.read_csv(file, chunksize=10000, keep_default_na=False, low_memory=False, **kwargs)
        for tb in tbs:
            _tb = pd.concat([base, tb])
            _tb.to_csv(save_path, index=False, encoding='gbk', header=not save_path.exists(), mode='a')
        print(f'>>>已合并第{index + 1}/{len(files)}个文件:{file}...')
    return save_path


def union_in_path_to_csv(save_path, file_path, file_type, engine='normal', skiprows=0,
                         header=None, encoding='gbk', include_subdir=False, **kwargs):
    save_path, file_path = Path(save_path), Path(file_path)
    if not file_path.exists():
        raise ValueError('文件路径不存在')
    file_list = get_files(file_path, file_type, include_subdir)
    return union_in_list_to_csv(save_path, file_list, engine=engine, skiprows=skiprows,
                                header=header, encoding=encoding, **kwargs)


def union_in_list_to_csv(save_path, file_list, engine='normal', skiprows=0,
                         header=0, encoding='gbk', **kwargs):
    if not save_path.exists():
        raise ValueError('保存路径不存在')
    need_trans_list_before = list(filter(lambda f: '.xls' in f.suffix, file_list))
    no_need_trans_list = [x for x in file_list if x not in need_trans_list_before]
    need_trans_list_after = []
    engine = _pandas_union_engine if engine == 'pandas' else _normal_union_engine
    kwargs.update(
        skiprows=skiprows,
        header=header,
        encoding=encoding
    )
    for file in need_trans_list_before:
        file = Path(file)
        need_trans_list_after += excel_to_csv(file.parent, file, kwargs.get('encoding', 'gbk'))
    need_union_file = need_trans_list_after + no_need_trans_list
    result = engine(save_path, need_union_file, **kwargs)
    [f.unlink() for f in need_trans_list_after]
    return result


def union_in_list_to_sheets(save_path, file_list, encoding='gbk', skiprows=0):
    for file in file_list:
        if '.xls' in file.__str__():
            print('_excel_trans_sheet_engine')
            print(file)
            _excel_trans_sheet_engine(save_path, file, skiprows)
        else:
            _csv_trans_excel_engine(save_path, file, encoding, skiprows)


def union_in_path_to_sheets(save_path, file_path, file_type, skiprows=0, encoding='gbk', include_subdir=False):
    save_path, file_path = Path(save_path), Path(file_path)
    if not file_path.exists():
        raise ValueError('文件路径不存在')
    file_list = get_files(file_path, file_type, include_subdir)
    union_in_list_to_sheets(save_path, file_list, encoding, skiprows)
