from os import error
from TPM2PPF_learntools.core import *
from TPM2PPF_learntools.core.problem import injected
from TPM2PPF_learntools.core.exceptions import Uncheckable
import textwrap 

import numpy as np
from astropy.constants import eps0
eps0 = eps0.value


class FiniteVolumeDiscretisation(ThoughtExperiment):
    _bonus = False
    _hint = textwrap.dedent("""
    To answer this question, use the Latex langage for equations (you can look that the other equations in the notebooks by double-cliking on the markdown cells)

    I expect in the question the diffinitions of $V_{e,i}$ (and other) as function of $d_x$ the cell size, and XXX
    """)  # TODO: continue the hint

    _solution = """You cannot have access to the solution !"""

    def check(self):
        raise Uncheckable



class BoundaryConditionDiscretisation(ThoughtExperiment):
    _bonus = False
    _hint = textwrap.dedent("""
    I expect in the question the diffinitions of $V_1$ (and $V_N$) as function of $V_2$ or $U_a$ (or $V_{N-1}$ and $U_c$) and other variables, for the three cases

    Somethink like :

    1. Dirichlet condition: $V_1 = U_a + V_2$ ... (this is wrong !!)
    2. Neumann Condition:  $V_1 = \log(U_c)$ (this is also wrong !!)

    """)  # TODO: continue the hint

    _solution = """You cannot have access to the solution !"""

    def check(self):
        raise Uncheckable


class MatrixDiscretisation(ThoughtExperiment):
    _bonus = False
    _hint = textwrap.dedent("""
    I expect here the details of the matrix `A`.
    You can use the markdown cell bellow where a generic matrix is used.

    If you can factor some parameters, please do it !
    In addition, don't forget the boundary condition, ie the first and last lines of `A`
    """)  # TODO: continue the hint

    _solution = """You cannot have access to the solution !"""

    def check(self):
        raise Uncheckable



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

class SolvingOnce(CodingProblem):
    _var = 'V'
    _hint = ("You need to initialize the four vectors `a, b, c` and `d` "
    "to use with the function `thomas`."
    "Don't forget the boundary conditions !")
    
    _solution = """You cannot have access to the solution !"""
    def check(self, V):

        import matplotlib.pyplot as plt
        
        Ua = 10  # Anode potential in V
        Uc = 5   # Cathode potential in V
        N = 50   # Number of points that discretize the domain
        Lx = 1   # size of the domain in cm

        a = np.ones(N)
        b = np.ones(N)
        c = np.ones(N)
        d = np.zeros(N)

        b *=-2
        c[0] = 0
        b[0] = -1
        a[-1] = 0
        b[-1] = -1



        d[0] = -Ua
        d[-1] = -Uc

        V_theo = thomas_solution(a, b, c, d)
        x = np.linspace(0, 1, N)
        dx = x[1] - x[0]

        plt.figure(figsize=(5,3))
        plt.title("Plasma potential \n with no charge density")
        plt.ylabel("Potential [V]")
        plt.xlabel("Position x [cm]")
        plt.plot(x, V_theo, label="The solution")
        plt.plot(x, V, label="Your answer")
        plt.legend()
        plt.tight_layout()


        error = np.sum(np.abs(V - V_theo))

        assert np.allclose(V,V_theo), self._failure_message(error)
        


    @property
    def _correct_message(self):
        history = self._view.interactions
        return ("Congrats ! "
        "You succedded to write the Thomas method to solve the Poisson Equation !")

    def _failure_message(self, error_value):
        
        return ("For some reasons, your solution for `V` is not good !"
                "In particular, the total square error I get is : "
                "$$\sum (V - V_{{theo}}) = {}$$"
                "which is very large !"
        ).format(error_value)


