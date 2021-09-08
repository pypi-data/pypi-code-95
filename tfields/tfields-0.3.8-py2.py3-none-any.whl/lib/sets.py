"""
Algorithms around set operations
"""
import numpy as np
import tfields


class UnionFind(object):
    """
    Source:
        http://code.activestate.com/recipes/215912-union-find-data-structure/

    This algorithm and data structure are primarily used for Kruskal's Minimum
    Spanning Tree algorithm for graphs, but other uses have been found.

    The Union Find data structure is not a universal set implementation, but can
    tell you if two objects are in the same set, in different sets, or you can
    combine two sets.
    ufset.find(obja) == ufset.find(objb)
    ufset.find(obja) != ufset.find(objb)
    ufset.union(obja, objb)
    """
    def __init__(self):
        """
        Create an empty union find data structure.
        """
        self.num_weights = {}
        self.parent_pointers = {}
        self.num_to_objects = {}
        self.objects_to_num = {}
        self.__repr__ = self.__str__

    def insert_objects(self, objects):
        """
        Insert a sequence of objects into the structure.  All must be Python hashable.
        """
        for obj in objects:
            self.find(obj)

    def find(self, obj):
        """
        Find the root of the set that an object 'obj' is in.
        If the object was not known, will make it known, and it becomes its own set.
        Object must be Python hashable.'''
        """
        if obj not in self.objects_to_num:
            obj_num = len(self.objects_to_num)
            self.num_weights[obj_num] = 1
            self.objects_to_num[obj] = obj_num
            self.num_to_objects[obj_num] = obj
            self.parent_pointers[obj_num] = obj_num
            return obj
        stk = [self.objects_to_num[obj]]
        par = self.parent_pointers[stk[-1]]
        while par != stk[-1]:
            stk.append(par)
            par = self.parent_pointers[par]
        for i in stk:
            self.parent_pointers[i] = par
        return self.num_to_objects[par]

    def union(self, object1, object2):
        """
        Combine the sets that contain the two objects given.
        Both objects must be Python hashable.
        If either or both objects are unknown, will make them known, and combine them.
        """
        o1p = self.find(object1)
        o2p = self.find(object2)
        if o1p != o2p:
            on1 = self.objects_to_num[o1p]
            on2 = self.objects_to_num[o2p]
            w1 = self.num_weights[on1]
            w2 = self.num_weights[on2]
            if w1 < w2:
                o1p, o2p, on1, on2, w1, w2 = o2p, o1p, on2, on1, w2, w1
            self.num_weights[on1] = w1 + w2
            del self.num_weights[on2]
            self.parent_pointers[on2] = on1

    def __str__(self):
        """
        Included for testing purposes only.
        All information needed from the union find data structure can be attained
        using find.
        """
        sets = {}
        for i in range(len(self.objects_to_num)):
            sets[i] = []
        for i in self.objects_to_num:
            sets[self.objects_to_num[self.find(i)]].append(i)
        out = []
        for i in sets.itervalues():
            if i:
                out.append(repr(i))
        return ', '.join(out)

    def __call__(self, iterator):
        """
        Build unions for whole iterators of any size
        """
        self.insert_objects(tfields.lib.util.flatten(iterator))
        i = 0
        for item in iterator:
            for i1, i2 in tfields.lib.util.pairwise(item):
                self.union(i1, i2)
            i += 1

    def groups(self, iterator):
        """
        Return full groups from iterator
        """
        groups = {}
        keys = []
        for item in iterator:
            key = self.find(item[0])
            if key not in keys:
                keys.append(key)
            if key not in groups:
                groups[key] = []
            groups[key].append(item)
        return [groups[k] for k in keys]

    def group_indices(self, iterator):
        """
        Return full groups from iterator
        """
        group_indices = {}
        keys = []
        for i, item in enumerate(iterator):
            key = self.find(item[0])
            if key not in keys:
                keys.append(key)
            if key not in group_indices:
                group_indices[key] = []
            group_indices[key].append(i)
        return [group_indices[k] for k in keys]


def disjoint_groups(iterator):
    """
    Disjoint groups implementation

    Examples:
        >>> import tfields
        >>> tfields.lib.sets.disjoint_groups([[0, 0, 0, 'A'], [1, 2, 3], [3, 0],
        ...                                   [4, 4, 4], [5, 4], ['X', 0.42]])
        [[[0, 0, 0, 'A'], [1, 2, 3], [3, 0]], [[4, 4, 4], [5, 4]], [['X', 0.42]]]
        >>> tfields.lib.sets.disjoint_groups([[0], [1], [2], [3], [0, 1], [1, 2], [3, 0]])
        [[[0], [1], [2], [3], [0, 1], [1, 2], [3, 0]]]

    Returns:
        list: iterator items grouped in disjoint sets
    """
    uf = UnionFind()
    uf(iterator)
    return uf.groups(iterator)


def disjoint_group_indices(iterator):
    """
    Examples:
        >>> import tfields
        >>> tfields.lib.sets.disjoint_group_indices([[0, 0, 0, 'A'], [1, 2, 3],
        ...                                          [3, 0], [4, 4, 4], [5, 4], ['X', 0.42]])
        [[0, 1, 2], [3, 4], [5]]
        >>> tfields.lib.sets.disjoint_group_indices([[0], [1], [2], [3], [0, 1], [1, 2], [3, 0]])
        [[0, 1, 2, 3, 4, 5, 6]]

    Returns:
        list: indices of iterator items grouped in disjoint sets
    """
    uf = UnionFind()
    if isinstance(iterator, np.ndarray):
        iterator = iterator.tolist()
    uf(iterator)
    return uf.group_indices(iterator)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
