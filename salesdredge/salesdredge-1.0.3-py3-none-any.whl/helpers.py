import hashlib


def hash_for_id(string):
    """
    Transform a string into an ID.
    :param string:
    :return:
    """
    return hashlib.md5(str(string).encode()).hexdigest()