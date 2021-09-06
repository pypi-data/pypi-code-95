# ------------------------------------------------------------ Imports ----------------------------------------------------------- #

# System
import os

# Local
from .utils import Utils
from .texts import new_class, new_enum, new_license, new_file, new_flow, gitignore, readme

# -------------------------------------------------------------------------------------------------------------------------------- #



# -------------------------------------------------------- Public methods -------------------------------------------------------- #

def create_new_class(name: str):
    _, file_path, _, _class = Utils.get_paths_name_class(name)
    config = Utils.get_config(True)
    Utils.create_file(file_path, new_class(_class, tab_size=config.spaces_per_tab, comment_line_len=config.comment_line_length))

def create_new_enum(name: str):
    _, file_path, _, _class = Utils.get_paths_name_class(name)
    config = Utils.get_config(True)
    Utils.create_file(file_path, new_enum(_class, tab_size=config.spaces_per_tab, comment_line_len=config.comment_line_length))

def create_new_file(name: str):
    _, file_path, _, _ = Utils.get_paths_name_class(name)
    config = Utils.get_config(True)
    Utils.create_file(file_path, new_file(tab_size=config.spaces_per_tab, comment_line_len=config.comment_line_length))

def create_new_flow(name: str):
    _, file_path, _, _ = Utils.get_paths_name_class(name)
    config = Utils.get_config(True)
    Utils.create_file(file_path, new_flow(tab_size=config.spaces_per_tab, comment_line_len=config.comment_line_length))

def create_new_gitignore():
    Utils.create_file(Utils.gitignore_path(), gitignore)

def create_new_readme():
    Utils.create_file(Utils.gitignore_path(), gitignore)

def create_new_subpackage(relative_folder_path: str, create_class: bool = True):
    _, init_file_path, _, _ = Utils.get_paths_name_class(Utils.init_file_path(relative_folder_path))

    if create_class:
        _, _, class_file_name, _class = Utils.get_paths_name_class(relative_folder_path)
        create_new_class(os.path.join(relative_folder_path, class_file_name))

        Utils.create_file(init_file_path, 'from .{} import {}'.format(class_file_name, _class))
    else:
        Utils.create_file(init_file_path, '')


# -------------------------------------------------------------------------------------------------------------------------------- #