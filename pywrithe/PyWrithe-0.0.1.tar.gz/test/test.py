import pywrithe
import numpy as np
import jax.numpy as jnp

curve = jnp.array([[-1,0,-1],[1,0,1],[0,-1,1],[0,1,1]])
print(pywrithe.writhe_jax(curve))

