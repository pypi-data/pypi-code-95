# double well potential 
import numpy as np 
import torch
import jax 
import jax.numpy as jnp
from jax import jit 
import jax.random as jrd 


# numpy version of the potential
class Doublewell(object):
    # potential 0.045 x^4 - x ^2 + 0.5 y ^2 + 0.5 z ^ 2 + ...
    params_default = {'k' : 0.045,
                      'dim' : 1}

    def __init__(self, **params):
        # set parameters
        self.params = self.__class__.params_default
        self.params.update(params)

        # useful variables
        self.dim = self.params['dim']

    def energy(self, x):
        """double well potential

        Returns
        -------
        potential : {float, np.ndarray}
            Potential energy. Will be the same shape as the inputs, x and y.

        """
        x1 = x[:, 0]
        value = self.params['k'] * x1 ** 4 - x1 ** 2
        # redundant variables
        if self.dim > 1:
            value += 0.5 * np.sum(x[:, 1:] ** 2, axis=1)

        return value

    def grad(self, x):
        """gradient of Double Well potential

        Returns
        -------
        potential : {float, np.ndarray}
            Potential energy. Will be the same shape as the inputs, x and y.

        """
        x1 = x[:, 0]
        dx1 = 4 * self.params['k'] * x1 ** 3 - 2 * x1 
        dx1 = np.reshape(dx1, [-1, 1])

        out = np.concatenate([dx1, x[:, 1:]], 1)
        assert out.shape[1] == self.dim
        return out



# torch implementation 
class Doublewell_torch(object):
    # potential 0.045 x^4 - x ^2 + 0.5 y ^2 + 0.5 z ^ 2 + ...
    params_default = {'k' : 0.045,
                      'dim' : 1}

    def __init__(self, **params):
        # set parameters
        self.params = self.__class__.params_default
        self.params.update(params)

        # useful variables
        self.dim = self.params['dim']

    def energy(self, x):
        """double well potential

        Returns
        -------
        potential : {float, np.ndarray}
            Potential energy. Will be the same shape as the inputs, x and y.

        """
        x1 = x[:, 0]
        value = self.params['k'] * x1 ** 4 - x1 ** 2
        # redundant variables
        if self.dim > 1:
            value += 0.5 * torch.sum(x[:, 1:] ** 2, axis=1)

        return value

    def grad(self, x):
        """gradient of Double Well potential

        Returns
        -------
        potential : {float, np.ndarray}
            Potential energy. Will be the same shape as the inputs, x and y.

        """
        x1 = x[:, 0]
        dx1 = 4 * self.params['k'] * x1 ** 3 - 2 * x1 
        
        out = torch.cat([dx1.unsqueeze(-1), x[:, 1:]], 1)
        assert out.shape[1] == self.dim
        return out


params = {'k' : 0.045}
# TODO: Jax implementation
# TODO: better merge of the backend
@jit
def grad_potential_jnp(data):
    x = data[:, 0]
    y = data[:, 1] 
    z = data[:, 2:] 
    out = jnp.stack([4 * params['k'] * x**3 - 2 * x, y], axis=1)
    out = jnp.concatenate([out, z], axis=1)
    return out 


if __name__ == '__main__':
    # testing 
    mbp = Doublewell()
    print(mbp.dim)

    mbp = Doublewell(dim=10)
    print(mbp.dim)

    random_x = np.random.randn(2, 10)
    print(mbp.energy(random_x), mbp.grad(random_x)) 

    torch_x = torch.from_numpy(random_x)
    mbp = Doublewell_torch(dim=10)
    print(mbp.dim)
    print(mbp.energy(torch_x), mbp.grad(torch_x)) 
