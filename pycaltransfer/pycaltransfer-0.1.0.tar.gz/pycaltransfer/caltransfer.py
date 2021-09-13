# ------------------------------------------------------------------------
#                           caltransfer methods
# by: Valeria Fonseca Diaz
#  ------------------------------------------------------------------------


import numpy as np
import scipy as sp
from sklearn.cross_decomposition import PLSRegression
from sklearn.linear_model import LinearRegression
from .utils import convex_relaxation


def ds_pc_transfer_fit(X_primary, X_secondary, max_ncp):
    

    '''    
    Direct Standardization (DS) based on PCR. Normally calculated with a high number of components (full rank)
    Method based on standard samples
    
    Parameters
    ----------    
    X_primary : ndarray
        A 2-D array corresponding to the spectral matrix. Shape (N, K) from primary domain
        
    X_secondary : ndarray
        A 2-D array corresponding to the spectral matrix. Shape (N, K) from secondary domain. X_secondary is expected to be paired with X_primary (standard samples)
        
    max_ncp : int
        Number of pc's to train DS model. For classical DS, max_ncp = K
        
    Returns
    -------    
    out : tuple
        (F,a), where `F` is the standardization matrix and `a` is the offset.
        F : ndarray (K,K)
        a : ndarray (1,K)
        
    Notes
    -----
    `F` and `a` used as:
        .. math:: X_p = X_s F + a
    If used for a bilinear model of the type 
        .. math:: y = X_p B_p + \beta_p
    then the final regression model after DS transfer becomes
        .. math:: B_s = F B_p
        .. math:: \beta_s = a B_p + \beta_p
        
    References
    ----------
    Y. Wang, D. J. Veltkamp, and B. R. Kowalski, “Multivariate Instrument Standardization,” Anal. Chem., vol. 63, no. 23, pp. 2750–2756, 1991, doi: 10.1021/ac00023a016.
    
    Examples
    --------
    
    >>> import numpy as np
    >>> from sklearn.cross_decomposition import PLSRegression
    >>> import pycaltransfer.caltransfer as caltransfer
    >>> F_sim = np.array([[0., -0.2, 1.], [1.,0.6,0.8], [0.4,2.5,-1.3]])
    >>> a_sim = np.array([[2.,5.,4.]])
    >>> X_secondary = np.array([[0., 0., 1.], [1.,0.,0.], [2.,2.,2.], [2.,5.,4.]])
    >>> x_error = np.array([[-0.03774524, -0.00475627,  0.01938877],
    ...       [-0.02925257,  0.1500586 ,  0.01706783],
    ...       [-0.11049506, -0.03469373, -0.03136003],
    ...       [-0.00685062, -0.00367186, -0.07211823]])
    >>> X_primary = X_secondary.dot(F_sim) + a_sim + x_error
    >>> x_mean = np.mean(X_primary, axis = 0)
    >>> x_mean.shape = (1,X_primary.shape[1])
    >>> Y = np.array([[0.1], [0.9], [6.2], [11.9]])
    >>> # plsr model primary domain
    >>> pls2 = PLSRegression(n_components=2,scale=False)
    >>> pls2.fit(X_primary, Y)
    >>> B_p = pls2.coef_
    >>> beta_p = pls2.y_mean_ - (x_mean.dot(B_p)) # baseline model y = X_primary B_p + beta_p
    >>> # DS transfer
    >>> F, a = caltransfer.ds_pc_transfer_fit(X_primary, X_secondary, max_ncp = 2) # with 3 components it's already a perfect fit (possibly over fit)
    >>> B_ds = F.dot(B_p)
    >>> beta_s = a.dot(B_p) + beta_p # transferred model y = X_secondary B_s + beta_s
    >>> print(pls2.predict(X_primary))
    >>> print(pls2.predict(X_secondary.dot(F) + a))
    [[ 0.10057381]
     [ 1.03398846]
     [ 5.95594099]
     [12.00949675]]
    [[ 0.18648704]
     [ 0.80221134]
     [ 6.23273672]
     [11.87856491]]



   

    
    '''

    kk = X_primary.shape[1]
    N = X_primary.shape[0]
    ww = 2*kk


    F = np.zeros((kk,kk))
    a = np.zeros((1,kk))

    mean_primary = X_primary.mean(axis=0)
    mean_secondary = X_secondary.mean(axis=0)
    X_primary_c = X_primary - mean_primary
    X_secondary_c = X_secondary - mean_secondary
    
    
    X_in = X_secondary_c[:, :]
    current_ncp = np.amin([max_ncp,X_in.shape[1]])
        

    # ------ svd

    U0,S,V0t = np.linalg.svd(X_in.T.dot(X_in),full_matrices=True)
    S_matrix = np.zeros((current_ncp,current_ncp))
    S_matrix[0:current_ncp,:][:,0:current_ncp] = np.diag(S[0:current_ncp])
    V = V0t[0:current_ncp,:].T
    U = U0[:,0:current_ncp]
    
    X_out = X_primary_c[:, :]  
    
    F = U.dot(np.linalg.inv(S_matrix)).dot(V.T).dot(X_in.T).dot(X_out)
    
    a = mean_primary - F.T.dot(mean_secondary)
    
    a.shape = (1,a.shape[0]) # row vector

 
    
    return (F,a)

    


