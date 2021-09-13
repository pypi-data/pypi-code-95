from typing import List, Dict
import pandas as pd
import re


def _get_content_row(bl_sdf: pd.DataFrame, t1_sdf: pd.DataFrame, t2_sdf: pd.DataFrame, profile_name: str, profile_group: str,
                     bl_total_cust: int, t1_total_cust: int, t2_total_cust: int):
    # sum abs number for each label value
    bl_abs = bl_sdf['no_of_cust'][bl_sdf[profile_name] == profile_group].sum()
    t1_abs = t1_sdf['no_of_cust'][t1_sdf[profile_name] == profile_group].sum()
    t2_abs = t2_sdf['no_of_cust'][t2_sdf[profile_name] == profile_group].sum()

    bl_perc = 0.0
    t1_perc = 0.0
    t2_perc = 0.0

    # calculate penetration
    if bl_abs is not None:
        bl_perc = round((bl_abs / bl_total_cust) * 100, 2)
    if t1_abs is not None:
        t1_perc = round((t1_abs / t1_total_cust) * 100, 2)
    if t2_abs is not None:
        t2_perc = round((t2_abs / t2_total_cust) * 100, 2)

    # calculate deviation
    t1_dev = (t1_perc - bl_perc)
    t2_dev = (t2_perc - bl_perc)
    return [profile_group, bl_abs, bl_perc, t1_abs, t1_perc, t1_dev, t2_abs, t2_perc, t2_dev]


def create_profile_df(bl_sdf: pd.DataFrame, t1_sdf: pd.DataFrame, t2_sdf: pd.DataFrame, selected_profiles: List[str], profile_title_map: Dict[str, str]):
    column_names = ['label', 'base_abs', 'base_perc', 'target1_abs', 'target1_perc', 'target1_dev', 'target2_abs', 'target2_perc', 'target2_dev']

    bl_total_cust = bl_sdf['no_of_cust'].sum()
    t1_total_cust = t1_sdf['no_of_cust'].sum()
    t2_total_cust = t2_sdf['no_of_cust'].sum()
    result_list = []
    for profile_name in selected_profiles:
        profile_groups = bl_sdf.groupby([profile_name]).groups.keys()
        profile_title = profile_title_map[profile_name]

        # create title row
        result_list.append([profile_title, None, None, None, None, None, None, None, None])

        # create content row
        for profile_group in profile_groups:
            if profile_group != "" and profile_group is not None and str(profile_group) != '0' and str(profile_group) != 'N':
                content_row = _get_content_row(bl_sdf, t1_sdf, t2_sdf, profile_name, profile_group, bl_total_cust, t1_total_cust, t2_total_cust)
                result_list.append(content_row)

    profile_df = pd.DataFrame(result_list, columns=column_names)
    return profile_df


def create_product_df(bl_sdf: pd.DataFrame, t1_sdf: pd.DataFrame, t2_sdf: pd.DataFrame, selected_products: List[str], product_title_map: Dict[str, str]):
    column_names = ['label', 'base_abs', 'base_perc', 'target1_abs', 'target1_perc', 'target1_dev', 'target2_abs', 'target2_perc', 'target2_dev']

    bl_total_cust = bl_sdf['no_of_cust'].sum()
    t1_total_cust = t1_sdf['no_of_cust'].sum()
    t2_total_cust = t2_sdf['no_of_cust'].sum()
    result_list = [["Product Holding", None, None, None, None, None, None, None, None]]

    for product_name in selected_products:
        product_values = bl_sdf.groupby([product_name]).groups.keys()

        for product_value in product_values:
            if product_value != "" and product_value is not None and str(product_value) != '0' and str(product_value) != 'N':
                content_row = _get_content_row(bl_sdf, t1_sdf, t2_sdf, product_name, product_value, bl_total_cust, t1_total_cust, t2_total_cust)
                content_row[0] = f"Have {product_title_map[product_name]}"
                result_list.append(content_row)

    profile_df = pd.DataFrame(result_list, columns=column_names)
    return profile_df


def get_result_df(bl_sdf: pd.DataFrame, t1_sdf: pd.DataFrame, t2_sdf: pd.DataFrame, selected_profiles: List[str], profile_title_map: Dict[str, str],
                  selected_products: List[str], product_title_map: Dict[str, str]):
    profile_df = create_profile_df(bl_sdf, t1_sdf, t2_sdf, selected_profiles, profile_title_map)
    product_df = create_product_df(bl_sdf, t1_sdf, t2_sdf, selected_products, product_title_map)
    return profile_df.append(product_df).reset_index(drop=True)


def convert_result_df_to_data_as_rows(result_df: pd.DataFrame):
    data_rows = result_df[["label", "base_perc", "target1_abs", "target1_perc", "target1_dev", "target2_abs", "target2_perc", "target2_dev"]].to_numpy().copy().tolist()
    for i, row in enumerate(data_rows):
        count_null = 0
        for j, value in enumerate(row):
            if pd.isnull(value):
                count_null += 1
                data_rows[i][j] = 0
            if j in [4, 7]:
                data_rows[i][j] = round(data_rows[i][j])
            elif j in [1, 3, 6]:
                data_rows[i][j] = str(round(data_rows[i][j])) + " %"
            elif j in [2, 5]:
                data_rows[i][j] = "{:,}".format(int(data_rows[i][j]))
            else:
                data_rows[i][j] = re.sub('\[*.*\]', '', str(data_rows[i][j])).strip()
        # Check if is header row
        if count_null > 3:
            data_rows[i] = [data_rows[i][0]]
    return data_rows
