import numpy as np
from scipy import constants
from typing import Tuple, List
from math import degrees, atan

pi = constants.pi  # define pi, the ratio of the circumference of a circle to its diameter
g = constants.g    # define the gravitational acceleration on earth, in ms^-2


def terminal_velocity(m: float, A: float, rho: float, c_d: float, g: float = g) -> float:
    """
    Calculate the terminal velocity of an object, given its mass (m), its surface area (A),
    the density of the substance it travels through (rho), the drag coefficient (c_d) and the gravitational acceleration

    :param m: mass of the object in kg
    :param A: surface area of the object in m^2
    :param rho: density of the medium in kgm^-3
    :param c_d: drag coefficient of the object
    :param g: gravitational acceleration of the object in ms^-2
    :return: the terminal velocity in m/s
    """
    return (2*m*g/(rho*A*c_d))**.5


def terminal_velocity_sphere(m: float, d: float, rho: float, g: float = g) -> float:
    """
    Calculate the terminal velocity of a perfect sphere, given its mass (m), its surface diameter (D),
    the density of the substance it travels through (rho), and the gravitational acceleration

    :param m: mass of the sphere in kg
    :param d: diameter of the sphere in m^2
    :param rho: density of the medium in kgm^-3
    :param g: gravitational acceleration of the sphere in ms^-2
    :return: the terminal velocity in m/s
    """
    c_d = .47
    r = d/2
    A = r**2 * pi
    return terminal_velocity(m, A, rho, c_d, g)


def float_input(_prompt: str = '') -> float:
    """Return the input as a float"""
    return float(input(_prompt))


def cartesion_to_polar(x: float, y: float) -> Tuple[float, float]:
    """Turn cartesian coordinates into polar coordinates"""

    radius = (x ** 2 + y ** 2) ** .5

    if x < 0:
        angle = degrees(atan(y / x)) + 180.
    elif x == 0:
        angle = 90. if y >= 0 else 270.
    else:
        angle = degrees(atan(y / x))

    angle = angle
    return radius, angle


def fibonacci_sequence(n) -> List[int]:
    """Generate n+1 terms of the fibonacci sequence"""
    fibo_sequence = [0, 1]
    a, b = fibo_sequence
    for i in range(2, n+1):
        a, b = b, a + b
        fibo_sequence += [b]
    return fibo_sequence


class EstimatePi:

    @staticmethod
    def arctan_method(desired_accuracy: float = None, max_n: int = None) -> Tuple[int, float, float]:
        """
        Use the arctan method to approximate pi, either to a desired accuracy, or an n number of steps

        :returns number of steps taken, distance from the true value of pi, and the found value of pi
        """

        if desired_accuracy is not None:
            stop_condition = lambda accuracy, n, desired_accuracy, max_n: accuracy < desired_accuracy
        elif max_n is not None:
            stop_condition = lambda accuracy, n, desired_accuracy, max_n: n >= max_n
        else:
            return 0, pi, 0.


        s = 0
        n = 0
        while not stop_condition(abs(pi - s), n, desired_accuracy, max_n):
            s += (-1)**n * 4 / (2*n + 1)
            n += 1

        return n, abs(pi - s), s


    @staticmethod
    def monte_carlo_simulation(max_n: int) -> Tuple[float, float]:
        """
        Estimate pi by seeing if randomly distributed points fall within the unit circle

        :param max_n: number of points sampled
        :return: the error, and the estimation of pi according to our method
        """
        coords = np.random.uniform(-1, 1, (2, max_n))
        d = np.sum(coords**2, axis=0)**.5 # using the pythagorean theorem to calculate the distance to the origin

        n_points_in_circle = np.count_nonzero(d <= 1)
        fraction_covered_by_circle = n_points_in_circle / max_n

        pi_estimation = fraction_covered_by_circle * 4

        error = abs(pi_estimation - pi)

        return error, pi_estimation