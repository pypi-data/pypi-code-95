import pandas as pd
from tabulate import tabulate


def read(file, separator=","):
    df = pd.read_csv(file, separator)
    return df


def write(df, outfile):
    if not outfile.endswith('.csv'):
        outfile = f'{outfile}.csv'
    df.to_csv(outfile)


def display_df(df):
    print(tabulate(df, headers='keys', tablefmt='psql'))


def config_display_pd(max_rows=None, max_columns=None,
                      display_width=1000, col_header_justify='center',
                      precision=10):
    pd.set_option('display.max_rows', max_rows)
    pd.set_option('display.max_columns', max_columns)
    pd.set_option('display.width', display_width)
    pd.set_option('display.colheader_justify', col_header_justify)
    pd.set_option('display.precision', precision)
