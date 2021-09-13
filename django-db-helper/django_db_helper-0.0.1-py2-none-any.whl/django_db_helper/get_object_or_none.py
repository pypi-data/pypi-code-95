from typing import Dict


def get_object_or_none(model, **kwargs:Dict[str,any]) ->{object,None}:
    """
    Use get() to return a matching object and return None if no match is found.
    :param model:
    :param kwargs:
    :return:
    """

    try:
        result = model.objects.get(**kwargs)
    except model.DoesNotExist:
        result = None
    return result