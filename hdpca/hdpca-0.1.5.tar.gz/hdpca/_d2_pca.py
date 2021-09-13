import numpy as np


class D2PCA:
    @staticmethod
    def get_components_from_percentage(eigen_value, percentage):
        # sum of all eigen values
        eigen_sum = np.sum(eigen_value)
        sum_of_n_components = 0
        n_components = 0
        while sum_of_n_components < percentage * eigen_sum:
            sum_of_n_components += eigen_value[n_components]
            n_components += 1
        return n_components

    def transform(self, data):
        return np.dot(data, self.base)

    def __init__(self, n_components):
        self.n_components = n_components
        self.base = None

    def fit(self, X, y=None):
        X = np.asarray(X)
        mean = np.mean(X, 0)
        mean_subtracted = X - mean

        # line_no = X.shape[0]
        height = X.shape[2]

        # creating emptymatrix for find covarience matrix
        covarience_matrix = np.zeros((height, height))
        for i in X:
            # multiplying net subtracted image with its transpose and adding in gt
            mean_subtracted = i - mean
            covarience_matrix += np.dot(mean_subtracted.T, mean_subtracted)
        covarience_matrix /= len(X)

        # finding eigen values and eigen vectors
        d_mat, p_mat = np.linalg.eig(covarience_matrix)

        # finding first p important vectors
        if type(self.n_components) == float and 0.0 < self.n_components < 1.0:
            self.n_components = self.get_components_from_percentage(d_mat, self.n_components)
        self.base = p_mat[:, 0:self.n_components]

    def inverse_transform(self, new_coordinates):
        return np.dot(new_coordinates, self.base.T)
