import networkx as nx
from collections import Counter

__all__ = [
    'nx_get_leaves',
    'nx_get_roots',
    'get_leaves',
    'get_roots',
    'order_nodes_from_roots',
    'order_nodes_from_leaves',
    'count_edges_by_attributes',
    'count_edges_by_attribute',
    'plot_circular_graph',
]


def nx_get_leaves(G, include_dangling=True):
    return (x for x in G.nodes() if G.out_degree(x) == 0 and (include_dangling or G.in_degree(x) > 0))


def nx_get_roots(G, include_dangling=True):
    return (x for x in G.nodes() if G.in_degree(x) == 0 and (include_dangling or G.out_degree(x) > 0))


def __order_nodes(G, roots=True):
    """"
        Returns nodes orderes starting from the roots  or from the leaves 
    """
    def __get_front(G):
        if roots:
            return list(nx_get_roots(G))
        else:
            return list(nx_get_leaves(G))

    G = nx.DiGraph(G)
    front = __get_front(G)
    nodes = []
    while front:
        nodes.extend(front)
        G.remove_nodes_from(front)
        front = __get_front(G)
    return nodes


def order_nodes_from_roots(G):
    """
        Returns the node of G ordered from the ROOTS to the LEAVES
    """
    return __order_nodes(G, True)


def order_nodes_from_leaves(G):
    """
        Returns the node of G ordered from the LEAVES to the ROOTS
    """
    return __order_nodes(G, False)


def count_edges_by_attributes(G, attributes, ret='singleton'):
    """
        ret : What to return
            "all": Dict[Counter] - A counter per each attribute
            "product": Counter[tuple] - A counter with the counting of the products of the attributes
            "both": Return both 'all' and 'product'
            "singleton": Counter - Return only the counter if attribute is one only, otherwise "all"
    """

    attributes = attributes if isinstance(attributes, list) else [attributes]
    counter = Counter()
    sub_counters = {attr: Counter() for attr in attributes}
    for edge in G.edges:
        identifier = tuple([G.edges[edge][attr] for attr in attributes])
        for ident, attr in zip(identifier, attributes):
            sub_counters[attr].update([ident])
        counter.update([identifier])
    if ret == 'both':
        return counter, sub_counters
    elif ret == 'product':
        return counter
    elif ret == 'singleton' and len(attributes) == 1:
        return list(sub_counters.values())[0]
    elif ret == 'singleton' or ret == 'all':
        return sub_counters
    else:
        raise ValueError(f'Invalid value ({ret}) for argument ret')


def count_edges_by_attribute(*args, **kwargs):
    """ Alias for count_edges_by_attributes"""
    return count_edges_by_attributes(*args, **kwargs)


def plot_circular_graph(G, show=True):
    import matplotlib.pyplot as plt

    pos = nx.circular_layout(G)
    nx.draw_networkx(G, pos)
    plt.axis('off')
    if show:
        plt.show()


get_leaves = nx_get_leaves
get_roots = nx_get_roots