class SolvingTwice(CodingProblem):
    _var = 'V'
    _hint = ("You need to initialize the four vectors `a, b, c` and `d` "
    "to use with the function `thomas`."
    "Don't forget the boundary conditions !")
    
    _solution = """You cannot have access to the solution !"""
    def check(self, V):

        import matplotlib.pyplot as plt

        Ua = 10  # Anode potential in V
        Uc = 5   # Cathode potential in V
        N = 50   # Number of points that discretize the domain
        Lx = 1   # size of the domain in cm

        a = np.ones(N)
        b = np.ones(N)
        c = np.ones(N)
        d = np.zeros(N)
        x = np.linspace(0, Lx, N)
        dx = x[1] - x[0]

        b *=-2
        c[0] = 0
        b[0] = -1
        a[-1] = 0
        b[-1] = -1

        rho = 1e-10 * np.ones(N)  # charge density in C/m³
        d = rho * dx / eps0
        d[0] = -Ua
        d[-1] = -Uc

        d[0] = -Ua
        d[-1] = -Uc

        V_theo = thomas_solution(a, b, c, d)

        plt.figure(figsize=(5,3))
        plt.title("Plasma potential \n with uniform charge density")
        plt.ylabel("Potential [V]")
        plt.xlabel("Position x [cm]")
        plt.plot(x, V_theo, label="The solution")
        plt.plot(x, V, label="Your answer")
        plt.legend()
        plt.tight_layout()


        error = np.sum(np.abs(V - V_theo))

        assert np.allclose(V,V_theo), self._failure_message(error)
        


    @property
    def _correct_message(self):
        history = self._view.interactions
        return ("Congrats ! "
        "You succedded to write the Thomas method to solve the Poisson Equation !")

    def _failure_message(self, error_value):
        
        return ("For some reasons, your solution for `V` is not good !"
                "In particular, the total square error I get is : "
                "$$\sum (V - V_{{theo}}) = {}$$"
                "which is very large !"
        ).format(error_value)
        

class ManufacturedSolution(CodingProblem):
    _vars = ['phi_theo', 'rho_theo']

    _hint = ("You need to modify the fonctions `phi_theo` and `rho_theo`, then to solve the the four vectors `a, b, c` and `d` "
    "to use with the function `thomas`."
    "Don't forget the boundary conditions !")
    
    _solution = """You cannot have access to the solution !"""
    def check(self, phi_theo, rho_theo):

        import matplotlib.pyplot as plt
        
        N = 50   # Number of points that discretize the domain
        Lx = 1   # size of the domain in cm
        x = np.linspace(0, Lx, N)
        dx = x[1] - x[0]

        phi_ref = phi_theo(x)
        Ua = phi_ref[0]  # Anode potential in V
        Uc = phi_ref[-1]   # Cathode potential in V

        a = np.ones(N)
        b = np.ones(N)
        c = np.ones(N)
        d = np.zeros(N)

        b *=-2
        c[0] = 0
        b[0] = -1
        a[-1] = 0
        b[-1] = -1

        rho = rho_theo(x)  # charge density in C/m³
        d = rho * dx / eps0
        d[0] = -Ua
        d[-1] = -Uc

        d[0] = -Ua
        d[-1] = -Uc

        V = thomas_solution(a, b, c, d)


        plt.figure(figsize=(5,3))
        plt.title("Solving the \n Manufactured solution")
        plt.ylabel("Potential [V]")
        plt.xlabel("Position x [cm]")
        plt.plot(x, phi_ref, label="The manufactured solution")
        plt.plot(x, V, label="The solution solving for  `rho_theo`")
        plt.legend()
        plt.tight_layout()

        error = np.sum(np.abs(V - phi_ref))

        assert np.allclose(V,phi_ref), self._failure_message(error)
        


    @property
    def _correct_message(self):
        history = self._view.interactions
        return ("Congrats ! ")

    def _failure_message(self, error_value):
        
        return ("For some reasons, your solution for `V` is not good !"
                "In particular, the total square error I get is : "
                "$$\sum (V - V_{{theo}}) = {}$$"
                "which is very large !"
        ).format(error_value)
        


SolvingSimpleCases = MultipartProblem(SolvingOnce, SolvingTwice)



qvars = bind_exercises(globals(), [
    FiniteVolumeDiscretisation,
    BoundaryConditionDiscretisation,
    MatrixDiscretisation,
    ExerciceThomasSolver,
    SolvingSimpleCases,
    ManufacturedSolution,
    ],
    start=1,
    )
__all__ = list(qvars)
