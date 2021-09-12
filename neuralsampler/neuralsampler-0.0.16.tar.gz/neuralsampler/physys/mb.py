import numpy as np 
import torch
import jax 
import jax.numpy as jnp
from jax import jit 
import jax.random as jrd 

# numpy version of the potential
class MuellerPotential(object):

    params_default = {'k' : 1.0 / 100,
                      'dim' : 2}


    aa = [-1, -1, -6.5, 0.7]
    bb = [0, 0, 11, 0.6]
    cc = [-10, -10, -6.5, 0.7]
    AA = [-200, -100, -170, 15]
    XX = [1, 0, -0.5, -1]
    YY = [0, 0.5, 1.5, 1]

    def __init__(self, **params):
        # set parameters
        self.params = self.__class__.params_default
        self.params.update(params)

        # useful variables
        self.dim = self.params['dim']

    def energy(self, x):
        """Muller potential

        Returns
        -------
        potential : {float, np.ndarray}
            Potential energy. Will be the same shape as the inputs, x and y.

        Reference
        ---------
        Code adapted from https://cims.nyu.edu/~eve2/ztsMueller.m
        """
        x1 = x[:, 0]
        x2 = x[:, 1]
        value = 0
        for j in range(0, 4):
            value += self.AA[j] * np.exp(self.aa[j] * (x1 - self.XX[j])**2 +
                                         self.bb[j] * (x1 - self.XX[j]) * (x2 - self.YY[j]) +
                                         self.cc[j] * (x2 - self.YY[j])**2)
        # redundant variables
        if self.dim > 2:
            value += 0.5 * np.sum(x[:, 2:] ** 2, axis=1)

        return self.params['k'] * value

    def grad(self, x):
        """gradient of Muller potential

        Returns
        -------
        potential : {float, np.ndarray}
            Potential energy. Will be the same shape as the inputs, x and y.

        Reference
        ---------
        Code adapted from https://cims.nyu.edu/~eve2/ztsMueller.m
        """
        x1 = x[:, 0]
        x2 = x[:, 1]
        dx1 = 0
        dx2 = 0

        for j in range(0, 4):
            middle_val = np.exp(self.aa[j] * (x1 - self.XX[j])**2 +
                                         self.bb[j] * (x1 - self.XX[j]) * (x2 - self.YY[j]) +
                                         self.cc[j] * (x2 - self.YY[j])**2)
            dx1 += self.AA[j] * middle_val * ( 2 * self.aa[j] * ( x1 - self.XX[j] ) + self.bb[j] * (x2 - self.YY[j]) )
            dx2 += self.AA[j] * middle_val * ( 2 * self.cc[j] * ( x2 - self.YY[j] ) + self.bb[j] * (x1 - self.XX[j]) )
            

        out = np.stack([dx1, dx2], 1)
        out = np.concatenate([out, x[:, 2:]], 1)
        assert out.shape[1] == self.dim

        return self.params['k'] * out



