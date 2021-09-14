import jax.numpy as jnp
import math as ma

def writhe_jax(curve):
    '''
    Returns writhe of given closed parametric curve.

    Parameters
    ----------
    curve: jnp.array
        An ``N`` by 3 array describing locations of endpoints of ``N`` linear segments approximating the curve. All locations should be distinct.

    Returns
    -------
    float
        Value of writhe for closed curve comprised of linear segments given.

    Example
    -------
    >>> import jax.numpy as jnp
    >>> curve = np.array([[-1,0,-1],[1,0,1],[0,-1,1],[0,1,1]])
    >>> pywrithe.writhe_jax(curve)
    0.366

    '''
    segments = jnp.transpose(jnp.array([jnp.roll(curve,1,axis=0),curve]),(1,0,2)) # (segment,begin/end,coordinate) order
    n = len(segments)

    segment_a = segments[:,jnp.newaxis]
    segment_b = segments[jnp.newaxis,:]
    r13 = segment_a[:,:,0] - segment_b[:,:,0]
    r14 = segment_a[:,:,0] - segment_b[:,:,1]
    r23 = segment_a[:,:,1] - segment_b[:,:,0]
    r24 = segment_a[:,:,1] - segment_b[:,:,1]

    r34 = segment_b[:,:,0] - segment_b[:,:,1]
    r12 = segment_a[:,:,0] - segment_a[:,:,1]

    n1 = jnp.cross(r13,r14)
    n2 = jnp.cross(r14,r24)
    n3 = jnp.cross(r24,r23)
    n4 = jnp.cross(r23,r13)

    n1norm = ((jnp.sum(n1**2,axis=-1) + jnp.finfo(n1.dtype).tiny)**(0.5))[:,:,jnp.newaxis]
    n2norm = ((jnp.sum(n2**2,axis=-1) + jnp.finfo(n1.dtype).tiny)**(0.5))[:,:,jnp.newaxis]
    n3norm = ((jnp.sum(n3**2,axis=-1) + jnp.finfo(n1.dtype).tiny)**(0.5))[:,:,jnp.newaxis]
    n4norm = ((jnp.sum(n4**2,axis=-1) + jnp.finfo(n1.dtype).tiny)**(0.5))[:,:,jnp.newaxis]

    # deal with NaN cases by changing norms to 1 where needed
    # deal with gradient issues by adding tiny where needed
    n1n = n1 / jnp.where(n1norm !=0.0, n1norm, 1) + jnp.finfo(n1.dtype).tiny
    n2n = n2 / jnp.where(n2norm !=0.0, n2norm, 1) + jnp.finfo(n2.dtype).tiny
    n3n = n3 / jnp.where(n3norm !=0.0, n3norm, 1) + jnp.finfo(n3.dtype).tiny
    n4n = n4 / jnp.where(n4norm !=0.0, n4norm, 1) + jnp.finfo(n4.dtype).tiny

    # products are over last axis
    foo = 0.99999995#jnp.array(1.) - jnp.finfo(n1.dtype).tiny 
    d1 = jnp.clip( jnp.sum(n1n*n2n,axis=-1) ,-foo,foo)
    d2 = jnp.clip( jnp.sum(n2n*n3n,axis=-1) ,-foo,foo)
    d3 = jnp.clip( jnp.sum(n3n*n4n,axis=-1) ,-foo,foo)
    d4 = jnp.clip( jnp.sum(n4n*n1n,axis=-1) ,-foo,foo)

    a1 = jnp.arcsin(d1)
    a2 = jnp.arcsin(d2)
    a3 = jnp.arcsin(d3)
    a4 = jnp.arcsin(d4)

    omega_star =  (a1+a2+a3+a4)

    omega = omega_star * jnp.sign( jnp.sum( jnp.cross(r34,r12) * r13 ,axis=-1) )

    mask = 1 - (jnp.eye(n) + jnp.roll(jnp.eye(n),1,axis=0) + jnp.roll(jnp.eye(n),1,axis=1))

    omega_masked = jnp.where( mask==1 ,omega,0)

    #print(omega_masked)

    return (1.0 / (4.0 * ma.pi)) * jnp.sum( omega_masked )
