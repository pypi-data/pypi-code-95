from collections import namedtuple, defaultdict
from typing import Callable, Optional, List, Dict, Sequence, Hashable

def __identity(x):
    return x


def group_by(sequence: Sequence, key_selector: Callable=__identity, value_selector: Callable = __identity) -> Dict:
    """
    Group sequence elements into dictionary
    
    Parameters
    ----------
    
    sequence: Sequence[TItem']
        Sequence to be groupped. 
    
    key_selector: Callable[TItem', TKey']
        Key selector. Default is identity
    
    value_selector: Callable[TItem', TKey']
        Value selector. Default is identity

    Returns
    -------
    Dict
        Groupped items

    Examples
    -------
    >>> TestItem = namedtuple("TestItem", ["key", "value"])
    >>> data1 = [TestItem("a", "A"), TestItem("b", "B"), TestItem("a", "A"), TestItem("a", "A+")]
    >>> result = group_by(data1, key_selector=lambda x: x.key, value_selector=lambda x: x.value)
    >>> test_utils.assertListEqual(result["a"], ["A","A","A+"])
    >>> test_utils.assertListEqual(result["b"], ["B"])
    """
    res = defaultdict(list)
    for x in sequence:
        res[key_selector(x)].append(value_selector(x))

    return res


def merge_into_dictionary(accumulator_dict: Dict[Hashable, Dict], seq_to_join: Sequence, property: Hashable, key_selector: Callable, value_selector: Callable = __identity) -> Dict[Hashable, Dict]:
    """
    Merge sequence elements into accumulator dicrionary.
    
    Parameters
    ----------
    accumulator_dict: Dict[Hashable, Dict]
        Accumulator dictionary. Contains merged elements

    seq_to_join: Sequence
        Sequence to be joined

    property: Hashable
        Property to be added to accumulator element

    key_selector: Callable[TItem', TKey']
        Key selector.
    value_selector: Callable[TItem', TKey']
        Value selector. Default is identity


    Returns
    -------
    Dict[Hashable, Dict]
        Mutated accumulator_dict (same instance)

    """
    for i in seq_to_join:
        key = key_selector(i)
        if key not in accumulator_dict:
            accumulator_dict[key] = {}

        current_node = accumulator_dict[key]
        
        current_node[property] = value_selector(i)
    return accumulator_dict


def merge_dictionaries(accumulator_dict: Dict[Hashable, Dict], dict_to_join: Dict, property: Hashable):
    """
    Merge elements of a dictionary into accumulator by key and value
    Parameters
    ----------
    accumulator_dict: Dict[Hashable, Dict]
        Accumulator dictionary. Contains merged elements

    dict_to_join: Dict
        Dictionary to join with accumulator

    property: Hashable
        Property to be added to accumulator element

    Returns
    -------
    Dict[Hashable, Dict]
        Mutated accumulator_dict (same instance)

    """
    return merge_into_dictionary(accumulator_dict, seq_to_join=dict_to_join.items(), property = property, key_selector= lambda x: x[0], value_selector=lambda x: x[1])
