from delft_physics_lab.delft_physics_lab.utils import *


def exercise1():
    steps_taken, error, pi_estimation = EstimatePi.arctan_method(desired_accuracy=1e-6)
    print(f"It took {steps_taken} steps to reach an error of {error:.8f}, with an estimation for pi of {pi_estimation:.8f}.")



def exercise2():
    error, pi_estimation = EstimatePi.monte_carlo_simulation(int(1e8))
    print(f"The value of pi that was found was {pi_estimation:.6f}, this deviates {error:.6f} from the true value of pi.")


def exercise3():
    fibo_sequence = fibonacci_sequence(20)
    for i in range(2, 21):
        print(f"The fibonacci number at position {i} is {fibo_sequence[i]}")
