# ------------------------------------------------------------------------
#                           caltransfer utils
# by: Valeria Fonseca Diaz
#  ------------------------------------------------------------------------

import numpy as np
from scipy.linalg import eigh

def convex_relaxation(xs, xt):
        '''
        Convex relaxation of covariance difference.
         
        The convex relaxation computes the eigenvalue decomposition of the (symetric) covariance 
        difference matrix, inverts the signs of the negative eigenvalues and reconstructs it again. 
        It can be shown that this relaxation corresponds to an upper bound on the covariance difference
        btw. source and target domain (see ref.)
        
        Reference:
        * Ramin Nikzad-Langerodi, Werner Zellinger, Susanne Saminger-Platz and Bernhard Moser 
          "Domain-Invariant Regression under Beer-Lambert's Law" In Proc. International Conference
          on Machine Learning and Applications, Boca Raton FL 2019.
        
        Parameters
        ----------
        
        xs: numpy array (Ns x k)
            Source domain matrix
            
        xt: numpy array (Nt x k)
            Target domain matrix
            
        Returns
        -------
        
        D: numpy array (k x k)
            Covariance difference matrix
        
        '''
        
        # Preliminaries
        ns = np.shape(xs)[0]
        nt = np.shape(xt)[0]
        x = np.vstack([xs, xt])
        x = x[..., :] - np.mean(x, 0)
        
        # Compute difference between source and target covariance matrices   
        rot = (1/ns*xs.T@xs- 1/nt*xt.T@xt) 

        # Convex Relaxation
        w,v = eigh(rot)
        eigs = np.abs(w)
        eigs = np.diag(eigs)
        D = v@eigs@v.T 

        return D

