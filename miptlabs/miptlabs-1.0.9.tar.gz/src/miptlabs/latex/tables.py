from pandas import DataFrame


def gen_from_dataframe(df: DataFrame, caption=None, header=None, index=False):
    """
    Генерирует таблицу из DataFame
    :param df: dataframe из pandas
    :param caption: название таблицы
    :param header: заголовок таблицы, располагается сверху всех строк и размером со все столбцы
    :param index: нужна ли индексация
    :return:
    """
    col_count = len(df.columns)

    cols = ''.join(['c|' for i in range(col_count)])

    # -------------begin-------------
    index_col = ''
    if index:
        index_col = 'c|'

    header_col = ''
    if header:
        header_col = f'\t\t\t\\hline\n' \
                     f'\t\t\t\\multicolumn{{{col_count}}}{{|c|}}{{{header}}}\\\\'

    table_begin = f'\\begin{{table}}[H]\n\t\\begin{{center}}\n' \
                  f'\t\t\\begin{{tabular}}{{|{index_col}{cols}}}\n' \
                  f'{header_col}\n' \
                  f'\t\t\t\\hline\n'

    # -------------body-------------
    body = ' & '.join(df.columns) + '\\\\\n\t\t\t\\hline\n'

    if index:
        body = '\t\t\tN & ' + body
    else:
        body = '\t\t\t' + body

    if index:
        for num, i in enumerate(df.values):
            body += f'\t\t\t{num} & ' + ' & '.join([str(elem) for elem in i]) + '\\\\\n\t\t\t\\hline\n'

    else:
        for num, i in enumerate(df.values):
            body += '\t\t\t' + ' & '.join([str(elem) for elem in i]) + '\\\\\n\t\t\t\\hline\n'

    # -------------caption-------------
    caption_text = ''
    if caption is not None:
        caption_text = f'\t\\caption{{\\label{{tab:bolts}} {caption}}}\n'

    # -------------end-------------
    table_end = f'\t\t\\end{{tabular}}\n\t\\end{{center}}\n{caption_text}\\end{{table}}'

    return f'{table_begin}{body}{table_end}'
