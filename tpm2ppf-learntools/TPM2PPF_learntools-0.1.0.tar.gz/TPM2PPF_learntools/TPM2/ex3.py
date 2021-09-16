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

    I expect in the question the diffinitions of $V_{e,i}$ (and others) as function of $d_x$ $d_y$ the cell sizes, $\epsilon_0$, and the source therm.
    The discretisation have been shown in the presentation.

    """)  # TODO: continue the hint

    _solution = """You cannot have access to the solution !"""

    def check(self):
        raise Uncheckable



class BoundaryConditionDiscretisation(ThoughtExperiment):
    _bonus = False
    _hint = textwrap.dedent("""
    I expect in the question the deffinitions of $V_i,j$ at $i=1$, $i=N$, $j=1$, $j=M$
    as function of the parameters $U_a$ (or $U_c$) and other variables like the plasma potential in the cells nearby.

    Somethink like :

    1. Dirichlet condition: $V_1,j = U_a + V_2,j$ ... (this is wrong !!)
    2. Neumann Condition:  $V_i,1 = \log(U_c)$ (this is also wrong !!)

    """)  # TODO: continue the hint

    _solution = """You cannot have access to the solution !"""

    def check(self):
        raise Uncheckable


class MatrixDiscretisation(ThoughtExperiment):
    _bonus = False
    _hint = textwrap.dedent("""
    I expect here the details of the matrix `A`.
    
    If you can factor some parameters, please do it !

    You do not need to write all the elements of $A$. Find ways to give the most important informations
    And find a way to deals with the 2D domain.

    """)  # TODO: continue the hint

    _solution = textwrap.dedent("""
    You cannot have access to the solution !
    However, there is a second tips.
    
    You have to write a 2D Matrix, with the vectors $V$ and $d$ 1D vectors.
    Hence, you need to "unwrap" the 2D domain into a 1D vector.
    One solutions is to start by iterating over $x$, then $y$ :
    
    $$
    V = [V_{1,1}, V_{2,1}, ... V_{N,1}, V_{1,2}, V_{2,2} ... V_{N, 2}, ... V_{N-1, M}, V_{N,M}]
    $$
     """
    )

    def check(self):
        raise Uncheckable



class UsingThomas(ThoughtExperiment):
    _bonus = False
    _hint = textwrap.dedent("""
    Look at the caracteristics of the matrix $A$,
    and the conditions to use the Thomas algorythm.
    """)  # TODO: continue the hint

    _solution = textwrap.dedent("""
    The Matrix $A$ is no more Tridiagonal. So the Thomas algorythm cannot be used.
    We will use the SOR algorithm.
     """
    )

    def check(self):
        raise Uncheckable



class ExerciceSorSolver(CodingProblem):
    _vars = ['SOR', "E",  "Ve", "Vo", "Vs", "Vn", "Vc", "rho", "V", "Ua", "Uc" ]
    _hint = "You need to modify the function `SOR` that would solve the tridiagonal matrix linear equation."
    _solution = textwrap.dedent("""
    You cannot have access to the solution !

    But there is another tips :
    The `SOR` function is actually pretty simple, it is almost direct translation for the math to python
    """
    )

    def check(self, SOR, E, Ve, Vo, Vs, Vn, Vc, rho, V, Ua, Uc):

        print("Running the `SOR` function over the system, it can take some time...")

        N = 50
        M = 50
        dx = 1./N
        dy = 1./M

        eps0 = 8.85E-14   # F/cm

        # dielectric layers
        epsdiel=1    # default =1 (no dielectric)

        nxdg = 0 # Nx/10      # dielectric anode side
        nxdd = 0 # Nx/10      # dielectric cathode side       

        from tqdm.auto import tqdm

        for index in tqdm(range(1000)):
            Vact = SOR(w=1.5)

        Vslot = 0.5 * (np.linspace(Uc, Ua, N) + np.linspace(Uc, Ua, N+2)[1:-1])

        Vtheo = np.zeros( (N,M) )
        for j in range(M):
            Vtheo[:,j] = Vslot

        error = np.sum(np.abs(Vact - Vtheo))

        if False:
            import matplotlib.pyplot as plt

            plt.figure()
            plt.plot(Vact[:, 1], label="comuted")
            plt.plot(Vtheo[:, 1], label = "expected")
            plt.legend()
            plt.xlabel("$x$ axis")
            plt.ylabel("V(i, j=1) [V]")
            plt.show()

        Vact = np.zeros((N,M))  # The solution

        assert error < N*M*1, self._failure_message(error)
        


    @property
    def _correct_message(self):
        history = self._view.interactions
        return ("Congrats ! "
        "You succedded to write the SOR function to solve the Poisson Equation !")

    def _failure_message(self, error_value):
        
        return ("For some reasons, when using your function `SOR`,"
                "the answer I obtained was not the value expected !\n"
                "In particular, the total square error is : "
                "$$\sum (V - V_{{theo}}) = {}$$"
                "which is very large !"
        ).format(error_value)


def SOR_solution(w=1):
    """arguments: w between 0 and 2
    Return x a vector of the same size of a"""
    
    "Verifying that the inputs are correct"
    assert w > 0 and w < 2 , "the argument is not between 0 and 2"
    
    for i in range(N):
        for j in range(M):
            
            Vact[i, j] = (1-w)*Vact[i, j] + w * (Vo(i,j)*V(i-1, j) +
            Ve(i,j)*V(i+1, j) +
            Vs(i,j)*V(i, j-1) +
            Vn(i,j)*V(i, j+1)
            - rho(i,j)) / Vc(i,j)
            
    # Write your code here
    
    return Vact 
    

class SolvingOnce(CodingProblem):
    _var = 'Vact'
    _hint = ("Remembrer, SOR is an iterativ solver !")
    
    _solution = """You cannot have access to the solution !"""
    def check(self, Vact):

        import matplotlib.pyplot as plt
        
        N = 50
        M = 50
        Ua = 45
        Uc = 10

        Vslot = 0.5 * (np.linspace(Uc, Ua, N) + np.linspace(Uc, Ua, N+2)[1:-1])

        Vtheo = np.zeros( (N,M) )
        for j in range(M):
            Vtheo[:,j] = Vslot
        

        plt.figure(figsize=(5,3))
        plt.title("Plasma potential \n with no charge density")
        plt.ylabel("Potential at $j=1$ [V]")
        plt.xlabel("Position x [cm]")
        plt.plot(Vtheo[:, 1], label="The solution")
        plt.plot(Vact[:, 1], label="Your answer `Vact`")
        plt.legend()
        plt.tight_layout()


        error = np.sum(np.abs(Vact - Vtheo))

        assert error < N*M*1, self._failure_message(error)
        


    @property
    def _correct_message(self):
        history = self._view.interactions
        return ("Congrats ! "
        "You succedded to solve the Poisson Equation !")

    def _failure_message(self, error_value):
        
        return ("For some reasons, your solution for `V` is not good !"
                "In particular, the total square error I get is : "
                "$$\sum (V - V_{{theo}}) = {}$$"
                "which is very large !"
        ).format(error_value)


class SolvingTwice(CodingProblem):
    _var = 'Vact'
    _hint = ("Remembrer, SOR is an iterativ solver !")

    _solution = """You cannot have access to the solution !"""

    def check(self, Vact):

        import matplotlib.pyplot as plt

        N = 50  
        M = 50
        Ua = 45
        Uc = 10

        x = np.linspace(0, 1, N)

        Vslot = 0.5 * (np.linspace(Uc, Ua, N) + np.linspace(Uc, Ua, N+2)[1:-1])
        Vslot = np.linspace(Uc, Ua, N)

        Vslot +=  1e-10/8.85e-14/2 * ( x*(x - 1))  # TDO : check that this is the true Solution !!

        Vtheo = np.zeros( (N,M) )
        for j in range(M):
            Vtheo[:,j] = Vslot

        plt.figure(figsize=(5,3))
        plt.title("Plasma potential \n with uniform charge density")
        plt.ylabel("Potential at $j=1$ [V]")
        plt.xlabel("Position x [cm]")
        plt.plot(Vtheo[:, 1], label="The solution")
        plt.plot(Vact[:, 1], label="Your answer `Vact`")
        plt.legend()
        plt.tight_layout()


        error = np.sum(np.abs(Vact - Vtheo))

        assert error < N*M*2, self._failure_message(error)



    @property
    def _correct_message(self):
        history = self._view.interactions
        return ("Congrats ! "
        "You succedded to solve the Poisson Equation !")

    def _failure_message(self, error_value):

        return ("For some reasons, your solution for `V` is not good !"
                "In particular, the total square error I get is : "
                "$$\sum (V - V_{{theo}}) = {}$$"
                "which is very large !"
        ).format(error_value)
        


SORfunction = MultipartProblem(UsingThomas, ExerciceSorSolver)
SolvingSimpleCases = MultipartProblem(SolvingOnce, SolvingTwice)



qvars = bind_exercises(globals(), [
    FiniteVolumeDiscretisation,
    BoundaryConditionDiscretisation,
    MatrixDiscretisation,
    SORfunction,
    SolvingSimpleCases,
    ],
    start=1,
    )
__all__ = list(qvars)