def pds_pls_transfer_fit(X_primary, X_secondary, max_ncp, ww):
    
    '''
    
    (Piecewise) Direct Standardization (PDS) based on PLSR 
    Method based on standard samples
    
    Parameters
    ----------    
    X_primary : ndarray
        A 2-D array corresponding to the spectral matrix. Shape (N, K) from primary domain
        
    X_secondary : ndarray
        A 2-D array corresponding to the spectral matrix. Shape (N, K) from secondary domain. X_secondary is expected to be paired with X_primary (standard samples)
        
    max_ncp : int
        Number of latent variables for PLSR models.
        
    ww : int
        Half of the total window width. The total window width is 2*ww + 1
        
    Returns
    -------    
    out : tuple
        (F,a), where `F` is the standardization matrix and `a` is the offset.
        F : ndarray (K,K)
        a : ndarray (1,K)
        
    Notes
    -----
    `F` and `a` used as:
        .. math:: X_p = X_s F + a
    If used for a bilinear model of the type 
        .. math:: y = X_p B_p + \beta_p
    then the final regression model after PDS transfer becomes
        .. math:: B_s = F B_p
        .. math:: \beta_s = a B_p + \beta_p
        
    References
    ----------
    E. Bouveresse and D. L. Massart, “Improvement of the piecewise direct standardisation procedure for the transfer of NIR spectra for multivariate calibration,”   Chemom. Intell. Lab. Syst., vol. 32, no. 2, pp. 201–213, 1996, doi: 10.1016/0169-7439(95)00074-7.
    
    Examples
    --------
    
    >>> import numpy as np
    >>> from sklearn.cross_decomposition import PLSRegression
    >>> import pycaltransfer.caltransfer as caltransfer
    >>> F_sim = np.array([[0., -0.2, 1.], [1.,0.6,0.8], [0.4,2.5,-1.3]])
    >>> a_sim = np.array([[2.,5.,4.]])
    >>> X_secondary = np.array([[0., 0., 1.], [1.,0.,0.], [2.,2.,2.], [2.,5.,4.]])
    >>> x_error = np.array([[-0.03774524, -0.00475627,  0.01938877],
    ...       [-0.02925257,  0.1500586 ,  0.01706783],
    ...       [-0.11049506, -0.03469373, -0.03136003],
    ...       [-0.00685062, -0.00367186, -0.07211823]])
    >>> X_primary = X_secondary.dot(F_sim) + a_sim + x_error
    >>> x_mean = np.mean(X_primary, axis = 0)
    >>> x_mean.shape = (1,X_primary.shape[1])
    >>> Y = np.array([[0.1], [0.9], [6.2], [11.9]])
    >>> # plsr model primary domain
    >>> pls2 = PLSRegression(n_components=2,scale=False)
    >>> pls2.fit(X_primary, Y)
    >>> B_p = pls2.coef_
    >>> beta_p = pls2.y_mean_ - (pls2.x_mean_.dot(B_p)) # baseline model y = X_primary B_p + beta_p
    >>> # PDS transfer
    >>> F, a = caltransfer.pds_pls_transfer_fit(X_primary, X_secondary, max_ncp = 1, ww = 1) # ww = 1 means a total window width of 3
    >>> B_ds = F.dot(B_p)
    >>> beta_s = a.dot(B_p) + beta_p # transferred model y = X_secondary B_s + beta_s
    >>> print(pls2.predict(X_primary))
    >>> print(X_primary.dot(B_p) + beta_p)
    >>> print(pls2.predict(X_secondary.dot(F) + a))
    [[ 0.10057381]
     [ 1.03398846]
     [ 5.95594099]
     [12.00949675]]
    [[ 0.10057381]
     [ 1.03398846]
     [ 5.95594099]
     [12.00949675]]
    [[ 0.76356358]
     [ 0.5984284 ]
     [ 5.69538785]
     [12.04262017]]




    '''

    kk = X_primary.shape[1]
    N = X_primary.shape[0]
   


    F = np.zeros((kk,kk))
    a = np.zeros((1,kk))

    mean_primary = X_primary.mean(axis=0)
    mean_secondary = X_secondary.mean(axis=0)
    X_primary_c = X_primary - mean_primary
    X_secondary_c = X_secondary - mean_secondary

    for jj_out in range(0,kk):

        # --- wv to predict    


        X_out = X_primary_c[:, jj_out]     


        # --- input matrix

        ll = np.amax([0, jj_out - ww])
        ul = np.amin([jj_out + ww, kk-1])
        jj_in = np.arange(ll, ul+1)
        X_in = X_secondary_c[:, jj_in]

        chosen_lv = np.amin([max_ncp,X_in.shape[1]])
        
        # --- pls transfer
        
 
        my_pls = PLSRegression(n_components = chosen_lv,scale=False)
        my_pls.fit(X_in, X_out)
        
 
        F[jj_in,jj_out] = my_pls.coef_[:,0]


    a[0,:] = mean_primary - F.T.dot(mean_secondary)
    
    return (F,a)


