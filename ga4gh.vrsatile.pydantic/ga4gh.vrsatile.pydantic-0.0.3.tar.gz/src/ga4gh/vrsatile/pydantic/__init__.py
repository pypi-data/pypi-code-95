"""Initialize GA4GH VRSATILE Pydantic."""


def return_value(cls, v):
    """Return value from object.

    :param ModelMetaclass cls: Pydantic Model ModelMetaclass
    :param v: Model from vrs or vrsatile
    :return: Value
    """
    if v is not None:
        try:
            if isinstance(v, list):
                tmp = list()
                for item in v:
                    while True:
                        try:
                            item = item.__root__
                        except AttributeError:
                            break
                    tmp.append(item)
                v = tmp
            else:
                v = v.__root__
        except AttributeError:
            pass
    return v
