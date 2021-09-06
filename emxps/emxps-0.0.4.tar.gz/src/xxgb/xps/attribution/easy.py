import numpy as np

from .api import BaseExplainer


class EasyFA(BaseExplainer):
    def __init__(self, trees, distribute=False):
        self.trees = trees
        self.distribute = distribute

    def shap_values(self, X):
        fa = np.zeros(X.shape)
        for i, x in enumerate(X):
            for tree in self.trees:
                path = tree.predict(x, path=True)
                for atom in path:
                    if self.distribute:
                        fa[i][atom.feature.idx] += path.weight / len(path)
                    else:
                        fa[i][atom.feature.idx] += path.weight
        return fa