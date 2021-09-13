import numpy as np
import matplotlib.pyplot as plt
from AI import mean_squared_error

class LinearRegression:

    def fit(self, X, y):
        self.X = np.array(X)
        self.y = np.array(y)
        X, y = self.X, self.y

        if len(X.shape) == 1 or X.shape[1:] == np.ones(X.shape[1:]).all():
            # Least Square Error (minimizes mean square error)
            self.coeffs = ((np.mean(X) * np.mean(y) - np.mean(X*y)) / ((np.mean(X)**2) - np.mean(X**2)))
            self.b = np.mean(y) - self.coeffs * np.mean(X)
            self.uni_dim = True
        else:
            self.coeffs = np.linalg.inv(X.T @ X) @ X.T @ y
            self.b = np.mean(y) - np.mean(X, axis=0) @ self.coeffs
            self.uni_dim = False
    
    def coef_(self):
        return self.coeffs
    
    def intercept_(self):
        return self.b

    def predict(self, X = None):
        if X is None: X = self.X

        if self.uni_dim: self.y_pred = X * self.coeffs + self.b
        else: self.y_pred = X @ self.coeffs + self.b
        return self.y_pred
    
    def mse(self, y_real = None, y_pred = None):
        if y_real is None: y_real = self.y
        if y_pred is None: y_pred = self.y_pred
        return mean_squared_error(y_real, y_pred)

    def plot(self, show = True, delimeters = False):
        if self.uni_dim:
            plt.title('Simple Linear Regression')
            plt.ylim(min(self.y), max(self.y))
            plt.plot(self.X, self.y_pred)
            plt.scatter(self.X, self.y, c='#325aa8')
            if show: plt.show()

        elif self.X.shape[1] == 2:
            plt.title('Multiple Linear Regression')
            ax = plt.axes(projection = '3d')

            min_x = np.min(self.X, axis = 0)
            max_x = np.max(self.X, axis = 0)

            x_axis = np.array([min_x[0],max_x[0]])
            y_axis = np.array([min_x[1],max_x[1]])

            x1, x2 = np.meshgrid(x_axis, y_axis)
            y = x1 * self.coeffs[0] + x2 * self.coeffs[1] + self.b

            ax.plot_surface(x1, x2, y, color = 'royalblue', alpha = 0.5)
            ax.scatter(self.X[:, 0], self.X[:, 1], self.y, c = 'lightcoral')
            if delimeters: ax.scatter(x1, x2, y, c = 'royalblue', alpha = 0.5)
            if show: plt.show()

def main():
    x = np.random.rand(1000) * 4 -2
    y = np.random.rand(1000) * 4 -2 
    X = np.array([x, y]).T

    Y = x * np.exp(-x**2 - y**2)
    
    MLR = LinearRegression()
    MLR.fit(X, Y)
    y_pred = MLR.predict()
    MLR.plot()
    print('Error: ', MLR.mse())

if __name__ == '__main__':
    main()