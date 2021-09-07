import jax.numpy as jnp
from emlp.reps import Rep,vis,V,equivariance_error
from emlp.groups import SO,S
import emlp
from emlp.reps import V,T,Rep
from emlp.groups import Z,S,SO,Group
import numpy as np


class SO2Irreps(Rep):
    """ (Real) Irreducible representations of SO2 """
    def __init__(self,order):
        assert order>0, "Use Scalar for 𝜓₀"
        self.G=SO(2)
        self.order = order
    def rho(self,M):
        return jnp.linalg.matrix_power(M,self.order)
    def __str__(self):
        number2sub = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
        return f"𝜓{self.order}".translate(number2sub)


class PseudoScalar(Rep):
    def __init__(self,G=None):
        self.G=G
    def __str__(self):
        return "P"
    def rho(self,M):
        sign = jnp.linalg.slogdet(M@jnp.eye(M.shape[0]))[0]
        return sign*jnp.eye(1)
    def __call__(self,G):
        return PseudoScalar(G)




class ProductSubRep(Rep):
    def __init__(self,G,subgroup_id,size):
        """   Produces the representation of the subgroup of G = G1 x G2
              with the index subgroup_id in {0,1} specifying G1 or G2.
              Also requires specifying the size of the representation given by G1.d or G2.d """
        self.G = G
        self.index = subgroup_id
        self._size = size
    def __str__(self):
        return "V_"+str(self.G).split('x')[self.index]
    def size(self):
        return self._size
    def rho(self,M): 
        # Given that M is a LazyKron object, we can just get the argument
        return M.Ms[self.index]
    def drho(self,A):
        return A.Ms[self.index]
    def __call__(self,G):
        # adding this will probably not be necessary in a future release,
        # necessary now because rep is __call__ed in nn.EMLP constructor
        assert self.G==G
        return self