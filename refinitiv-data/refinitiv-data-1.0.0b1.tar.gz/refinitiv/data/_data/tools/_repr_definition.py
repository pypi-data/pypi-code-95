from typing import Any


def create_str_definition(
    self: object,
    middle_path: str = "",
    end_path: str = "",
    name_class: str = "Definition",
    content: Any = None,
) -> str:
    module_path = self.__module__
    new_path = get_new_path(
        module_path=module_path, middle=middle_path, end=end_path, class_name=name_class
    )
    hex_id_object = hex(id(self))
    frm_repr_str = f"<{new_path} object at {hex_id_object}>"

    if content:
        frm_repr_str = frm_repr_str.replace(">", f" {content}>")

    return frm_repr_str


def get_new_path(
    module_path: str, middle: str = "", end: str = "", class_name: str = ""
) -> str:
    """
    Examples
    --------
    >>> module_path = "refinitiv.data._data.pricing.stream"
    >>> class_name = "Definition"
    >>> start = "refinitiv.data"
    >>> end = "stream"
    >>> new_path = ".".join([start, end, class_name])
    >>> new_path
    ... "refinitiv.data.stream.Definition"

    >>> middle = "content"
    >>> new_path
    ... "refinitiv.data.content.stream.Definition"

    >>> end = "pricing"
    >>> new_path
    ... "refinitiv.data.pricing.Definition"

    >>> middle = "content"
    >>> end = "pricing"
    >>> new_path
    ... "refinitiv.data.content.pricing.Definition"
    """
    start, *_ = module_path.split("._data.", maxsplit=1)

    if not end:
        *_, end = module_path.rsplit(".", maxsplit=1)

    if middle:
        end = ".".join([middle, end])

    new_path = ".".join([start, end, class_name])
    return new_path
