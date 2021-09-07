from functools import partial, reduce

from aryth.comparison import max_compare, max_indicate, min_compare, min_indicate


def max_by(entries, indicator=None, initial=None):
    if isinstance(indicator, tuple): key_indicator, value_indicator = indicator
    else: key_indicator = value_indicator = indicator
    if not len(entries): return (None, None) if initial is None else initial
    if initial is None:
        key, value = entries[0]
        key_initial = key_indicator(key) if key_indicator else key
        value_initial = value_indicator(value) if value_indicator else value
        initial = (key_initial, value_initial)
    key_compare = partial(max_indicate, indicator=key_indicator) if key_indicator else max_compare
    value_compare = partial(max_indicate, indicator=value_indicator) if value_indicator else max_compare
    return reduce(
        lambda pr_kv, cu_kv: (key_compare(pr_kv[0], cu_kv[0]), value_compare(pr_kv[1], cu_kv[1])),
        entries,
        initial
    )


def min_by(entries, indicator=None, initial=None):
    if isinstance(indicator, tuple): key_indicator, value_indicator = indicator
    else: key_indicator = value_indicator = indicator
    if not len(entries): return (None, None) if initial is None else initial
    if initial is None:
        key, value = entries[0]
        key_initial = key_indicator(key) if key_indicator else key
        value_initial = value_indicator(value) if value_indicator else value
        initial = (key_initial, value_initial)
    key_compare = partial(min_indicate, indicator=key_indicator) if key_indicator else min_compare
    value_compare = partial(min_indicate, indicator=value_indicator) if value_indicator else min_compare
    return reduce(
        lambda pr_kv, cu_kv: (key_compare(pr_kv[0], cu_kv[0]), value_compare(pr_kv[1], cu_kv[1])),
        entries,
        initial
    )
