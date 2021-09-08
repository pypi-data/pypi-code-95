import os
import shutil

LOCALAPP_ROOT = 'LOCALAPPDATA'

def check_and_make_new_proj_localapp(app_root, proj_name):
    root = check_and_make_localapp_application_path_dir(app_root)
    return check_and_make_proj_path_dir(root, proj_name)

def root_and_name(root, proj_name):
    return f"{root}\\{proj_name}"

def check_and_make_proj_path_dir(root, proj_name):
    proj_dir = root_and_name(root, proj_name)
    check_and_make_dir(proj_dir)

    return proj_dir

def localapp_root(root):
    local_app_data = os.getenv(LOCALAPP_ROOT)
    return f"{local_app_data}\\{root}"

def check_and_make_localapp_application_path_dir(application_root):
    la_root = localapp_root(application_root)
    check_and_make_dir(la_root)
    return la_root

def check_and_make_dir(dir):
    chk = os.path.isdir(dir)

    if not chk:
        os.makedirs(dir)

def copy_file_from_to(filepath_to_copy: str, to_filepath: str):
    shutil.copy2(filepath_to_copy, to_filepath)