def epo_fit(X_primary, X_secondary,epo_ncp=1):
    
    
    '''
    
    External Parameter Orthogonalization (EPO) based on spectral value decomposition (SVD) of the difference matrix
    Method based on standard samples
    
    Parameters
    ----------    
    X_primary : ndarray
        A 2-D array corresponding to the spectral matrix. Shape (N, K) from primary domain
        
    X_secondary : ndarray
        A 2-D array corresponding to the spectral matrix. Shape (N, K) from secondary domain. X_secondary is expected to be paired with X_primary (standard samples)
        
    epo_ncp : int
        Number of EPO components to remove. 
          
    Returns
    -------    
    out : tuple
        (E,a), where `E` is the orthogonalization matrix and `a` is the offset.
        E : ndarray (K,K)
        a : ndarray (1,K)
        
    Notes
    -----
    `E` comes from `SVD(D)` where `D = X_primary - X_secondary`
    Orthogonalization of matrices as:
        .. math:: X_{pE} = X_p E + a
        .. math:: X_{sE} = X_s E + a
    If used for a bilinear model, retrain model using `X_{pE}` and `y`. Obtain model 
        .. math:: y = X_{pE} B_e + \beta_e
    Then the final regression model after EPO transfer becomes
        .. math:: B_s = E B_e
        .. math:: \beta_s = a B_e + \beta_e
        
    References
    ----------
    
    M. Zeaiter, J. M. Roger, and V. Bellon-Maurel, “Dynamic orthogonal projection. A new method to maintain the on-line robustness of multivariate calibrations. Application to NIR-based monitoring of wine fermentations,” Chemom. Intell. Lab. Syst., vol. 80, no. 2, pp. 227–235, 2006, doi: 10.1016/j.chemolab.2005.06.011.
    J. M. Roger, F. Chauchard, and V. Bellon-Maurel, “EPO-PLS external parameter orthogonalisation of PLS application to temperature-independent measurement of sugar content of intact fruits,” Chemom. Intell. Lab. Syst., vol. 66, no. 2, pp. 191–204, 2003, doi: 10.1016/S0169-7439(03)00051-0.
    
    Examples
    --------
    >>> import numpy as np
    >>> import pycaltransfer.caltransfer as caltransfer
    >>> from sklearn.cross_decomposition import PLSRegression
    >>> X_primary = np.array([[0., 0., 1.], [1.,0.,0.], [2.,2.,2.], [2.,5.,4.]])
    >>> x_error = np.array([[-0.03774524, -0.00475627,  0.01938877],
    ...       [-0.02925257,  0.1500586 ,  0.01706783],
    ...       [-0.11049506, -0.03469373, -0.03136003],
    ...       [-0.00685062, -0.00367186, -0.07211823]])
    >>> X_secondary = X_primary + x_error
    >>> # Fit EPO
    >>> E,a = caltransfer.epo_fit(X_primary, X_secondary,epo_ncp=1)
    >>> X_primary_e = X_primary.dot(E) + a
    >>> x_mean_e = np.mean(X_primary_e, axis = 0)
    >>> x_mean_e.shape = (1,X_primary_e.shape[1])
    >>> Y = np.array([[0.1], [0.9], [6.2], [11.9]])
    >>> # PLSR after EPO
    >>> pls2 = PLSRegression(n_components=2,scale=False)
    >>> pls2.fit(X_primary_e, Y)
    >>> B_pe = pls2.coef_
    >>> beta_pe = pls2.y_mean_ - (x_mean_e.dot(B_pe)) # Model after EPO y = X_se B_pe + beta_pe; X_se = X_s E +a
    >>> B_s = E.dot(B_pe)
    >>> beta_s = a.dot(B_pe) + beta_pe # transferred model y = X_s Bs + beta_s
    >>> print(X_secondary.dot(B_s) + beta_s)
    >>> print(Y)
    [[ 0.47210387]
     [-0.01622479]
     [ 6.95309782]
     [10.92865516]]
    [[ 0.1]
     [ 0.9]
     [ 6.2]
     [11.9]]

    
    '''  
    
    D = X_primary - X_secondary


    U0,S,V0t = np.linalg.svd(D)
    S_matrix = np.zeros((epo_ncp,epo_ncp))
    S_matrix[0:epo_ncp,:][:,0:epo_ncp] = np.diag(S[0:epo_ncp])
    V = V0t[0:epo_ncp].T
    U = U0[:,0:epo_ncp]

    E = np.identity(n=V.shape[0]) - V.dot(V.T)    
    a = np.mean(X_primary,axis=0)
    a.shape = (1,a.shape[0]) # row vector    

    
    return (E, a)


