from dataclasses import dataclass
from typing import Iterable

from emutils.utils import get_leaves, get_roots

import numpy as np
import networkx as nx

from xxgb.monotonefeature import Feature, LESS, MORE

EPSILON = 1e-6


@dataclass
class Atom:
    """A logical atom:  [feature] [sign] [value], e.g. 'income < 50.6'

    Args:
        feature (Feature): left-hand side of the atom
        value : right-hand side of the atom
        weight : sign of the atom/atom
    """

    feature: Feature
    value: float
    sign: str

    def f(self, x):
        return (x[self.feature.idx] < self.value) if self.sign == LESS else (x[self.feature.idx] > self.value)

    def in_counter_trend(self, pred):
        if pred == 0:
            return ((self.feature.trend == -1) and (self.sign == LESS)) or \
                ((self.feature.trend == 1) and (self.sign == MORE))
        elif pred == 1:
            return ((self.feature.trend == -1) and (self.sign == MORE)) or \
                ((self.feature.trend == 1) and (self.sign == LESS))
        else:
            raise NotImplementedError('Invalid prediction. Only 0 or 1 supported (binary prediction).')

    def __repr__(self):
        return f"{self.feature.name} {self.sign} {self.value}"

    def __str__(self):
        return self.__repr__()

    def __lt__(self, other):
        """
            Total order
            A < B iff A is more less general than B, or on other words
            A < B iff A is more stringent than B, or in other words again
            A < B iff the semi-infinite interval A is smaller than the semi-infinite interval B
            e.g., (x <= 1) < (x<=7), and  (x > 9) < (x > 7)
        """
        if self.feature.idx == other.feature.idx:
            if self.sign == MORE:
                return self.value > other.value
            else:
                return self.value < other.value
        else:
            return self.feature.idx < other.feature.idx

    def __eq__(self, other: 'Atom'):
        return (self.feature == other.feature) and (self.value == other.value) and (self.sign == other.sign)

    def __hash__(self):
        return hash((self.feature.idx, self.value, self.sign))

    def __contains__(self, other):
        if self.feature != other.feature:
            return False
        if ((self.sign == LESS) and (other.sign == LESS) and (self.value >= other.value)) or \
                ((self.sign == MORE) and (other.sign == MORE) and (self.value <= other.value)):
            return True
        else:
            return False

    def __enforce(self, x):
        if self.f(x):
            return self.value
        else:
            if self.sign == LESS:
                return self.value - EPSILON
            elif self.sign == MORE:
                return self.value + EPSILON
            else:
                raise ValueError('Invalid sign! Must be in ', [LESS, MORE])

    def enforce_satisfaction(self, x, inplace: bool = True):
        if not inplace:
            x = x.copy()
        x[self.feature.idx] = self.__enforce(x)
        return x

    def dist(self, x, relative=False):
        return self.__enforce(x) - self.value


@dataclass
class Path(list):
    """A path/rule in a tree (as a list of atoms), more in general it represent a conjuction of atoms

    Args:
        self : List of atoms in the conjunction
        cover : (optional) the cover of the path/conjuction (in the tree)
        weight : (optional) weight of the path/conjuction
    """
    def __init__(
        self,
        atoms: Iterable[Atom] = None,
        cover: int = None,
        weight: float = None,
        unsafe: bool = False,
    ):
        if atoms is not None:
            if unsafe:
                super().__init__(atoms)
            else:
                super().__init__()
                for atom in atoms:
                    self.append(atom)
        else:
            super().__init__()

        self.cover = cover
        self.weight = weight
        self.sorted = False

    def __repr__(self):
        s = " AND ".join([r.__repr__() for r in self])
        if self.weight is not None:
            s += ' => ' + str(self.weight)
        return s

    def __str__(self):
        return self.__repr__()

    def fs(self, x):
        return [r.f(x) for r in self]

    def f(self, x):
        return all(self.fs(x))

    def __sub__(self, other: 'Path'):
        return [atom for atom in self if atom not in other]

    def __eq__(self, other: 'Path'):
        # Note: this is not efficient, it's O(n^2), if atoms are sorted in each path the comparison can be done in O(n)
        if len(self) != len(other):
            return False
        return all([self.__contains__(atom) for atom in other])

    def __contains__(self, atom: Atom):
        for a in self:
            if a == atom:
                return True
        return False

    def isstronger(self, other):
        if not self.sorted:
            raise ValueError('Path must be sorted to ')
        lenght = len(self)

        # Early stop
        if lenght < len(other):
            return False

        def __search_from(start, f):
            for a in range(start, lenght):
                if f == self[a].feature.idx:
                    return a + 1, self[a]
            return lenght, None

        start = 0
        # For each of the atom in other
        # there must exist an atom in self for the same feature
        # that is at least as stringent
        for atom in other:
            start, el = __search_from(start, atom.feature.idx)
            if el is None:
                return False
            if atom < el:
                return False
        return True

    def append(self, new_atom):
        self.sorted = False
        # Add only if more specific (less general atom)
        for a in range(len(self)):
            if self[a].feature.idx == new_atom.feature.idx:
                if new_atom < self[a]:
                    self[a] = new_atom
                return None
        return super().append(new_atom)

    def sort(self):
        super().sort()
        self.sorted = True

    def __add__(self, other: 'Path'):
        return Path(atoms=super().__add__(other), cover=self.cover + other.cover, weight=self.weight + other.weight)

    def as_dict(self):
        return {
            'atom': self.__str__(),
            'weight': self.weight,
            'cover': self.cover,
        }

    def __hash__(self):
        return hash(tuple([hash(atom) for atom in self]))

    def enforce_satisfaction(self, x):
        x_prime = x.copy()
        for atom in self:
            x_prime = atom.enforce_satisfaction(x_prime, inplace=True)
        return x_prime

    def in_counter_trend(self, pred):
        return np.all([atom.in_counter_trend(pred) for atom in self])

    def filter_nonviolated(self, x):
        return Path(atoms=[atom for atom in self if not atom.f(x)], weight=self.weight, cover=self.cover, unsafe=True)


