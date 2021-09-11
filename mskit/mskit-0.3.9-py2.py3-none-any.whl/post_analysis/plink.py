import os
import re
from collections import defaultdict
from os.path import join as join_path

import pandas as pd

from mskit import rapid_kit as rk


def collect_plink_results(data_dir):
    used_linkers = os.listdir(data_dir)
    used_linkers = [_ for _ in used_linkers if os.path.isdir(join_path(data_dir, _))]
    plink_results = {'Cross': defaultdict(list), 'Loop': defaultdict(list), 'Mono': defaultdict(list)}
    for linker in used_linkers:
        linker_dir = join_path(data_dir, linker)
        for rep_name in os.listdir(linker_dir):
            rep_dir = join_path(linker_dir, rep_name)
            for file_name in os.listdir(rep_dir):
                file_path = join_path(rep_dir, file_name)
                df = rk.flatten_two_headers_file(file_path, sep=',')
                if df.size == 0:
                    continue
                df['Linker'] = linker
                df['Source'] = f'{linker}/{rep_name}/{file_name}'
                if 'cross-linked' in file_name:
                    df['LinkType'] = 'CrossLink'
                    plink_results['Cross'][linker].append(df.copy())
                elif 'loop-linked' in file_name:
                    df['LinkType'] = 'LoopLink'
                    df['Protein_Type'] = 'Intra-Protein'
                    plink_results['Loop'][linker].append(df.copy())
                elif 'mono-linked' in file_name:
                    df['LinkType'] = 'MonoLink'
                    plink_results['Mono'][linker].append(df.copy())
                else:
                    raise
    for link_type in list(plink_results.keys()):
        for linker in list(plink_results[link_type].keys()):
            plink_results[link_type][linker] = pd.concat(plink_results[link_type][linker]).reset_index().rename({'index': 'RawIndex'}, axis=1)
    return plink_results


def split_cross_link_info(x, prot_name_mapper):
    link_info = x['Proteins']

    re_match = re.match(r'(.+?)\((\d+)\)-(.+?)\((\d+)\).*', link_info)
    prot_site = [(re_match.group(1), int(re_match.group(2))),
                 (re_match.group(3), int(re_match.group(4)))]

    sorted_prot_site = sorted(prot_site, key=lambda _: _[1])
    sorted_link_info = '{}({})-{}({})'.format(prot_name_mapper[sorted_prot_site[0][0]], sorted_prot_site[0][1],
                                              prot_name_mapper[sorted_prot_site[1][0]], sorted_prot_site[1][1])

    pep = x['Peptide']
    if str(sorted_prot_site[0][1]) != re_match.group(2):
        pep = '-'.join(pep.split('-')[::-1])

    return (pep, *rk.sum_list(prot_site), sorted_link_info)


def process_cross_link_result(df, prot_name_mapper):
    # 非 gi| 的部分 proteins 均为单组位点
    df = df[~df['Proteins'].str.contains('gi|', regex=False)].copy()

    df[[
        'SortedPeptide',
        'Raw_Prot1',
        'Raw_Site1',
        'Raw_Prot2',
        'Raw_Site2',
        'SortedLinkInfo'
    ]] = df.apply(split_cross_link_info, args=(prot_name_mapper,), axis=1, result_type='expand')
    return df.copy()


def split_loop_link_info(x, prot_name_mapper):
    link_info = x['Proteins']

    re_match = re.match(r'(.*?)\((\d+)\)\((\d+)\).*', link_info)
    prot_site = [re_match.group(1), int(re_match.group(2)), int(re_match.group(3))]
    sorted_site = sorted(prot_site[1:])
    sorted_link_info = '{0}({1})-{0}({2})'.format(prot_name_mapper[prot_site[0]], sorted_site[0], sorted_site[1])

    pep = x['Peptide']
    re_match = re.match(r'(.+?)\((\d+)\)\((\d+)\).*', pep)
    pep = '{0}({1})-{0}({2})'.format(
        re_match.group(1),
        *sorted([int(re_match.group(2)), int(re_match.group(3))])
    )

    return (pep, *prot_site, sorted_link_info)


def process_loop_link_result(df, prot_name_mapper):
    df = df[~df['Proteins'].str.contains('gi|', regex=False)].copy()

    df[[
        'SortedPeptide',
        'Raw_Prot',
        'Raw_Site1',
        'Raw_Site2',
        'SortedLinkInfo'
    ]] = df.apply(split_loop_link_info, args=(prot_name_mapper,), axis=1, result_type='expand')
    return df.copy()
