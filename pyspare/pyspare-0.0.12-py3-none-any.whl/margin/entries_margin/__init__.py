from pyspare.margin.entries_margin.entries_margin import EntriesMargin


def entries_margin(entries, head, tail, key_read, read, rule):
    return EntriesMargin \
        .build(entries, head, tail) \
        .stringify(key_read, read) \
        .to_list(rule)  # ('..', '..') if rule is None else rule