def jointypls_regression(tscores_primary,tscores_secondary, y_primary, y_secondary):
    
    '''
    
    Re-specification of Q parameters based on scores variables (or latent variables) from an existing PLSR model.
    This function should be used for univariate response (y 1D)
    
    Parameters
    ----------    
    tscores_primary : ndarray
        A 2-D array containing the scores of the primary domain spectra (assumed to be centered). Shape (Np,A)
        
    tscores_secondary : ndarray
        A 2-D array containing the scores of the secondary domain spectra (assumed to be centered). Shape (Ns,A)
        
    y_primary : ndarray
         A 1-D array with reference values of primary spectra. Shape (Np,) 
         
    y_secondary : ndarray
        A 1-D array with reference values of secondary spectra. Shape (Ns,)
        
    Returns
    -------
    out : tuple
        (q_jpls,b), where `q_jpls` is the set of coefficients in the output layer of the bilinear model and `b` is the new intercept.
        q_jpls : array of shape (A,) 
        a : float
    
    Notes
    -----
    If used for a bilinear model of the type 
        .. math:: y = X_p B_p + \beta_p
    where `B_p = Rq`, then the new regression vector is
        .. math:: B_{jpls} = Rq_{jpls}
        .. math:: \beta_{jpls} = b - (\bar(x) B_{jpls})
        
    References
    ----------
    S. García Muñoz, J. F. MacGregor, and T. Kourti, “Product transfer between sites using Joint-Y PLS,” Chemom. Intell. Lab. Syst., vol. 79, no. 1–2, pp. 101–114, 2005, doi: 10.1016/j.chemolab.2005.04.009.
    A. Folch-Fortuny, R. Vitale, O. E. de Noord, and A. Ferrer, “Calibration transfer between NIR spectrometers: New proposals and a comparative study,” J. Chemom., vol. 31, no. 3, pp. 1–11, 2017, doi: 10.1002/cem.2874.
    
    Examples
    --------
    
    >>> import numpy as np
    >>> from sklearn.cross_decomposition import PLSRegression
    >>> import pycaltransfer.caltransfer as caltransfer
    >>> X_secondary = np.array([[0., 0., 1.], [1.,0.,0.], [2.,2.,2.], [2.,5.,4.]])
    >>> x_error = np.array([[-0.03774524, -0.00475627,  0.01938877],
    ...       [-0.02925257,  0.1500586 ,  0.01706783],
    ...       [-0.11049506, -0.03469373, -0.03136003],
    ...       [-0.00685062, -0.00367186, -0.07211823]])
    >>> X_primary = X_secondary + x_error
    >>> x_mean = np.mean(X_primary, axis = 0)
    >>> x_mean.shape = (1,X_primary.shape[1])
    >>> Y = np.array([[0.1], [0.9], [6.2], [11.9]])
    >>> # PLSR
    >>> pls2 = PLSRegression(n_components=2,scale=False)
    >>> pls2.fit(X_primary, Y)
    >>> R_p = pls2.x_rotations_
    >>> B_p = pls2.coef_
    >>> beta_p = pls2.y_mean_ - (x_mean.dot(B_p)) # baseline model y = X_primary B_p + beta_p
    >>> # Transfer with Joint Y PLS. Here a subset of samples or other samples can be used. For the example we use the same samples
    >>> tprimary = (X_primary-x_mean).dot(R_p)
    >>> tsecondary = (X_secondary-x_mean).dot(R_p)
    >>> y_primary = Y[:,0] # flatten 1D
    >>> y_secondary = Y[:,0] # flatten 1D
    >>> q_jpls,b_jpls = caltransfer.jointypls_regression(tprimary, tsecondary, y_primary, y_secondary)
    >>> B_jpls = R_p.dot(q_jpls)  
    >>> beta_jpls = np.asarray(b_jpls - (x_mean).dot(B_jpls))
    >>> print(X_primary.dot(B_jpls) + beta_jpls)
    >>> print(X_secondary.dot(B_jpls) + beta_jpls)
    [ 0.0759273   1.01125531  6.07352354 11.87814864]
    [ 0.12036472  0.81699714  6.28765203 11.93613132]
    

    '''
 
    t_jointpls = np.concatenate((tscores_primary,tscores_secondary), axis = 0)
    y_jointpls = np.concatenate((y_primary,y_secondary), axis = 0)


    calmodel_tr_jointpls = LinearRegression()
    calmodel_tr_jointpls.fit(t_jointpls,y_jointpls) # output values need to be 1D always here
    
            # output
    
    q_jpls = calmodel_tr_jointpls.coef_ 
    b_jpls = calmodel_tr_jointpls.intercept_
  
    
    return (q_jpls,b_jpls)



