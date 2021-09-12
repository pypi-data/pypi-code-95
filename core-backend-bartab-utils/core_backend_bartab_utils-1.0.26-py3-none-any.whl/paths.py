import os
from django.conf import settings

def get_domain() -> str:
    if settings.IS_PRODUCTION:
        return f"https://{settings.URL_PREFIX}.{settings.DOMAIN}"
    elif settings.IS_DEVELOPMENT:
        return f"https://dev.{settings.URL_PREFIX}.{settings.DOMAIN}"
    elif settings.IS_QA:
        return f"https://qa.{settings.URL_PREFIX}.{settings.DOMAIN}"
    else:
        return f"http://localhost:{settings.PORT}"


def get_parent_directory(file_running_script: str) -> str:
    file_running_script_array = file_running_script.split("/")

    dot_count = file_running_script_array[-1].count(".")
    if dot_count > 0:
        if file_running_script_array[-1][0] != '.' or dot_count > 1:
            del file_running_script_array[-1]
    
    return "/".join(file_running_script_array)

# Use __file__ to get path of file running script
def get_relative_path(path: str, file_running_script: str) -> str:
    starting_local_split = get_parent_directory(file_running_script).split("/")
    split_path = path.split('/')
    
    if split_path[0] == '.':
        if len(split_path) == 1:
            split_path = []
        else:
            split_path = split_path[1:]
    else:
        while len(split_path) > 0 and split_path[0] == "..":
            split_path.pop(0)
            starting_local_split = starting_local_split[:-1]

    starting_local = "/".join(starting_local_split)
    landing_path = "/".join(split_path)

    if landing_path == '':
        return starting_local
    else:
        return f"{starting_local}/{landing_path}"
