import datetime

from ufl import (as_vector, Coefficient, derivative, diff, dx, inner, Identity, grad,
                 ds, dot, triangle, replace, SpatialCoordinate, TestFunction, TrialFunction,
                 tr, transpose, zero)

import ufl.algorithms.renumbering


from phasefield.auxfun import Implicit, Obstacle, SimpleInterpolate, SmoothStep
from inspect import signature

import numpy as np

##### use small letters for file names
from phasefield.InspectSharp import InspectSharp, coefficient # , cell

def projTSigma(vec):
    """ Takes a vector and projects it to the tangent space TSigma
    """

    dim = vec.ufl_shape[0]
    # in dimension 1 projection operator is the identity
    if dim == 1:
        return vec
    sumTot = 0

    for i in range(0,dim):
        sumTot = sumTot + vec[i]

    return as_vector([vec[i]- (1/dim)*sumTot for i in range(0,dim)])


class UflPhasefield:
    """ Initialises ufl class with smoothing parameters
    """

    def __init__(self, sharpCls, epsilon = None, dt = None,
                 constrained = False, thetaSemi = False,
                 well = None):
        """
        Parameters
        ----------
        sharpCls : object specifying a P gradient flow. Contains the required methods
            and parameters in order to define P gradient flow.

        epsilon : float
            Small parameter proportional to the width of the interface. Default is
            (None)

        dt : float
            Time step (default is None)

        well : (DEPRECATED) function, optional function that has one argument a PhaseModel class
            Potential well W that also specifys the time
            discretisation (default is Implicit).

        thetaSemi : bool, optional
            Flag used to specify whether a specific explicit implicit time
            discretisation is used of the surface energy if it is written in terms of
            an orientation angle theta (default is False).
        """

        if well is not None:
            print("DEPRECATED: do not pass in the 'well' as constructor"+\
                  "argument to the 'PhaseModel' class - just set the 'well'"+\
                  "attribute after construction.")
        assert constrained is False or well == None
        self.constrained = constrained

        self._debug = True
        self.sharpCls = sharpCls

        # set the discretisation for the theta term
        self.thetaSemi = thetaSemi

        if constrained is False:
            if well is None:
                self.well = UflPhasefield.defaultWell
            else: # deprecated
                self.well = well
        else:
            self.well = Obstacle

        # setup constants so use can edit them if they wish before passing to
        # phase base
        self.eps = epsilon
        self.dt = dt
        self.time = 0

        self.inspectDict = InspectSharp(self.sharpCls).inspectDict

        # setup the default smoothing and time discretisation for balance laws
        self.bulkSmoothdict = {}
        self.interpolate = SimpleInterpolate

    def setupPhase(self, phi, phiN, u, uN, vPhi, vU, x=None, constant=None):
        """

        UFL form for balance  + phase field.

        Parameters
        ----------
        phi : Coefficient
            Implicit phase field function.

        phiN : Coefficient
            Explicit phase field function.

        u : Coefficient
            Implicit bulk function.

        uN : Coefficient
            Explicit bulk function.

        vPhi : Coefficient
            Testfunction for phase field equations.

        vU : Coefficient
            Testfunction for bulk equations.

        x : SpatialCoordinate
            Point of the domain used for Dirichlet boundary conditions.

        constant : External.constant class
            Needed for storage of epsilon, dt and t so are allowed to change from
             within time loop. Defaults to `None` leading to the provided
             values being useed directly within the ufl forms.

        Returns
        ----------
        UflForm object :
            Form used for computation, in format
            [[lhsBalance, RhsBalance],[lhsPf,rhsPf]]
        """
        if constant is not None:
            self.eps  = constant(self.eps, "eps")
            self.dt   = constant(self.dt, "dt")
            self.time = constant(self.time, "time")
            self.mobility = constant(self.sharpCls.mobility, "mobility")
        else:
            self.mobility = self.sharpCls.mobility
        self.phi = phi
        self.phiN = phiN
        self.u = u
        self.un = uN
        self.vPhi = vPhi
        self.vU = vU
        if x is not None:
            self.x = x
        else:
            self.x  = SpatialCoordinate(phi[0].ufl_domain())

        if self.inspectDict['dimRangeBalance'] != 0 and self.inspectDict['dimRangePhase'] != 0:
            return [self.setupBalance(), self.setupAllenCahn()]
        elif self.inspectDict['dimRangeBalance'] != 0:
            return [self.setupBalance()]
        else:
            return [self.setupAllenCahn()]

    def forcing(self):
        """
        see if a exists -> how many arguments does it take -> are the return
        values the same
        uses smoothstep function to regularise the bulk quantities
        """
        if self.inspectDict['bulkargs']:
            args=(self.u, grad(self.u), self.un, grad(self.un))[0:self.inspectDict['bulkargs']]
            return inner(projTSigma(self.diffSym(lambda x,y:self.interpolate(x, y, self.sharpCls.a(*args)))),
                         self.vPhi)
        else:
            self.debug("No bulk energy specified")
            return 0

    # sets up the phasefield model in full
    def setupAllenCahn(self):
        """
        Returns ufl form of the right hand side of the Allen-Cahn equation.
        Takes into account the different time scaling if there is only one phase
        """
        # for of this is diffusion - well - bulk forcing
        rhs = (self.diffusionTerm() -
               1/self.eps*inner(projTSigma(self.diffSym(lambda x,y: self.well(self,x,y))),self.vPhi) -
               self.forcing())

        lhs = (inner(self.phi, self.vPhi)*self.mobility -
               inner(self.phiN, self.vPhi)*self.mobility)

        # Implement different time scales
        if self.inspectDict['numPhases'] > 1:
            lhs = lhs*self.eps
        return [lhs*dx, self.dt * rhs * dx]

    def defaultWell(self, phi, phiK):
        """
        If the energy is isoptric multiply the well by that number if it is anisotropic
        don't do anything
        """
        if self.inspectDict['numPhases'] == 1:
            return Obstacle(self,phi,phiK)
        else:
            return Implicit(self,phi,phiK)

    def diffusionTerm(self):
        """
        There are two scenarios here that can happen
        - The user defines an isotropic energy
        - The user defines an ansotropic energy in terms of nu - 1 homo
        - The user defines an ansotropic energy in terms of theta - 0 homo
        """
        # check how many arguments gamma has for if anisotropic
        if self.inspectDict['isotropic'] == False and self.inspectDict['theta'] == False:
            density = self.sharpCls.gamma(grad(phi[0]))[0][1]
            energy = 0.5*inner(density,density)
            d_energy = derivative(energy, phi, self.vPhi)
        elif self.inspectDict['isotropic'] == False and self.inspectDict['theta'] == True:
            theta = coefficient(self.inspectDict['dimDomain'], 1)
            gamma = self.sharpCls.gammaTheta(theta[0])
            gammadash = ufl.algorithms.apply_derivatives.apply_derivatives(diff(gamma, theta))
            expr = gamma*(gamma*ufl.as_matrix([[1, 0], [0, 1]]) +
                          gammadash[0]*ufl.as_matrix([[0, -1], [1, 0]]))
            if self.thetaSemi == True:
                expr = ufl.replace(expr, {theta:as_vector([ufl.atan_2(grad(self.phiN[0])[1],
                                                                      grad(self.phiN[0])[0])])})
            else:
                expr = ufl.replace(expr, {theta:as_vector([ufl.atan_2(grad(self.phi[0])[1],
                                                                      grad(self.phi[0])[0])])})
            d_energy = inner(projTSigma(as_vector([2*expr*grad(self.phi[0]),zero(2)])), grad(self.vPhi))

        elif self.inspectDict['isotropic'] == True:
            d_energy = self.lambdaDash()
            d_energy = inner(d_energy,grad(self.vPhi))
        return -self.eps * d_energy

    def setupBalance(self):
        """
            Setting up the balance laws for the computations order of checking
            - Has use defined custome discretisation?
            - Are distributions the same for each phase?
            - No default discretisation
        """
        lhsTot = 0
        rhsTot = 0

        argsQ = (self.u, self.un)[0:self.inspectDict['QdistArgNum']]
        argsF = (self.u, self.x, self.un)[0:self.inspectDict['FdistArgNum']]

        if self.inspectDict['neuman']:
            x = SpatialCoordinate(triangle)
            flux = self.sharpCls.neuman(self.time + self.dt, x)

        for i in range(0, self.inspectDict['dimRangeBalance']):
            lhs = 0
            rhs = 0
            if self.inspectDict['EdistDiff', i]:
                lhs = (lhs + inner(self.sharpCls.distE(self.u)[i][0], self.vU[i]) -
                       inner(self.sharpCls.distE(self.un)[i][0], self.vU[i]))
            else:
                eTemp = (inner(self.phi, as_vector(self.sharpCls.distE(self.u)[i]))
                         -inner(self.phiN, as_vector(self.sharpCls.distE(self.un)[i])))
                lhs = lhs + inner(eTemp, self.vU[i])

            if self.inspectDict['QdistDiff', i]:
                qtemp = self.sharpCls.distQ(*argsQ)[i][0]
            else:
                qtemp = 0
                for j in range(0, self.inspectDict['numPhases']):
                    qtemp = qtemp + ufl.as_vector(self.bulkSmoothdict.get(('Q', i),
                                                             lambda phi, phin: [i for i in phi])
                                     (self.phi, self.phiN)[j] *
                                     self.sharpCls.distQ(*argsQ)[i][j])

            rhs = rhs + inner(qtemp, grad(self.vU[i]))

            if self.inspectDict['FdistDiff', i]:
                rhs = rhs + inner(self.sharpCls.distF(*argsF)[i][0], self.vU[i])
            else:
                rhs = rhs + inner(inner(as_vector(self.bulkSmoothdict.get(('F', i),
                                                                lambda phi, phin: [i for i in phi])
                                        (self.phi, self.phiN)),
                                        as_vector(self.sharpCls.distF(*argsF)[i]))
                                  , self.vU[i])

            # check here whether neuman conditions exist and are nonzero for that component
            if self.inspectDict['neuman'] and flux[i] != 0:
                if lhs == 0:
                   # do not multiply by dt
                   rhsTot = rhsTot + inner(flux[i], self.vU[i]) * ds
                else:
                   rhsTot = rhsTot + self.dt * inner(flux[i], self.vU[i]) * ds

            # add current balance law to total
            if lhs == 0:
                if rhs != 0:
                    rhsTot = rhsTot + rhs * dx
            else:
                lhsTot = lhsTot + lhs * dx
                if rhs != 0:
                    rhsTot = rhsTot + self.dt * rhs * dx

        return [lhsTot, rhsTot]

    def surfaceVec(self):
        """ In the isotropic case manipulates the user given matrix of surface tensions
        Back in form that is easy for bulding the gradient tensitites
        1 phase - (sigma_11)
        2 phase - (sigma_12)
        3 phase - (sigma_12 sigma_13 sigma_23)
        """
        gamma12 = gamma13 = gamma23 = 0

        # Validation has already been done in inspect classe
        if self.inspectDict['numPhases'] == 1:
            gamma12 = 4*self.sharpCls.gamma(grad(self.phi[0]))[0][0]

        if self.inspectDict['numPhases'] >= 2:
            gamma12 = self.sharpCls.gamma(grad(self.phi[0]))[0][1]

        if self.inspectDict['numPhases'] >= 3:
            gamma13 = self.sharpCls.gamma(grad(self.phi[0]))[0][2]
            gamma23 = self.sharpCls.gamma(grad(self.phi[0]))[1][2]

        Sigma1 = gamma12 + gamma13 - gamma23
        Sigma2 = gamma12 - gamma13 + gamma23
        Sigma3 = -gamma12 + gamma13 + gamma23

        return [Sigma1, Sigma2, Sigma3][0:self.inspectDict['numPhases']]

    def lambdaDash(self):
        # not to be confused with other lambda is the Lambda in the free energy only
        # lower case because of naming conventions
        # preFac is a list of prefactors to each |\nabla \varphi_i|^2 in the energy
        # This is in general not the same as the surface tensions
        return as_vector([self.surfaceVec()[i]*grad(self.phi[i]) for i in range(0,self.inspectDict['numPhases'])])

    def diffSym(self,fnc):
        # Takes a function as the first argument whos first arugment is phi and second is phiK
        derPhi = coefficient(self.inspectDict['dimDomain'], self.inspectDict['numPhases'])
        derPhiN = coefficient(self.inspectDict['dimDomain'], self.inspectDict['numPhases'])

        # expand derivatives to get riof variables
        lowerDeriv = ufl.algorithms.apply_derivatives.apply_derivatives
        lowerAlgebra = ufl.algorithms.apply_algebra_lowering.apply_algebra_lowering

        expr = lowerDeriv(diff(lowerAlgebra(fnc(derPhi, derPhiN)), derPhi) +
                          diff(lowerAlgebra(fnc(derPhi, derPhiN)), derPhiN))
        expr = replace(expr,{derPhi:self.phi})
        expr = replace(expr,{derPhiN:self.phiN})
        return projTSigma(expr)


    # if dubug flat is set outputs to log file
    def debug(self, output):
        try:
            if(self._debug):
                with open("pfout.log", "a") as myfile:
                    myfile.write(str(datetime.datetime.now()))
                    myfile.write(" - ")
                    myfile.write(output)
                    myfile.write("\n")
        except:
            pass
