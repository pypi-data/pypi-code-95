from .utils import *
from datetime import datetime


def exercise1():
    m = float_input("Mass of the ball (kg): ") # request the user for input through IPython or the commandline
    d = float_input("Diameter of the ball (m): ")
    rho = 1.184 # the density of air at 25 degrees celsius and 1 atmosphere of pressure

    v_t = terminal_velocity_sphere(m, d, rho)
    print(f"The terminal velocity fo the ball is: {v_t:.2f} m/s (or {v_t*3.6:.2f} km/h)")


def exercise2():
    x_coordinate = float_input("Please give an x-coordinate: ")
    y_coordinate = float_input("Please give an y-coordinate: ")

    radius, angle = cartesion_to_polar(x_coordinate, y_coordinate)

    print(f"The polar coordinate version of your point ({x_coordinate:.2f}, {y_coordinate:.2f}) is ({radius:.2f}, {angle:.2f})")


def exercise3():
    def f(x):
        return .25*x**2

    start = datetime.now()
    for i in range(int(1e6)):
        f(i)

    end = datetime.now() - start

    print(f"The time it took to run this loop was {end.total_seconds():.4f} seconds.")