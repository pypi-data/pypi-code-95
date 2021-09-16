from cloudspec import CloudSpecFunction


def return_sphinx_doc(hub, func_data: CloudSpecFunction):
    ret = ""
    if func_data.return_type:
        ret += "\n\n    Returns:\n"
        ret += f"        {func_data.return_type}"
        ret += "\n"
    return ret
