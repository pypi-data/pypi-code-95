import numpy as np
from hdpca._d2_pca import D2PCA


class D2SquarePCA:

    def fit(self, X):
        X = np.asarray(X)
        mean = np.mean(X, 0)

        line_no = X.shape[0]
        height = X.shape[1]
        width = X.shape[2]
        row_covarience_matrix = np.zeros((width, width))
        column_covarience_matrix = np.zeros((height, height))

        for i in range(line_no):
            mean_subtracted = X[i] - mean
            row_covarience_matrix += np.dot(mean_subtracted.T, mean_subtracted)
            column_covarience_matrix += np.dot(mean_subtracted, mean_subtracted.T)

        row_covarience_matrix /= line_no
        column_covarience_matrix /= line_no

        d_mat, p_mat = np.linalg.eig(row_covarience_matrix)
        if type(self.n_components) == float and 0.0 < self.n_components < 1.0:
            self.n_components = D2PCA.get_components_from_percentage(d_mat, self.n_components)
        self.bases_row = p_mat[:, 0:self.n_components]

        d_mat, p_mat = np.linalg.eig(column_covarience_matrix)
        if type(self.n_components_2) == float and 0.0 < self.n_components_2 < 1.0:
            self.n_components_2 = D2PCA.get_components_from_percentage(d_mat, self.n_components_2)
        self.bases_column = p_mat[:, 0:self.n_components_2]

    def transform(self, data):
        temp = np.dot(data, self.bases_row)
        if len(data.shape) == 2:
            transform_data = np.dot(self.bases_column.T, temp)
        else:
            line_no = data.shape[0]
            transform_data = np.zeros((line_no, self.n_components_2, self.n_components))
            for i in range(line_no):
                transform_data[i, :, :] = np.dot(self.bases_column.T, temp[i])
        return transform_data

    def __init__(self, n_components, n_components_2=None):
        if n_components_2 is None:
            self.n_components_2 = n_components
        self.n_components = n_components
        self.bases_row = None
        self.bases_column = None

    def inverse_transform(self, new_coordinates):
        return np.dot(self.bases_column, np.dot(new_coordinates, self.bases_row.T))
