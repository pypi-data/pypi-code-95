from delft_physics_lab.delft_physics_lab.utils import *
import numpy as np
import matplotlib.pyplot as plt

def exercise1():
    m = float_input("Mass of the ball (kg): ")
    d = float_input("Diameter of the ball (m): ")
    rho = 1.184 # the density of air at 25 degrees celsius and 1 atmosphere of pressure

    v_t = terminal_velocity_sphere(m, d, rho)
    print(f"The terminal velocity fo the ball is: {v_t:.2f} m/s (or {v_t*3.6:.2f} km/h)")


def exercise2():
    m = np.linspace(.01, 10, 100) # find the terminal velocity for masses between .01 kg and 100 kg
    rho = 1.184 # the density of air at 25 degrees celsius and 1 atmosphere of pressure
    v_t = terminal_velocity_sphere(m, 1, rho) # the terminal velocities for spheres of different mass

    plt.figure()
    plt.plot(m, v_t, 'k.') # plot mass (m) against velocity (v_t)
    # labeling of the axes, dollar signs are used to print the characters in between in italics
    plt.xlabel('$m$ (kg)')
    plt.ylabel('$v$ (m/s)')
    plt.show()
