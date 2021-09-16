from os import error
from TPM2PPF_learntools.core import *
from TPM2PPF_learntools.core.problem import ThoughtExperiment, injected
from TPM2PPF_learntools.core.exceptions import Uncheckable
import textwrap 

import numpy as np
from astropy.constants import eps0
eps0 = eps0.value




def tridiag(a, b, c, k1=-1, k2=0, k3=1):
    """Return a tridiagonal matrix """
    return np.diag(a[1:], k1) + np.diag(b, k2) + np.diag(c[:-1], k3)



class ExerciceThomasSolver(CodingProblem):
    _var = 'thomas'
    _hint = "You need to modify the function `thomas` that would solve the tridiagonal matrix linear equation."
    _solution = """You cannot have access to the solution !"""
    def check(self, thomas):

        N = 40
        a, b, c, xtheo = [ np.random.rand(N) for i in range(4)]
        A = tridiag(a, b, c)
        d = A.dot(xtheo)

        x = thomas(a, b, c, d)
        error = np.sum(np.abs(x - xtheo))
        assert np.allclose(x,xtheo), self._failure_message(error)
        


    @property
    def _correct_message(self):
        history = self._view.interactions
        return ("Congrats ! "
        "You succedded to write the Thomas method to solve the Poisson Equation !")

    def _failure_message(self, error_value):
        
        return ("For some reasons, when using your function `thomas`,"
                "the answer I obtained was not the value expected !\n"
                "In particular, the total square error is : "
                "$$\sum (V - V_{{theo}}) = {}$$"
                "which is very large !"
        ).format(error_value)


def thomas_solution(a, b, c, d):
    """arguments: a,b,c and d, four vector of same size
    Return x a vector of the same size of a"""
    
    N = len(a)
    "Verifying that the inputs are correct"
    assert len(b)== N and len(c) == N and len(d) == N, "the arguments are not of the same lenght"
    
    V = np.zeros_like(a)
    
    cprim = np.zeros_like(a)
    dprim = np.zeros_like(a)

    cprim[0] = c[0] / b[0]

    for i in range(1, N):
        cprim[i] = c[i]/(b[i] - a[i] * cprim[i-1])
    
    dprim[0] = d[0]/b[0]

    for i in range(1, N):
        dprim[i] = (d[i] - a[i]*dprim[i-1])/(b[i] - a[i]*cprim[i-1])

    V[-1] = dprim[-1]

    for i in range(N-2, -1, -1):
        V[i] = dprim[i] - cprim[i] * V[i+1]

    return V


class performance1(ThoughtExperiment):
    _bonus = False
    _hint =  textwrap.dedent("""
    Use this kind of formulation :
     ```
    import time
    start_time = time.time()
    x = thomas(a, b, c, d)
    stop_time = time.time()
    ```
    
    You can measure the time several times to obtaine an average !
    """)  # TODO: continue the hint

    _solution = CS("""
    def time_thomas(N, N_measure=5):
    import time
    times = np.zeros(N_measure)
    
    for idx_measure in range(N_measure):
       a, b, c, d = [ np.random.rand(N) for i in range(4)]

        start_time = time.time()
        x = thomas(a, b, c, d)
        stop_time = time.time()

        times[idx_measure] = (stop_time - start_time)

    return times.mean(), times.std()"""
    )

    def check(self):
        raise Uncheckable


class performance2(ThoughtExperiment):
    _bonus = False
    _hint = ("First, generate an list with the values of $N$."
    "Then, loop over the list and use the function defined before"
    )  # TODO: continue the hint

    _solution = textwrap.dedent("""
    There is the results for my computer :"
    ```
    N_list = [50, 100, 500, 1000, 2000, 5000, 10000, 20_000, 50_000, 100_000, 200_000]
    perf_N = [3.3e-4, 3.8e-4, 2e-3, 3.8e-3, 8.4e-3, 1.9e-2, 3.6e-2, 7e-2, 1.5e-1, 3.2e-1, 6.3e-1]
    ```
    """)

    def check(self):
        raise Uncheckable

class performance3(ThoughtExperiment):
    _bonus = False
    _hint = ("Here, comments the evolution of the time with $N$ : does is increase ? If yes how ? Is the behavior expected ?") 

    _solution = ("No solution evailable"
    )

    def check(self):
        raise Uncheckable



Complexites = MultipartProblem(performance1, performance2, performance3)



class precision1(ThoughtExperiment):
    _bonus = False
    _hint =  textwrap.dedent("""
    You need to compare the obtained results with a reference !
    
    The reference could be an analytic solution (see the manufactured solution aproched) 
    """)  # TODO: continue the hint

    _solution = "No solutions are available"

    def check(self):
        raise Uncheckable


Precisions = MultipartProblem(precision1)


class UsingLibsSolve(ThoughtExperiment):
    _bonus = False
    _hint =  textwrap.dedent("""
    You need to start by importing the function, with 
    ```
    from scipy.linalg import solve
    ```

    """) 

    _solution = "No solutions are available"

    def check(self):
        raise Uncheckable



qvars = bind_exercises(globals(), [
    ExerciceThomasSolver,
    Complexites,
    Precisions,
    UsingLibsSolve
    ],
    start=0,
    )
__all__ = list(qvars)
