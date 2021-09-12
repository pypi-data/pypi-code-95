from typing import Union


def get_first_line(o, default_val: str) -> Union[str, None]:
    """
    Get first line for a pydoc string
    :param o: object which is documented (class or function)
    :param default_val: value to return if there is no documentation
    :return: the first line which is not whitespace
    """
    doc: Union[str, None] = o.__doc__
    if doc is None:
        return default_val
    lines = doc.split("\n")
    for line in lines:
        if line == "" or line.isspace():
            continue
        return line.strip()
    return default_val
