import numpy as np
from sklearn.base import BaseEstimator


def scaled_linspace(x: np.ndarray, y: np.ndarray, num: int, scaler: BaseEstimator) -> np.ndarray:
    """Generate a linspace, evenly spaced according to the normalization

        Args:
            x (np.ndarray): First point
            y (np.ndarray): Sencond point
            num (int): Number of points (in between the two points)
            method (str): Normalization method

        Returns:
            np.ndarray: Sequence of points evenly spaced
        """
    # Normalize the points
    x = scaler.transform([x])[0]
    y = scaler.transform([y])[0]

    # Generate the linspace
    ls = np.linspace(x, y, num=num + 1, endpoint=True)

    # Unnormalize the points
    ls = scaler.inverse_transform(ls)

    return ls
