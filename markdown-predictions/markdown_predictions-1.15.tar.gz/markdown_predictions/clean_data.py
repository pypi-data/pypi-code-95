""" This script cleans the dataframe """
from types import prepare_class
from numpy.core.numeric import True_
import pandas as pd
from datetime import datetime, timedelta

from markdown_predictions.parse_data import LoadSalesData


PRICE_COLS = ["price_PRE", "price_POST"]
TARGET_SALES = ["quantity_sold_POST", "quantity_sold_sub1_POST"]
DATE_COLS = ["first_week_sale_PRE"]


class PreProcessor:

    def __init__(self, df: pd.DataFrame):
        self.df = df.astype(str) # cast as strings to process
        self.numeric_cols = []
        self.object_cols = []

    def drop_rows_without_reference(self):
        """ If no product reference drop row - likely to be the total rows """
        self.df = self.df[self.df.reference_PRE.notnull()]

    def drop_row_with_missing_entries(self):
        """ Drop all rows with a '-' or 'nan' within them """
        self.df = self.df[~(self.df == '-').any(axis=1)]
        self.df = self.df[~(self.df == 'nan').any(axis=1)]
        self.df = self.df[~(self.df == 'Inconnu').any(axis=1)]

    def replace_decimal_in_price_cols(self):
        """ Replace the comma with a decimal point in price columns """
        for price_col in PRICE_COLS:
            if not price_col in self.df:
                continue
            self.df[price_col] = self.df[price_col].replace({r',': '.'}, regex=True)

    def clean_up_symbols(self, x):
        """ Remove symbols and commas from columns """
        x = x.replace(',', '').replace('€', '')
        if '%' in x:
            x =  str(float(x.replace('%', '')) / 100.)
        return x

    def make_columns_numeric(self):
        """ Try to make columns numeric, else leave as original type """
        for col in self.df.columns:
            try:
                self.df[col] = self.df[col].apply(lambda x: self.clean_up_symbols(x)).astype(float)
                self.numeric_cols.append(col)
            except ValueError as e:
                # print(e)
                self.object_cols.append(col)

    def add_2week_sales(self):
        """ Add sales target """
        self.df["two_week_sales"] = self.df[TARGET_SALES].sum(axis=1)
        self.df = self.df[self.df["two_week_sales"] >= 0]
        self.df.drop(TARGET_SALES, axis=1, inplace=True)

    def parse_dates(self):
        """ Parse dates - supports '%Y-S%U' format currently"""
        for col in DATE_COLS:
            self.df["weeks_plus"] = self.df[col].apply(lambda dt: timedelta(weeks=int(dt[-2:])))
            self.df[col] = self.df[col].apply(lambda dt: datetime.strptime(dt,"%Y-S%U")) + self.df["weeks_plus"]
            self.df.drop("weeks_plus", axis=1, inplace=True)

    def clean_up_data(self, train_set: bool=True):
        """ Clean up the dataframe """
        self.drop_rows_without_reference()
        self.drop_row_with_missing_entries()
        self.replace_decimal_in_price_cols()
        self.make_columns_numeric()
        self.parse_dates()
        if train_set:
            self.add_2week_sales()


def outlier_scan(df, cols, threshold=0.1):
    """ Detect numeric outliers based upon quantile threshold """
    liers = set([])
    index = df.index.copy()
    for col in cols:
        Q1 = df[[col]].quantile(threshold)[0]
        Q3 = df[[col]].quantile(1-threshold)[0]
        IQR = Q3 - Q1
        low_liers = df[[col]][df[col] < Q1 - 1.5 * IQR].index.tolist()
        high_liers = df[[col]][df[col] > Q3 + 1.5 * IQR].index.tolist()
        liers.update(low_liers)
        liers.update(high_liers)
    return sorted(list(liers))

if __name__ == "__main__":
    # Load in the data locally into a single dataframe
    loaded_data = LoadSalesData.load_in_files("raw_data")
    # Initiate pre-processing class instance
    pre_processor = PreProcessor(df=loaded_data.sales_data)
    pre_processor.clean_up_data()
