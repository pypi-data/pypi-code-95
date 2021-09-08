"""
w7x utilty methods.
"""

import json
import hashlib
import time


def gen_run_id(obj, code=None, prefix="w7x", unique=True):
    """
    Generate run id.

    Examples:
        >>> from w7x.lib.utils import gen_run_id
        >>> id1 = gen_run_id({"a": 1})
        >>> id2 = gen_run_id({"a": 1})
        >>> id1 == id2
        False

        >>> id1 = gen_run_id({"a": 1}, unique=False)
        >>> id2 = gen_run_id({"a": 1}, unique=False)
        >>> id1 == id2
        True

    """

    if code is None:
        code = obj.__class__.__name__.lower()

    dump = json.dumps(
        obj.__dict__ if hasattr(obj, "__dict__") else obj,
        sort_keys=True,
        default=lambda o: "type={t}".format(t=type(o)),
    )

    #  Add timestamp to get unique run id
    if unique:
        dump += str(time.time())

    return "{prefix}-{code}-{hash_id}".format(
        prefix=prefix, code=code, hash_id=hashlib.md5(dump.encode()).hexdigest()
    )