class Tree(list):
    def __init__(self, T, features):
        super().__init__()

        self.T = T
        self.features = features

        # Add atoms to nodes
        for node in self.T.nodes:
            if node != self.root():
                # Get the parent of the node
                parent = list(T.predecessors(node))
                assert len(parent) == 1
                parent = parent[0]

                # Add atom object to the node
                self.T.nodes[node]['atom'] = Atom(
                    feature=features[int(T.nodes[parent]['#'])],
                    value=T.nodes[parent]['Split'],
                    sign=LESS if T.nodes[parent]['Yes'] == node else MORE
                )

        # Enumerate Paths
        for leaf in get_leaves(T):
            path = list(nx.algorithms.shortest_path(T, self.root(), leaf))
            self.append(
                Path(
                    # Weight of the atom
                    weight=T.nodes[leaf]['Gain'],
                    cover=T.nodes[leaf]['Cover'],
                    atoms=[self.T.nodes[n]['atom'] for n in path[1:]]
                )
            )

    def root(self):
        return next(get_roots(self.T))

    def predict(self, x, path=False):
        # Root
        curkey = list(self.T.nodes.keys())[0]
        curnode = self.T.nodes[curkey]
        history = [curkey]

        # Navigate the tree to the right leaf
        while not np.isnan(curnode['Split']):
            if x[int(curnode['#'])] < curnode['Split']:
                curkey = curnode['Yes']
            else:
                curkey = curnode['No']
            curnode = self.T.nodes[curkey]
            history.append(curkey)

        # Return the result
        if path:
            return Path(
                atoms=[self.T.nodes[n]['atom'] for n in history[1:]],
                weight=curnode['Gain'],
                cover=curnode['Cover'],
            )
        else:
            return curnode['Gain']

    def relevant_tweaks(self, x, pred, monotonic=True):
        # Get current value
        curval = self.predict(x)
        # If class=0, I want to increase the pre-sigmoid output
        # If class=1, I want to decrease the pre-sigmoid output
        if pred == 0:
            rules = [path for path in self if path.weight > curval]
        elif pred == 1:
            rules = [path for path in self if path.weight < curval]
        else:
            raise NotImplementedError('Support only logistic output.')

        rules = list(map(lambda rule: rule.filter_nonviolated(x), rules))
        if monotonic:
            rules = [rule for rule in rules if rule.in_counter_trend(pred)]

        return [FeatureTweak(rule, x, tree_delta=rule.weight - curval) for rule in rules]


@dataclass
class FeatureTweak:
    def __init__(self, rule: Path, x: np.ndarray, tree_delta: float):
        self.rule = rule
        self.x = x
        self.x_prime = self.rule.enforce_satisfaction(x)

        self.tree_delta = tree_delta

        self.delta = None
        self.margin_delta = None
        self.effective = None

    def set(self, **kwargs):
        self.__dict__.update(kwargs)

    def __repr__(self):
        s = str(self.rule) if 'rule' in self.__dict__ else str(self.path)
        if self.tree_delta is not None:
            s += f' / Δtree = {self.tree_delta}'
        if self.delta is not None:
            s += f' / Δmodel = {self.delta}'
        return s

    def __str__(self):
        return self.__repr__()

    def to_dict(self):
        return dict(
            local_delta=self.tree_delta,
            global_delta=self.delta,
            margin_delta=self.margin_delta,
            effective=self.effective,
            x_prime=self.x_prime,
        )

    def debug_dict(self):
        return dict(
            local_delta=self.tree_delta,
            global_delta=self.delta,
            margin_delta=self.margin_delta if 'margin_delta' in self.__dict__ else None,
            effective=self.effective,
        )

    def __add__(self, other: 'FeatureTweak'):
        return FeatureTweak(rule=self.rule + other.rule, tree_delta=self.tree_delta + other.tree_delta, x=self.x)
