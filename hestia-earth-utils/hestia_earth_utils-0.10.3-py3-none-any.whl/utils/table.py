import re


def pivot_csv(filepath: str, exclude_columns=[]):
    """
    Pivot the values of term.@id columns, forming new columns with values taken from the respective .value columns.

    Note that this function requires pandas, which is not included in the package requirements by default due to size.

    Parameters
    ----------
    filepath : str
        Path to the CSV to be pivoted.

    exclude_columns : list
        Which columns to exclude.

    Returns
    -------
    pandas.DataFrame
        Pivoted pandas dataframe

    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError("Run `pip install pandas~=1.2.0` to use this functionality")

    df = pd.read_csv(filepath, index_col=None)

    term_columns_to_pivot = df.filter(regex=r'^.*\.[a-zA-Z]+\.[\d]+\.term\.@id$')
    term_columns_to_pivot = list(filter(lambda x: x not in exclude_columns, term_columns_to_pivot))

    df_out = df.copy()

    # drop all columns for pivot
    term_columns_no_pivot = list(df.filter(regex=r'^.*\.[a-zA-Z]+\.[\d]').columns.values)
    df_out.drop(term_columns_no_pivot, axis=1, inplace=True)

    out = []
    for column in term_columns_to_pivot:
        stem = column.strip('term.@id')
        value_col = '.'.join([stem, 'value'])

        # handle node without value column
        if value_col not in df:
            df[value_col] = '-'

        p = df.pivot(columns=[column], values=[value_col])

        p = p.dropna(axis=1, how='all')
        p = p.droplevel(axis=1, level=0)
        p = p.rename(lambda x: '.'.join([re.sub(r'(\.[\d]+)$', '', stem), x, 'value']), axis=1)

        out.append(p)

    pivoted_columns = pd.concat(out, axis=1)
    return pd.concat((df_out, pivoted_columns), axis=1)
