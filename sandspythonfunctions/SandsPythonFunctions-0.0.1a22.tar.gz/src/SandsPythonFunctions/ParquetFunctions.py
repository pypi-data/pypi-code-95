# --------------------------------------------------------------------------------------
# File: "ParquetFunctions.py"
# Dir: "/mnt/f/GithubRepos/SandsPythonFunctions/src/SandsPythonFunctions"
# Created: 2020-06-26
# --------------------------------------------------------------------------------------

"""
this file contains functions related to dealing with pandas dataframes that are stored in parquet
files. Note that I use zstandard to compress these files.

length_parquet_files
read_parquet_by_path
save_dataframe_as_parquet
"""


def read_parquet_by_path(path, columns=None, reset_index=True):
    """this function will read in all files given if the path variable is a list of
    pathlib objects or will read in the file if the path is one pathlib object

    Args:
        path (pathlib object): this must be a full path string or a pathlib object for a
        parquet file or a list of pathlib objects

        columns (list of strings, optional): this must be a list of strings even if
        there is only one column included, also the columns must be present in the files
        included in the path otherwise it will throw an error. Defaults to None.

        reset_index {bool} -- if True then the index of the dataframe will be reset
        (default: {False})

    Returns:
        dataframe: this returns the pandas dataframe of the path object or a combined
        pandas dataframe if there was a list of paths given
    """
    import pandas as pd
    import pathlib
    import pyarrow as pa
    import pyarrow.parquet as pq
    import sys

    if type(path) == list:
        dataframe_list = []
        for file in path:
            if isinstance(file, (pathlib.PurePath)):
                if columns is None:
                    if str(file.resolve()).endswith(".parquet"):
                        dta = pq.read_table(file)
                        dataframe_list.append(dta.to_pandas())
                else:
                    if str(file.resolve()).endswith(".parquet"):
                        dta = pq.read_table(file, columns=columns)
                        dataframe_list.append(dta.to_pandas())
            else:
                sys.exit(
                    f"The path is a {type(file)} type please enter either a pathlib object or a string"
                )
                raise SystemExit
        dta = pd.concat(dataframe_list)
    elif isinstance(path, (pathlib.PurePath)):
        if columns is None:
            if str(path.resolve()).endswith(".parquet"):
                dta = pq.read_table(path)
                dta = dta.to_pandas()
        else:
            if str(path.resolve()).endswith(".parquet"):
                dta = pq.read_table(path, columns=columns)
                dta = dta.to_pandas()
    else:
        sys.exit(
            f"The path is a {type(path)} type please enter either a pathlib object or a string"
        )
        raise SystemExit
    if reset_index:
        return dta.reset_index(drop=True)
    else:
        return dta


def length_parquet_files(files, columns=None):
    """This function will take a list of parquet files and print the name of each file
    along with the number of rows for that file.

    Then at the end will print out the total number of rows for all of the parquet files
    included in the list.
    """
    import pyarrow as pa
    import pyarrow.parquet as pq
    import pandas as pd

    total_len = 0
    for file in files:
        if columns is None:
            dta = pq.read_table(file)
        else:
            dta = pq.read_table(file, columns=columns)
        dta = dta.to_pandas()
        row_num = len(dta)
        print(f"the length of {file.name} is: {row_num}")
        total_len += row_num
    print(f"the length of the files is: {total_len}")


def save_dataframe_as_parquet(dta, file_destination=""):
    """this function saves a pandas dataframe as a parquet file compressed with the
    zstandard compression algorithm

    Arguments:
        dta {pandas dataframe} -- the dataframe you want saved

    Keyword Arguments:
        pathlib_destination {pathlib object} | {str} -- This is either a string or
        pathlib object. IMPORTANT: you must have both the folder and filename
        (default: {""})
    """
    from pathlib import Path
    import pandas as pd
    import pathlib
    import pyarrow as pa
    import pyarrow.parquet as pq
    import sys

    if file_destination != "":
        if type(file_destination) == str:
            filename = Path(file_destination)
        elif isinstance(file_destination, (pathlib.PurePath)):
            filename = file_destination.resolve()
        else:
            sys.exit(
                f"The file_destination is a {type(file_destination)} type please enter either a pathlib object or a string"
            )
            raise SystemExit
        filename.parent.mkdir(parents=True, exist_ok=True)
    else:
        filename = Path(__file__).parent / "output.parquet"
    dta = pa.Table.from_pandas(dta)
    # print(filename)  # TESTCODE:
    # print(type(filename))  # TESTCODE:
    pq.write_table(dta, filename, compression="zstd")
