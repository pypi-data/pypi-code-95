""" Reads in the sales data and loads into a pandas dataframe """
import collections
import glob
from json import encoder
import re
import os
import logging
import pandas as pd

from markdown_predictions.selection import COLUMN_SELECTION, COLUMN_MAPPING


class LoadSalesData:

    def __init__(self, sales_data: pd.DataFrame):
        self.sales_data = sales_data

    @staticmethod
    def extract_season(file_path: str, file_name: str):
        """ Regex the file name to extract the season """
        # Define the regex expression

        if file_path:
            regex_expr = re.compile(rf"{file_path}\/(?P<season>\w+) W.+.csv")
        else:
            regex_expr = re.compile(rf"(?P<season>\w+) W.+.csv")


        m = regex_expr.search(file_name)

        if m:
            return m.group('season')
        else:
            logging.critical(f"Season cannot be extracted from {file_name}.")
            return None

    @staticmethod
    def parse_file(filename: str, pre_post_toggle: str, column_mapping: dict, selected_columns: dict, file_path: str=""):
        """ Parse csv file into dataframe """
        # Parse csv into dataframe
        seasonal_data = pd.read_csv(filename, index_col=None, encoding='utf-8')

        if "image_url" in seasonal_data.columns:
            images = seasonal_data.pop("image_url", None)
        else:
            images = None
        

        # Remove all escape characters
        seasonal_data.columns = [col.replace('\r','').replace('\n','').lower() for col in seasonal_data.columns]

        # Rename the columns
        seasonal_data.rename(columns=column_mapping, inplace=True)

        # If not all selected columns in the csv, report & exit.
        if not set(seasonal_data.columns).issuperset(set(selected_columns)):
            print(f"Not all selected columns present in csv file: {filename}.")
            print(f"Missing columns: {set(selected_columns).difference(set(seasonal_data.columns))}\nExiting.")
            exit(1)

        # Select the columns
        seasonal_data = seasonal_data[selected_columns]

        # Add season as a column to the dataframe
        season = LoadSalesData.extract_season(file_path=file_path, file_name=filename)

        if not season:
            # If season unable to be extracted skip
            return False
        seasonal_data['season'] = season

        # Add suffix
        seasonal_data = seasonal_data.add_suffix(suffix=f"_{pre_post_toggle}")
        
        if images:
            seasonal_data["image_url"] = images
        return seasonal_data


    @staticmethod
    def read_in_files(file_path: str, pre_post_toggle: str, column_mapping: dict, selected_columns: dict):
        """ Read in files from local directory """
        all_sales_data = []

        for seasonal_file in glob.glob(f'{file_path}/*{pre_post_toggle}*'):
            logging.info(f"Reading file: {seasonal_file}")

            seasonal_data = LoadSalesData.parse_file(filename=seasonal_file, pre_post_toggle=pre_post_toggle,
                                                     column_mapping=column_mapping, selected_columns=selected_columns,
                                                     file_path=file_path)
            if not type(seasonal_data) == pd.DataFrame:
                continue
            all_sales_data.append(seasonal_data)

        return pd.concat(all_sales_data, axis=0, ignore_index=True)

    @staticmethod
    def make_dict_lowercase(input_dict: dict):
        lower_case_dict = {}
        for k, v in input_dict.items():
            lower_case_dict[k.lower()] = v
        return lower_case_dict

    @classmethod
    def load_in_files(cls, file_path: str):
        """ Load in Files """
        mapping = LoadSalesData.make_dict_lowercase(COLUMN_MAPPING)

        pre_sales_data = LoadSalesData.read_in_files(file_path=file_path, pre_post_toggle="PRE", column_mapping=mapping, selected_columns=COLUMN_SELECTION["PRE"])
        post_sales_data = LoadSalesData.read_in_files(file_path=file_path, pre_post_toggle="POST", column_mapping=mapping, selected_columns=COLUMN_SELECTION["POST"])

        sales_data = pd.merge(pre_sales_data,
                            post_sales_data,
                            left_on=[key + "_PRE" for key in COLUMN_SELECTION["reference_keys"]] ,
                            right_on=[key + "_POST" for key in COLUMN_SELECTION["reference_keys"]],
                            how="inner")

        training_adjustment = [col + "_PRE" for col in COLUMN_SELECTION["PRE"]] + ["quantity_sold_POST", "quantity_sold_sub1_POST"]
        sales_data = sales_data[training_adjustment]
        return cls(sales_data)

    @classmethod
    def load_in_test_file(cls, test_file: str):
        mapping = LoadSalesData.make_dict_lowercase(COLUMN_MAPPING)
        sales_data = LoadSalesData.parse_file(filename=test_file, pre_post_toggle="PRE", column_mapping=mapping, selected_columns=COLUMN_SELECTION["PRE"])
        return cls(sales_data)


if __name__ == "__main__":
    loaded_data = LoadSalesData.load_in_files("raw_data")