# torch implementation 
class MuellerPotential_torch(object):

    params_default = {'k' : 1.0 / 100,
                      'dim' : 2}


    aa = [-1, -1, -6.5, 0.7]
    bb = [0, 0, 11, 0.6]
    cc = [-10, -10, -6.5, 0.7]
    AA = [-200, -100, -170, 15]
    XX = [1, 0, -0.5, -1]
    YY = [0, 0.5, 1.5, 1]

    def __init__(self, **params):
        # set parameters
        self.params = self.__class__.params_default
        self.params.update(params)

        # useful variables
        self.dim = self.params['dim']

    def energy(self, x):
        """Muller potential

        Returns
        -------
        potential : {float, np.ndarray}
            Potential energy. Will be the same shape as the inputs, x and y.

        Reference
        ---------
        Code adapted from https://cims.nyu.edu/~eve2/ztsMueller.m
        """
        x1 = x[:, 0]
        x2 = x[:, 1]
        value = 0
        for j in range(0, 4):
            value += self.AA[j] * torch.exp(self.aa[j] * (x1 - self.XX[j])**2 +
                                         self.bb[j] * (x1 - self.XX[j]) * (x2 - self.YY[j]) +
                                         self.cc[j] * (x2 - self.YY[j])**2)
        # redundant variables
        if self.dim > 2:
            value += 0.5 * torch.sum(x[:, 2:] ** 2, axis=1)

        return self.params['k'] * value

    def grad(self, x):
        """gradient of Muller potential

        Returns
        -------
        potential : {float, np.ndarray}
            Potential energy. Will be the same shape as the inputs, x and y.

        Reference
        ---------
        Code adapted from https://cims.nyu.edu/~eve2/ztsMueller.m
        """
        x1 = x[:, 0]
        x2 = x[:, 1]
        dx1 = 0
        dx2 = 0

        for j in range(0, 4):
            middle_val = torch.exp(self.aa[j] * (x1 - self.XX[j])**2 +
                                         self.bb[j] * (x1 - self.XX[j]) * (x2 - self.YY[j]) +
                                         self.cc[j] * (x2 - self.YY[j])**2)
            dx1 += self.AA[j] * middle_val * ( 2 * self.aa[j] * ( x1 - self.XX[j] ) + self.bb[j] * (x2 - self.YY[j]) )
            dx2 += self.AA[j] * middle_val * ( 2 * self.cc[j] * ( x2 - self.YY[j] ) + self.bb[j] * (x1 - self.XX[j]) )
            

        out = torch.stack([dx1, dx2], 1)
        out = torch.cat([out, x[:, 2:]], 1)
        assert out.shape[1] == self.dim

        return self.params['k'] * out



# TODO: Jax implementation
# TODO: better merge of the backend


params = {'k' : 1.0 / 100}

aa = [-1, -1, -6.5, 0.7]
bb = [0, 0, 11, 0.6]
cc = [-10, -10, -6.5, 0.7]
AA = [-200, -100, -170, 15]
XX = [1, 0, -0.5, -1]
YY = [0, 0.5, 1.5, 1]

@jit
def mbp_grad_jnp(x):

    x1 = x[:, 0]
    x2 = x[:, 1]
    dx1 = 0
    dx2 = 0

    for j in range(0, 4):
        middle_val = jnp.exp(aa[j] * (x1 - XX[j])**2 +
                                        bb[j] * (x1 - XX[j]) * (x2 - YY[j]) +
                                        cc[j] * (x2 - YY[j])**2)
        dx1 += AA[j] * middle_val * ( 2 * aa[j] * ( x1 - XX[j] ) + bb[j] * (x2 - YY[j]) )
        dx2 += AA[j] * middle_val * ( 2 * cc[j] * ( x2 - YY[j] ) + bb[j] * (x1 - XX[j]) )
        

    out = jnp.stack([dx1, dx2], 1)
    out = jnp.concatenate([out, x[:, 2:]], 1)

    return params['k'] * out


@jit 
def mbp_energy_jnp(x):
    x1 = x[:, 0]
    x2 = x[:, 1]
    value = 0
    for j in range(0, 4):
        value += AA[j] * jnp.exp(aa[j] * (x1 - XX[j])**2 +
                                        bb[j] * (x1 - XX[j]) * (x2 - YY[j]) +
                                        cc[j] * (x2 - YY[j])**2)
    # redundant variables
    value += 0.5 * jnp.sum(x[:, 2:] ** 2, axis=1)

    return params['k'] * value



if __name__ == '__main__':
    # testing 
    mbp = MuellerPotential()
    print(mbp.dim)

    mbp = MuellerPotential(dim=10)
    print(mbp.dim)

    random_x = np.random.randn(2, 10)
    print(mbp.energy(random_x), mbp.grad(random_x)) 

    torch_x = torch.from_numpy(random_x)
    mbp = MuellerPotential_torch(dim=10)
    print(mbp.dim)
    print(mbp.energy(torch_x), mbp.grad(torch_x)) 
