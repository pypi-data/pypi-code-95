import os


def init_data_working_dir(working_dir):
    temp_working_dir = working_dir or "/data"
    if not os.access(temp_working_dir, os.W_OK): temp_working_dir = os.path.expanduser("~/cnvrg_datasets")
    return temp_working_dir