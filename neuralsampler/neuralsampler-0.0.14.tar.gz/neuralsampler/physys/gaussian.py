# gaussian potential 
import numpy as np 
import torch
import jax 
import jax.numpy as jnp
from jax import jit 
import jax.random as jrd 

# numpy version of the potential
class Gaussian(object):
    # potential 0.5 * x ^2 + 0.5 y ^2 + 0.5 z ^ 2 + ...
    params_default = {'dim' : 1}

    def __init__(self, **params):
        # set parameters
        self.params = self.__class__.params_default
        self.params.update(params)

        # useful variables
        self.dim = self.params['dim']

    def energy(self, x):
        """gaussian potential

        Returns
        -------
        potential : {float, np.ndarray}
            Potential energy. Will be the same shape as the inputs, x and y.

        """
        value = 0.5 * np.sum(x ** 2, axis=1)
        return value

    def grad(self, x):
        """gradient of gaussian potential

        Returns
        -------
        potential : {float, np.ndarray}
            Potential energy. Will be the same shape as the inputs, x and y.

        """
        assert x.shape[1] == self.dim
        return x



# torch implementation 
class Gaussian_torch(object):
    # potential 0.5 * x ^2 + 0.5 y ^2 + 0.5 z ^ 2 + ...
    params_default = {'dim' : 1}

    def __init__(self, **params):
        # set parameters
        self.params = self.__class__.params_default
        self.params.update(params)

        # useful variables
        self.dim = self.params['dim']

    def energy(self, x):
        """gaussian potential

        Returns
        -------
        potential : {float, np.ndarray}
            Potential energy. Will be the same shape as the inputs, x and y.

        """
        value = 0.5 * torch.sum(x ** 2, axis=1)
        return value

    def grad(self, x):
        """gradient of gaussian potential

        Returns
        -------
        potential : {float, np.ndarray}
            Potential energy. Will be the same shape as the inputs, x and y.

        """
        assert x.shape[1] == self.dim
        return x

# TODO: Jax implementation
# TODO: better merge of the backend
@jit
def grad_potential_jnp(data):
    return data 

if __name__ == '__main__':
    # testing 
    mbp = Gaussian()
    print(mbp.dim)

    mbp = Gaussian(dim=10)
    print(mbp.dim)

    random_x = np.random.randn(2, 10)
    print(mbp.energy(random_x), mbp.grad(random_x)) 

    torch_x = torch.from_numpy(random_x)
    mbp = Gaussian_torch(dim=10)
    print(mbp.dim)
    print(mbp.energy(torch_x), mbp.grad(torch_x)) 