def slope_bias_correction(y_secondary, y_secondary_pred):
    
    '''
    
    Slope and Bias Correction (SBC) as `y_secondary = b + s*y_secondary_pred`
    This function should be used for univariate response (y 1D)
    
    Parameters
    ----------
    y_secondary : ndarray
        A 1-D array with observed reference values of secondary spectra. Shape (Ns,)
        
    y_secondary_pred : ndarray
        A 1-D array with predicted reference values of secondary spectra using primary model. Shape (Ns,)
        
    Returns
    -------
    out : tuple
        (slope,bias) 
        slope : float 
        bias : float
        
    Notes
    -----
    
    SBC corrects the predictions as `y = y_pred *s + b`
    If used for a bilinear model of the type 
        .. math:: y = X_p B_p + \beta_p
    then the transferred model becomes
        .. math:: B_s = B_p*s
        .. math:: \beta_s = \beta_p*s + b
        
    References
    ----------
    T. Fearn, “Standardisation and calibration transfer for near infrared instruments: A review,” J. Near Infrared Spectrosc., vol. 9, no. 4, pp. 229–244, 2001, doi: 10.1255/jnirs.309.
    
    Examples
    --------
    >>> import numpy as np
    >>> from sklearn.cross_decomposition import PLSRegression
    >>> import pycaltransfer.caltransfer as caltransfer
    >>> X_secondary = np.array([[0., 0., 1.], [1.,0.,0.], [2.,2.,2.], [2.,5.,4.]])
    >>> x_error = np.array([[-0.03774524, -0.00475627,  0.01938877],
    ...       [-0.02925257,  0.1500586 ,  0.01706783],
    ...       [-0.11049506, -0.03469373, -0.03136003],
    ...       [-0.00685062, -0.00367186, -0.07211823]])
    >>> X_primary = X_secondary + x_error
    >>> x_mean = np.mean(X_primary, axis = 0)
    >>> x_mean.shape = (1,X_primary.shape[1])
    >>> Y = np.array([[0.1], [0.9], [6.2], [11.9]])
    >>> # PLSR
    >>> pls2 = PLSRegression(n_components=2,scale=False)
    >>> pls2.fit(X_primary, Y)
    >>> R_p = pls2.x_rotations_
    >>> B_p = pls2.coef_
    >>> beta_p = pls2.y_mean_ - (x_mean.dot(B_p)) # baseline model y = X_primary B_p + beta_p
    >>> # Transfer with Slope and Bias Correction
    >>> y_secondary = Y[:,0]
    >>> y_secondary_pred = X_secondary.dot(B_p) + beta_p
    >>> slope, bias = caltransfer.slope_bias_correction(y_secondary, y_secondary_pred)
    >>> B_sbc = B_p.dot(slope)
    >>> beta_sbc = beta_p.dot(slope) + bias
    >>> print(y_secondary)
    >>> print(X_secondary.dot(B_sbc) + beta_sbc)
    [ 0.1  0.9  6.2 11.9]
    [ 0.15333474  0.81766258  6.25070668 11.87829601]

    '''
    
    sbc = LinearRegression()
    sbc.fit(y_secondary_pred, y_secondary)
    
    slope = sbc.coef_
    bias = sbc.intercept_
    
    return (slope, bias)
    



