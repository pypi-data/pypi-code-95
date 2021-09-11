import numpy as np 
from neuralsampler.physys.dw import Doublewell
from neuralsampler.physys.gaussian import Gaussian
from neuralsampler.physys.mb import MuellerPotential

import jax 
import jax.numpy as jnp
from jax import jit 
import jax.random as jrd 
from functools import partial

MODEL = {"mb": MuellerPotential, "dw": Doublewell, "gaussian": Gaussian}


class langevin:
    # perform the over-damped langevin update
    def __init__(self, delta_t, model, batchsize, dim):
        self.delta_t = delta_t
        self._model = model 
        self.model = MODEL[model](dim=dim)
        self.k = np.sqrt(2 * delta_t)
        self.batchsize = batchsize
        self.dim = dim 
    
    def step(self, x):
        # one step update
        out = x - self.delta_t * self.model.grad(x) + self.k * np.random.randn(self.batchsize, self.dim)
        return out 
    
    def restrict_step(self, x, thres_eng=100):
        # update with restriction 
        # for example, energy restriction (thres_eng)
        x_new = self.step(x)
        energy_new = self.model.energy(x_new)
        # criterion: x[energy_new < thres_eng]
        out = np.where(energy_new.reshape(-1, 1) < thres_eng, x_new, x)
        return  out 


# jax implementation
@partial(jit, static_argnums=(0,))
def langevin_step_jax(grad_potential_jnp, x, key, delta_t, N_dataset, DIM):
    return x - delta_t * grad_potential_jnp(x) + jnp.sqrt(2 * delta_t) * jrd.normal(key, shape=(N_dataset, DIM))

@partial(jit, static_argnums=(0,1))
def langevin_restrict_step_jax(potential_jnp, grad_potential_jnp, x, key, delta_t, N_dataset, DIM, gen_eng_thres):
    x_new = x - delta_t * grad_potential_jnp(x) + jnp.sqrt(2 * delta_t) * jrd.normal(key, shape=(N_dataset, DIM))
    energy_new = potential_jnp(x_new)
    return jnp.where(energy_new.reshape(-1, 1) < gen_eng_thres, x_new, x)