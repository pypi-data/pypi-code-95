from typing import List
from UniversalParser._tools import patt_template_replace
from .templates import *

def parse_html_table(
        datas: List[List[List[str]]]
        , title: str = 'Table'
        , caption: str = ''
        , tfoot: str = ''
    ) -> str:

    tables = ''

    for rows in datas:

        tr_ths = rows[0]
        tr_tds = rows[1:]

        insert_tr_ths = ''
        insert_tr_tds = ''

        t_str = '<tr>'
        for th in tr_ths:
            t_str += f'<th>{th}</th>'
        t_str += '</tr>'
        insert_tr_ths += t_str

        for tr_td in tr_tds:
            t_str = '<tr>'
            for td in tr_td:
                t_str += f'<td>{td}</td>'
            t_str += '</tr>'
            insert_tr_tds += t_str

        tables += patt_template_replace(
            TABLE
            , tr_ths = insert_tr_ths
            , tr_tds = insert_tr_tds
        )
    
    return patt_template_replace(
        HTML
        , title = title
        , tables = tables
    )
