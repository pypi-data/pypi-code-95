import os
import pickle
import time
import copy

import numpy as np
import pandas as pd

from .data_struc_kit import sum_list


def file_prefix_time(with_dash=False):
    curr_time = time.strftime('%Y%m%d', time.localtime())
    prefix = curr_time + '-' if with_dash else curr_time
    return prefix


def pd_read_csv_skip_row(file, comment=None, **kwargs):
    if os.stat(file).st_size == 0:
        raise ValueError("File is empty")
    with open(file, 'r') as f:
        pos = 0
        cur_line = f.readline()
        while cur_line.startswith(comment):
            pos = f.tell()
            cur_line = f.readline()
            f.seek(pos)
    return pd.read_csv(f, **kwargs)


def read_one_col_file(file, skiprows=None):
    with open(file, 'r') as f:
        one_col_list = [row.strip('\n') for row in f.readlines()]
        one_col_list = one_col_list[skiprows:] if skiprows is not None else one_col_list
        while '' in one_col_list:
            one_col_list.remove('')
    return one_col_list


def flatten_two_headers_file(file, header_num=2, sep=',', method=None):
    """

    method: stack headers or cross-insert or lower-first

    Headle file with two headers like

    Peptide_Order	Peptide	Peptide_Mass	Modifications	Proteins
        Spectrum_Order	Title	Charge	Precursor_Mass
    1	AAAAAAAAAAAAAAAAAA	2000	Carbamidomethyl[C](9)	PAK
        1	T1	3	1999
        2	T2	3	1999
        3	T3	3	1999
        4	T1	3	1999
        5	T5	3	1999
    2	CCCCCCCCCCCCCCC	3000	Carbamidomethyl[C](15)	PBK
        1	T2	3	2999
    3	DDDDDDDDDDDDDDDD	4000	null	PCK
        1	T3	3	3999
        2	T1	3	3999
        3	T2	3	3999

    """
    if isinstance(file, str):
        if len(file) < 300 and os.path.exists(file):
            with open(file, 'r') as f:
                file = f.readlines()
        else:
            file = file.split('\n')

    headers = [file[i].rstrip(f'\n{sep}').split(sep) for i in range(header_num)]
    headers_used_col_idx = [[idx for idx, value in enumerate(header) if value != ''] for header in headers]
    headers_used_col_num = [len(idx) for idx in headers_used_col_idx]

    if method is None or method == 'stack':
        flatten_text_used_col_idx = []
        for idx, num in enumerate([0, *headers_used_col_num][:-1]):
            flatten_text_used_col_idx.append(np.arange(num, num + headers_used_col_num[idx]))
    elif method == 'cross-insert':
        flatten_text_used_col_idx = []
    elif method == 'lower-first':
        flatten_text_used_col_idx = []
    else:
        raise

    flatten_header = sum_list([[value for value in header if value != ''] for header in headers])
    flatten_col_num = len(flatten_header)
    flatten_text = []

    header_level = 1
    consensus_text = ['' for i in range(flatten_col_num)]
    for row in file[header_num:]:
        row = row.rstrip(f'\n{sep}').split(sep)
        for idx, value in enumerate(row, 1):
            if value != '':
                header_level = idx
                break
        if header_level == 1:
            consensus_text = ['' for i in range(flatten_col_num)]

        for value_idx, raw_idx in enumerate(headers_used_col_idx[header_level - 1]):
            consensus_text[flatten_text_used_col_idx[header_level - 1][value_idx]] = row[raw_idx]

        if header_level == header_num:
            flatten_text.append(consensus_text.copy())

    return pd.DataFrame(flatten_text, columns=flatten_header)


def process_list_or_file(x):
    if isinstance(x, list) or isinstance(x, set):
        target_list = x
    else:
        if os.path.isfile(x):
            target_list = read_one_col_file(x)
        else:
            raise
    return target_list


def print_basename_in_dict(path_dict):
    for name, path in path_dict.items():
        print(f'{name}: {os.path.basename(path)}')


def check_path(path):
    print(f'{os.path.exists(path)} - {os.path.basename(path)}')


def check_path_in_dict(path_dict: dict, shown_filename_right_idx: int = 1):
    # TODO 显示的文件名称可以是多个 idx 对应 substring 的组合
    """
    :param path_dict:
    :param shown_filename_right_idx: None or int. None: use full path (raw value in dict). int: use idx part of file path (right count with 1st-first idx)
    """
    print(f'Total {len(path_dict)} files')
    for name, path in path_dict.items():
        if shown_filename_right_idx is None:
            shown_filename = path
        elif isinstance(shown_filename_right_idx, int) and shown_filename_right_idx > 0:
            used_path = path
            for _ in range(shown_filename_right_idx):
                used_path = os.path.dirname(used_path)
            shown_filename = os.path.basename(used_path)
        else:
            raise ValueError(f'Param `shown_filename_right_idx` must be None or any positive integer. Now {shown_filename_right_idx}')
        print(f'{os.path.exists(path)} - {name}: {os.path.basename(shown_filename)}')


def check_input_df(data, *args) -> pd.DataFrame:
    if isinstance(data, pd.DataFrame):
        df = data
    else:
        if os.path.exists(data):
            df = pd.read_csv(data, *args)
        else:
            raise FileNotFoundError
    return df


def fill_path_dict(path_to_fill: str, fill_string: dict, exist_path_dict: dict = None):
    if exist_path_dict is None:
        path_dict = dict()
    else:
        path_dict = exist_path_dict.copy()

    for k, file_name in fill_string.items():
        file_name = [file_name] if isinstance(file_name, str) else file_name
        path_dict[k] = path_to_fill.format(*file_name)
    return path_dict


def join_path(path, *paths, create=False):
    pass


def write_inten_to_json(prec_inten: dict, file_path):
    total_prec = len(prec_inten)
    with open(file_path, 'w') as f:
        f.write('{\n')

        for prec_idx, (prec, inten_dict) in enumerate(prec_inten.items(), 1):
            f.write('    "%s": {\n' % prec)
            frag_num = len(inten_dict)
            for frag_idx, (frag, i) in enumerate(inten_dict.items(), 1):
                if frag_idx != frag_num:
                    f.write(f'        "{frag}": {i},\n')
                else:
                    f.write(f'        "{frag}": {i}\n')

            if prec_idx != total_prec:
                f.write('    },\n')
            else:
                f.write('    }\n')

        f.write('}')


def data_dump_load_skip(file_path, data=None, cover_data=False, update_file=False):
    if not os.path.exists(file_path):
        if data is not None:  # Here use 'is not None' because some thing will be wrong when the data is a pd.DataFrame. (Truth value is ambiguous error)
            with open(file_path, 'wb') as f:
                pickle.dump(data, f)
        else:
            raise FileNotFoundError('No existing file and no input data')
    else:
        if data is not None:
            if update_file:
                with open(file_path, 'wb') as f:
                    pickle.dump(data, f)
            elif cover_data:
                with open(file_path, 'rb') as f:
                    data = pickle.load(f)
            else:
                pass
        else:
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
    return data