def dipals(xcal, ycal, xs, xt, A, l, center_mode = "target", heuristic=False):
    
        '''
        Domain-invariant partial least squares regression (di-PLS) performs PLS regression 
        using labeled Source domain data x (=xs) and y and unlabeled Target domain data (xt)
        with the goal to fit an (invariant) model that generalizes over both domains.

    
            
        Parameters
        ----------
        xcal: numpy array (N,K)
            Labeled X data
            
        ycal: numpy array (N,1)
            Response variable
        
        xs: numpy array (N_S,K) 
            Source domain data
        
        xt: numpy array (N_T, K)
            Target domain data. 
            
        A: int
            Number of latent variables
            
        l: int or numpy array (A x 1)
            Regularization parameter: Typically 0 < l < 1e10
            If Array is passed, a different l is used for each LV
            
        center_mode: str, default "target"
            "calibration" (x), "source" (xs) or "target" (xt). This is the mode to recenter the matrices for final prediction. 
            
        heuristic: str
            If 'True' the regularization parameter is determined using a 
            heuristic that gives equal weight to: 
            i) Fitting the output variable y and 
            ii) Minimizing domain discrepancy.
            For details see ref. (3).
    
            
        Returns
        -------
        B: numpy array (K,1)
            Regression vector
            
        beta: float
            Offset (See Notes)
        
        T: numpy array (N,A)
            Training data projections (scores)
        
        Ts: numpy array (N_S,A)
            Source domain projections (scores)
            
        Tt: numpy array (N_T,A)
            Target domain projections (scores)
        
        W: numpy array (K,A)
            Weight vector
            
        P: numpy array (K,A)
            Loadings vector
            
        E: numpy array (N_S,K)
            Residuals of labeled X data   
            
        Es: numpy array (N_S,K)
            Source domain residual matrix
            
        Et: numpy array (N_T,K)
            Target domain residual matrix
            
        Ey: numpy array (N_S,1)
            Response variable residuals
            
        C: numpy array (A,1)
            Regression vector, such that
            y = Ts*C
        
        opt_l: numpy array (A,1)
            The heuristically determined regularization parameter for each LV 
            (if heuristic = 'True')
            
        discrepancy: numpy array (A,)
            Absolute difference between variance of source and target domain projections
            
            
        Notes
        -----
        For this bilinear model, the final model for target  (secondary) data is specified as

            .. math:: \beta = b_0 - (\hat(x)B)
            .. math:: y = xt B + \beta

        References
        ----------

        (1) Ramin Nikzad-Langerodi, Werner Zellinger, Edwin Lughofer, and Susanne Saminger-Platz 
          "Domain-Invariant Partial Least Squares Regression" Analytical Chemistry 2018 90 (11), 
          6693-6701 DOI: 10.1021/acs.analchem.8b00498
        (2) Ramin Nikzad-Langerodi, Werner Zellinger, Susanne Saminger-Platz and Bernhard Moser 
          "Domain-Invariant Regression under Beer-Lambert's Law" In Proc. International Conference
          on Machine Learning and Applications, Boca Raton FL 2019.
        (3) Ramin Nikzad-Langerodi, Werner Zellinger, Susanne Saminger-Platz, Bernhard A. Moser, 
          Domain adaptation for regression under Beer–Lambert’s law, Knowledge-Based Systems, 
          2020 (210) DOI: 10.1016/j.knosys.2020.106447

        Examples
        --------

        For a full application see the jupyter notebooks at https://gitlab.com/vfonsecad/pycaltransfer

  
        
        '''
        
        # Get array dimensions
        (n, k) = np.shape(xcal)
        (ns, k) = np.shape(xs)
        (nt, k) = np.shape(xt)
        
                
        # Center all matrices
        b0 = np.mean(ycal,axis=0)
        x_mu = np.mean(xcal, 0)           # Column means of x
        xs_mu = np.mean(xs, 0)         # Column means of xs
        xt_mu = np.mean(xt, 0)         # Column means of xt
        
        
        x = xcal - x_mu   
        xs = xs - xs_mu
        xt = xt - xt_mu
        
        if center_mode == "calibration":
            
            x_mu_final = x_mu.copy()
        
        elif center_mode == "source":
            
            x_mu_final = xs_mu.copy()
            
        elif center_mode == "target":
            
            x_mu_final = xt_mu.copy()
            
        y = ycal.copy()
            
        if y.ndim == 1:
            y.shape = (y.shape[0], 1)


        

        # Initialize matrices
        T = np.zeros([n, A])
        P = np.zeros([k, A])

        Tt = np.zeros([nt, A])
        Pt = np.zeros([k, A])

        Ts = np.zeros([ns, A])
        Ps = np.zeros([k, A])

        W = np.zeros([k, A])
        C = np.zeros([A, 1])
        opt_l = np.zeros(A)
        discrepancy = np.zeros(A)

        I = np.eye(k)
        
        l = np.asarray(l).flatten()

        # Compute LVs
        for i in range(A):          
  
                
            if l.shape[0]>1:
                
                lA = l[i]
                
            else:
                
                lA = l[0]


            # Compute Domain-Invariant Weight Vector
            w_pls = ((y.T@x)/(y.T@y))  # Ordinary PLS solution



            # Convex relaxation of covariance difference matrix
            D = convex_relaxation(xs, xt)

            if(heuristic is True): # Regularization parameter heuristic

                w_pls = w_pls/np.linalg.norm(w_pls)
                gamma = (np.linalg.norm((x-y@w_pls))**2)/(w_pls@D@w_pls.T)
                opt_l[i] = gamma
                lA = gamma

        
            # Compute di-PLS weight vector
            # reg = (np.linalg.inv(I+lA/((y.T@y))*D))
            # w = w_pls@reg
            reg = I+lA/((y.T@y))*D
            w = sp.linalg.solve(reg.T, w_pls.T, assume_a='sym').T  # ~10 times faster

            # Normalize w
            w = w/np.linalg.norm(w)
          

            # Absolute difference between variance of source and target domain projections
            discrepancy[i] = w@D@w.T
                            

            # Compute scores
            t = x@w.T
            ts = xs@w.T
            tt = xt@w.T

            # Regress y on t
            c = (y.T@t)/(t.T@t)

            # Compute loadings
            p = (t.T@x)/(t.T@t)
            ps = (ts.T@xs)/(ts.T@ts)
            pt = (tt.T@xt)/(tt.T@tt)

            # Deflate X and y (Gram-Schmidt orthogonalization)
            
            t.shape = (t.shape[0],1)
            ts.shape = (ts.shape[0],1)
            tt.shape = (tt.shape[0],1)
            
   
  
            
            x = x - t@p
            xs = xs - ts@ps
            xt = xt - tt@pt
            y = y - t*c

            # Store w,t,p,c
            W[:, i] = w
            T[:, i] = t.reshape(n)
            Ts[:, i] = ts.reshape(ns)
            Tt[:, i] = tt.reshape(nt)
            P[:, i] = p.reshape(k)
            Ps[:, i] = ps.reshape(k)
            Pt[:, i] = pt.reshape(k)
            C[i] = c                


        # Calculate regression vector
        B = W@(np.linalg.inv(P.T@W))@C

        # Store residuals
        E = x
        Es = xs
        Et = xt
        Ey = y
        
        #Offset
        
        beta = b0 - (x_mu_final@B)

        return B, beta, T, Ts, Tt, W, P, Ps, Pt, E, Es, Et, Ey, C, opt_l, discrepancy