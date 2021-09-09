# --------------------------------------------------------------------------------------
# File: "PandasFunctions.py"
# Dir: "/mnt/f/GithubRepos/SandsPythonFunctions/src/SandsPythonFunctions"
# Created: 2020-06-26
# --------------------------------------------------------------------------------------

"""
this file contains useful functions that manipulate pandas dataframes

display_full_dataframe
add_month_year_column_function
"""


def display_full_dataframe(dta):
    """displays a dataframe without cutting anything off for being too long

    Arguments:
        dta {dataframe} -- a dataframe you wish to display
    """
    import pandas as pd

    with pd.option_context("display.max_rows", None, "display.max_columns", None):
        print(dta)


def add_month_year_column_function(dta, column_name):
    """
    add a year and year-monthcolumn to the dataframe for easier date useage
    """
    import pandas as pd

    dta["column_name"] = pd.to_datetime(dta["column_name"])
    dta["year_month"] = pd.to_datetime(dta["column_name"]).dt.strftime("%Y-%m")
    dta["year"] = pd.to_datetime(dta["column_name"]).dt.strftime("%Y")
    return dta


def remove_documents_below_x_words(dta, column_name, min_number_words_in_doc=0):
    print(f"length before removing docs with less than {min_number_words_in_doc} words: {len(dta)}")
    if min_number_words_in_doc > 0:
        dta["num_words"] = dta[column_name].apply(lambda x: len(str(x).split()))
        dta = dta[dta["num_words"] > min_number_words_in_doc]
    print(f"length after removing docs with less than {min_number_words_in_doc} words: {len(dta)}")
    return dta
