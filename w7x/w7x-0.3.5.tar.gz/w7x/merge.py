import itertools
import numpy as np

import rna.pattern.composite
from w7x.switches import exposed
import w7x.lib.dataclasses as dataclasses


def cls_from_instances(*instances):
    """
    Pick the first type from the instances
    """
    inst = instances[0]
    while isinstance(inst, (list, tuple)):
        inst = inst[0]
    return type(inst)


def merge_dataclasses_field(*instances, field=None, merge_dict=None) -> dict:
    """
    Add the key field.name with the value of the merged field attributes of instances
    to merge_dict (create merge_dict if None).
    Use field.metadata["merged"] as merge function if present.
    """
    if merge_dict is None:
        merge_dict = {}
    if isinstance(field, str):
        cls = cls_from_instances(*instances)
        for fld in dataclasses.fields(cls):
            if fld.name == field:
                field = fld
                break
        else:
            raise ValueError("Field not found")
    if field is None:
        raise AttributeError("Requiring field")

    values_reversed = []
    if "merged" in field.metadata:
        merge_function = field.metadata["merged"]
    else:
        merge_function = None
    with exposed(True):
        for instance in reversed(instances):
            if not hasattr(instance, field.name):
                # e.g. init = False
                continue
            value = getattr(instance, field.name)
            if value is not None:
                values_reversed.append(value)
            if merge_function is not None:
                continue
            if hasattr(value, "merged"):
                merge_function = value.merged
                continue
            if value is not None:
                # Fallback: take the first value from behind. This is the reason for "reversed"
                merge_dict[field.name] = value
                break
        else:
            if merge_function is not None and values_reversed:
                merge_dict[field.name] = merge_function(*reversed(values_reversed))
    return merge_dict


def merge_dataclasses(*instances, cls=None, **kwargs):
    """
    Merge the dataclass fields of multiple instances of the same dataclass.

    Returns:
        dict: attributes and values

    Args:
        kwargs: allows providing some default
    """
    if cls is None:
        cls = cls_from_instances(*instances)
    # Determin forwarded fields -> later we skip the field we forward
    children_aliased = False
    for field in dataclasses.fields(cls):
        if dataclasses.is_alias_field(field):
            children_aliased = True
            break

    for field in dataclasses.fields(cls):
        if children_aliased and field.name == "_children":
            continue
        merge_dataclasses_field(*instances, field=field, merge_dict=kwargs)
    obj = cls(**kwargs)
    return obj


def merge_children_cumulative(*instances):
    """
    Just add up the children.
    """
    return list(itertools.chain(*instances))


def merge_children_structure_preserving(*instances, **kwargs):
    """
    Merge the instances of type cls with strictly merging equal attributes and only appending
    those that are not
    """
    # skip empty instances
    children = None
    others = instances
    while not children:
        children = others[0]
        if len(others) > 1:
            others = others[1:]
        else:
            others = []
            break

    # ignore empty children
    if not children:
        return []

    # determine composite type
    parent_types = rna.pattern.composite.get_leaves(
        children, apply_composite=lambda leaves, **kwargs: type(kwargs["component"])
    )

    others = [
        rna.pattern.composite.get_leaves(children, flat=True) for children in others
    ]
    consumed = []

    def apply_leaf_merge(leaf, **kwargs):
        merges = []
        for o, other_leafs in enumerate(others):
            for l, ol in enumerate(other_leafs):  # noqa
                if (o, l) in consumed:
                    continue
                if leaf == ol:
                    merges.append(ol)
                    consumed.append((o, l))
                    break
        leaf = merge_dataclasses(leaf, *merges)
        return leaf

    def apply_composite_merge(leaves, **kwargs):
        position = kwargs["position"]
        cls = parent_types
        for p in position:
            cls = cls[p]

        comp = cls()
        comp._children = []  # in case defaults are set
        for leaf in leaves:
            comp.add(leaf)
        return comp

    return rna.pattern.composite.get_leaves(
        children, apply=apply_leaf_merge, apply_composite=apply_composite_merge
    )


def merge_dicts(*instances, merge_values=None):
    """
    Examples:
        >>> import w7x.merge
        >>> import numpy as np
        >>> w7x.merge.merge_dicts({1:1, 2:1, 3:2}, {4:4, 2:1, 3:2})
        {1: 1, 2: 1, 3: 2, 4: 4}
        >>> w7x.merge.merge_dicts({1:1, 2:1, 3:2}, {4:4, 2:1, 3:1}, merge_values=np.add)
        {1: 1, 2: 2, 3: 3, 4: 4}
    """
    if merge_values is None:

        def merge_values(x, y):
            return x

    res = dict(instances[0])
    for inst in instances[1:]:
        for key in inst.keys():
            if key not in res:
                res[key] = inst[key]
            else:
                res[key] = merge_values(res[key], inst[key])
    return res


def merge_dicts_add_values(*instances):
    """
    Alias for merge_dicts with value addition
    """
    return merge_dicts(*instances, merge_values=np.add)


def merge_dicts_assert_equal(*instances):
    """
    Alias for merge_dicts for static values (expecting the same value in the dict if key is
    conflicting)

    Examples:
        >>> import w7x.merge
        >>> w7x.merge.merge_dicts_assert_equal({1:1, 2:1, 3:2}, {4:4, 2:1})
        {1: 1, 2: 1, 3: 2, 4: 4}
    """

    def merge_assert_equal(one, other):
        assert one == other
        return one

    return merge_dicts(*instances, merge_values=merge_assert_equal)


def merge_discard(*instances):
    """
    Setting e.g. a cache attribute to None on merge
    """
    return None


def merge_value_or_none(*instances):
    """
    Return first instance which is not None or None
    """
    if not instances:
        return None
    for inst in instances:
        if inst is not None:
            return inst
    else:
        return None
