"""
Only contains phase base class currently
"""

from __future__ import print_function

import ufl

from phasefield.external import External
from phasefield.InspectSharp import coefficient

from ufl import (as_vector, Coefficient, dot, dx, grad, inner, Identity, SpatialCoordinate,
                 TestFunction, TrialFunction, tr, transpose, replace, zero)
from ufl.algorithms import expand_indices
from ufl.algorithms.analysis import extract_arguments_and_coefficients
from ufl.algorithms.apply_derivatives import apply_derivatives
from ufl.algorithms.apply_algebra_lowering import apply_algebra_lowering

class PhaseStepper:
    """
    Base class for phasefield computations with timestepping
    """


    def __init__(self, uflModel, solverParameters = {"newton.tolerance":1e-8,
                                                     "newton.linear.tolerance":1e-10,
                                                     "newton.verbose":False,
                                                     "newton.linear.verbose":False},
                 orderFe = 1, solver = "gmres",
                 preBulk = [], phaseBulk = [], postBulk = [],
                 storage = None, debug = False,
                 gridView = None
                ):

        """

        auxParam has; dirichlet, storage, solver, orderFe, solverParameters, mono

        1) 'constraint' is used if
           (a) the well is an 'Obstacle' well and
           (b) the phase bulk equation (phaseBulk) + the phasefield equation are linear

        2) if phaseBulk = [] then we set this to be all bulk equation not specified in
           preBulk and postBulk, i.e phaseBulk = [0,...,dimBulk-1]/(preBulk+postBulk).
           This way it is sufficient to only prescribe one (or both) of pre/postBulk
           and not to provide phaseBulk. If all three are given they have to add up to
            [0,..,dimRange-1].

        Parameters
        ----------
        uflModel : class specifying P epsilon gradient flow
            Must provide a public method called setupPhase which takes 7 arguments the
            coefficients for the implicit and explicit parts of phi and u in addition
            to spatial co-ordinates for forcing terms (phi, phiN, u, uN, vPhi, vU, x).

        solverParameters : dictionary, optional
            Tolerance and verbosity parameters to pass to the dictionary,

        orderFe : int, optional
            Order of the lagrange FEM space (default is 1)

        solver : string, optional
            The solver used for solving the results systems of equations which are
            possibly non-linear. If using DUNE a number of possible solvers are
            {'cg','gmres','bigcgstab','("suitesparse","umfpack")','petsc'}. Depending
            on the  solver the storage is also set.

        preBulk : uflForm, optional
            Bulk equations solved before the phasefield equations, must not depend on
            phi.

        phaseBulk : uflForm, optional
            Phase-field equations to be solved after the pre bulk must not depend on
            any coefficients solved in postBulk.

        postBulk : uflForm, optional
            Finaly bulk equations to be solved can depend on any of the other
            coefficients.

        storage: string, optional
            The type of storage used for the FE functions. If None the solver is
            checked and the appropriate storage is then chosen. (default is "cg")

        debug : bool, optional
            In depth debuggins information on ufl form printing to log file.
            (default is False)

        Raises
        ----------
            AttributeError
                If the storage can nott be deduced from the given solver, it therefore must be
                specified manually.

            ValueError
                The pre and post, bulk equations depend on each other in an inconsistent way.

            ValueError
                Constrained is set to True imposing an obstacle solver must impose the
                constraints 0 < phi < 1 however the storage is not set to istl.
        """

        if storage is None:
            if solver in ["gmres","cg","bicgstab"]:
                storage = "istl"
            elif solver == "direct":
                solver = ("suitesparse","umfpack")
                storage = "fem"
            elif solver[0] == "suitesparse":
                storage = "fem"
            elif solver[0] == "petsc":
                storage = "petsc"
                solver = solver[1]
            else:
                raise AttributeError("can't determine which storage from given solver")
        else:
            if solver[0] == "suitesparse":
                assert storage == "fem"

        self._debug = debug

        self._uflModel = uflModel
        self.auxParam = {'solverParameters':solverParameters, 'storage':storage,
                         'solver':solver, 'orderFe':orderFe}

        if gridView is None:
            self.gridView = External.mesh(self._uflModel.sharpCls.omega)
        else:
            self.gridView = gridView

        self.dimBulk  = self._uflModel.inspectDict['dimRangeBalance']
        self.dimPhase = self._uflModel.inspectDict['dimRangePhase']
        self.dimRange = self.dimBulk + self.dimPhase

        self.preBulk   = preBulk
        self.postBulk  = postBulk
        self.phaseBulk = phaseBulk
        if set(self.preBulk) and set(self.postBulk):
            raise ValueError("the partitioning into pre and post set of bulk equations is not disjoint")
        if self.phaseBulk == []:
            self.phaseBulk = [x for x in range(self.dimBulk)
                                if x not in self.preBulk + self.postBulk]
        if not set(self.phaseBulk).isdisjoint(self.postBulk) or \
           not set(self.phaseBulk).isdisjoint(self.preBulk):
            raise ValueError("the partitioning into phase, pre, and post set of bulk equations is not disjoint")
        if not set(self.preBulk) and set(self.postBulk) and set(self.phaseBulk) == set(range(self.dimBulk)):
            raise ValueError("the partitioning of the bulk equations is not consistent")

        self.setupModel()

        self.constrained = self._uflModel.constrained

        # Check that if constraint is to be used the storage is consistent
        if self.constrained and storage != "istl":
            raise ValueError("Storage must be set to istl when using obstacle potential")

        if self.constrained:
            self.zeros = self.spaces[0][0].interpolate(self.spaces[0][0].dimRange*[0],name="zeros")
            self.res   = self.spaces[0][0].interpolate(self.spaces[0][0].dimRange*[0],name="res")
            self.lower_lim = self.spaces[0][0].interpolate(self.spaces[0][0].dimRange*[0], name = "upper_lim")
            self.upper_lim = self.spaces[0][0].interpolate(self.spaces[0][0].dimRange*[1], name = "lower_lim")

        # set up the initial data
        self.initialInterpolate()

        # default indicator and phasefield parameters for adaptive grid
        self.indicator = sum(dot(grad(self.solution[i]), grad(self.solution[i])) for i in range(0,self._uflModel.inspectDict['dimRangePhase']))

        # in format [refineTolerance, coarsenTolerance, minLevel, maxLevel]
        self.defaultRefine = [1.4, 1.2, 4, 12]

        try:
            from dune.fem.function import levelFunction, partitionFunction
            self.saveStep = self._uflModel.sharpCls.saveStep
            self.fileBase = self._uflModel.sharpCls.__name__ \
                            if not hasattr(self._uflModel.sharpCls,"fileBase") \
                            else self._uflModel.sharpCls.fileBase
            self.dimPhase = self._uflModel.inspectDict['dimRangePhase']
            self.dimBulk  = self._uflModel.inspectDict['dimRangeBalance']
            func  = [["phi_"+str(i),self.solution[i]] for i in range(self.dimPhase)]
            func += [["u_"+str(i),self.solution[i+self.dimPhase]] for i in range(self.dimBulk)]
            self.vtk = self.gridView.sequencedVTK(self.fileBase,
                                               pointdata=[self.solution], # dict(func),
                                               celldata=[levelFunction(self.gridView)])
            self.saveTime = None
        except: # AttributeError or ImportError or ModuleNotFoundError:
            self.vtk = None

        if self.dimBulk>0:
            self.bulk = as_vector([self.solution[i] for i in range(self.dimPhase,self.dimRange)])
        else:
            self.bulk = None
        if self.dimPhase>0:
            self.phase = as_vector([self.solution[i] for i in range(0,self.dimPhase)])
        else:
            self.phase = None


    @property
    def time(self):
        return float(self._uflModel.time)
    @time.setter
    def time(self,value):
        self._uflModel.time.assign(value)
    @property
    def dt(self):
        return float(self._uflModel.dt)
    @dt.setter
    def dt(self,value):
        self._uflModel.dt.assign(value)
    @property
    def epsilon(self):
        return float(self._uflModel.eps)
    @epsilon.setter
    def epsilon(self,value):
        self._uflModel.eps.assign(value)
    @property
    def mobility(self):
        return float(self._uflModel.mobility)
    @mobility.setter
    def mobility(self,value):
        self._uflModel.mobility.assign(value)

    def setupModel(self):
        # spaces are for [phase,pre,post], so [0]=phase also for scheme etc.
        self.spaces  = [None,None,None]
        self.spaces[0] = (self.setupSpace(self.gridView,
                len(self.phaseBulk)+self.dimPhase),"phase")
        if not self.preBulk == []:
            self.spaces[1] = (self.setupSpace(self.gridView,
                    len(self.preBulk)), "pre")
        if not self.postBulk == []:
            self.spaces[2] = (self.setupSpace(self.gridView,
                    len(self.postBulk)), "post")
        if self.spaces[1] is None and self.spaces[2] is None:
            self.spc = self.spaces[0][0]
            setattr(self.spc,"name",self.spaces[0][1])
        else:
            from dune.fem.space import product as productSpace
            self.spc = productSpace(
                         [s[0] for s in self.spaces if s is not None],
                         components=[s[1] for s in self.spaces if s is not None]
                       )
            setattr(self.spc,"name","full")

        self.scalarSpace = self.setupSpace(self.gridView,1)

        # solution at new and old timsteps
        self.solution = External.discreteFunction(self.spc, "solution")
        self.solutionN = External.discreteFunction(self.spc, "solutionN")

        self.x  = SpatialCoordinate(self.spc)
        vFull   = TestFunction(self.spc)

        solutionParts = dict([ (s[1],getattr(self.solution,s[1]).as_ufl())
                              for s in self.spaces if s is not None ])
        imCoeff = as_vector([ u[i] for s in self.spaces if s is not None
                              for u in [solutionParts[s[1]]]
                              for i in range(u.dimRange) ])
        coeffN  = as_vector([ u[i] for s in self.spaces if s is not None
                              for u in [getattr(self.solutionN,s[1]).as_ufl()]
                              for i in range(u.dimRange) ])


        # first define the phase field variables for generating the ufl model
        if self._uflModel.inspectDict['numPhases'] == 1:
            # single phase problem
            phi = ufl.as_vector([imCoeff[0]])
            phiN = ufl.as_vector([coeffN[0]])
            vPhi = ufl.as_vector([vFull[0]])
        elif self._uflModel.inspectDict['dimRangePhase'] !=0:
            # the mth component of vphi will be set to zero
            # while the mth compoentn of phi and phiN will be set to 1-phi[0]
            vPhi_M = coefficient(self.scalarSpace)
            imCoeff_M = coefficient(self.scalarSpace)
            coeffN_M = coefficient(self.scalarSpace)

            phi = ufl.as_vector([imCoeff[i] for i in range(0, self._uflModel.inspectDict['dimRangePhase'])] + [imCoeff_M[0]])
            phiN = ufl.as_vector([coeffN[i] for i in range(0, self._uflModel.inspectDict['dimRangePhase'])] + [coeffN_M[0]])
            vPhi = ufl.as_vector([vFull[i] for i in range(0, self._uflModel.inspectDict['dimRangePhase'])] + [vPhi_M[0]])
        else:
           phi = 0
           phiN = 0
           vPhi = 0

        # renumber the bulk equations according to pre/phase/post
        if self._uflModel.inspectDict['dimRangeBalance'] != 0:
            renumbering = [None for _ in range(self.dimBulk)]
            for i,x in enumerate(self.phaseBulk):
                renumbering[x] = self.dimPhase+i
            for i,x in enumerate(self.preBulk):
                renumbering[x] = self.dimPhase++len(self.phaseBulk)+i
            for i,x in enumerate(self.postBulk):
                renumbering[x] = self.dimPhase+len(self.phaseBulk+self.preBulk)+i
            vU = ufl.as_vector([vFull[j] for j in renumbering])
            u  = ufl.as_vector([imCoeff[j] for j in renumbering])
            un = ufl.as_vector([coeffN[j] for j in renumbering])
        else:
            vU = 0
            u = 0
            un = 0

        form = self._uflModel.setupPhase(phi, phiN, u, un, vPhi, vU,
                                         constant=External.constant )
        #sums the lhs or rhs respectively to get the ufl forms
        equation = sum(row[0]-row[1] for row in form)

        # If the number of phases is bigger than one to the reduciton to m-1 phases
        if self._uflModel.inspectDict['numPhases'] > 1:
            # replace the v component in the phase field equations with zero
            equation = replace(equation,{vPhi_M:zero(1)})
            equation = replace(equation,{imCoeff_M:as_vector([1-sum(imCoeff[i] for i in range(0, self._uflModel.inspectDict['dimRangePhase']))])})
            equation = replace(equation,{coeffN_M:as_vector([1-sum(coeffN[i] for i in range(0, self._uflModel.inspectDict['dimRangePhase']))])})

        # now build the three separate equations
        self.equations = [None,None,None]
        def remove(i):
            if self.spaces[i] is not None:
                v = TestFunction(self.spaces[i][0])
                w = [0 for _ in range(self.dimRange)]
                if i == 0:
                    for j in range(self.dimPhase):
                        w[j] = v[j]
                    for j,e in enumerate(self.phaseBulk):
                        w[self.dimPhase+e] = v[self.dimPhase+j]
                if i == 1:
                    for j,e in enumerate(self.preBulk):
                        w[self.dimPhase+e] = v[j]
                if i == 2:
                    for j,e in enumerate(self.postBulk):
                        w[self.dimPhase+e] = v[j]
                return {vFull: as_vector(w),
                        solutionParts[ self.spaces[i][1] ]: TrialFunction(self.spaces[i][0])}
            else:
                return None
        d = remove(0)
        if d:
            self.equations[0] = replace(equation,d)
            _, test = extract_arguments_and_coefficients(self.equations[0])
        d = remove(1)
        if d:
            self.equations[1] = replace(equation,d)
            _, test = extract_arguments_and_coefficients(self.equations[0])
        d = remove(2)
        if d:
            self.equations[2] = replace(equation,d)

        # check validity of equations
        for i, e in enumerate(self.equations):
            if not e:
                assert self.spaces[i] is None
            else:
                def getAttr(t):
                    try:
                        return solutionParts[t]
                    except:
                        return None
                if i == 0:
                    checkCoeffsNotPresent = [getAttr("phase"),getAttr("post")]
                if i == 1:
                    checkCoeffsNotPresent = [getAttr("phase"),getAttr("pre"),getAttr("post")]
                if i == 2:
                    checkCoeffsNotPresent = [getAttr("post")]

        # setup the dirichlet boudnary conditions needs to be done after space but before model
        self.dirichlet = [None,None,None]
        if "dirichlet" in dir(self._uflModel.sharpCls):
            bcs = [[v,k] for k, v in
                   self._uflModel.sharpCls.dirichlet(self.time+self.dt, self.x).items()]
            if self.spaces[0] is not None: # have a 'phase' part
                self.dirichlet[0] = [External.dirichletBC(self.spaces[0][0],
                                       self.dimPhase*[None]+[bc[0][i] for i in self.phaseBulk],
                                       bc[1]) for bc in bcs]
            if self.spaces[1] is not None: # have a pre part
                self.dirichlet[1] = [External.dirichletBC(self.spaces[1][0],
                                       [bc[0][i] for i in self.preBulk],
                                       bc[1]) for bc in bcs]
            if self.spaces[2] is not None: # have a post part
                self.dirichlet[2] = [External.dirichletBC(self.spaces[2][0],
                                       [bc[0][i] for i in self.postBulk],
                                       bc[1]) for bc in bcs]
            self.debug("Dirichlet boundary conditions")

        self.schemes = [self.setupScheme(e,d) for e,d in zip(self.equations,self.dirichlet)]

    def setupSpace(self, gridView, dimRange):
        self.debug("storage set as" + str(self.auxParam['storage']))
        return External.discreteFunctionSpace(self.gridView, dimRange=dimRange, order=self.auxParam['orderFe'],
                             storage=self.auxParam['storage'])

    def setupScheme(self, eqn, dirichlet):
        if eqn:
            return External.scheme( eqn==0, dirichlet,
                               solver = self.auxParam['solver'],
                               parameters = self.auxParam['solverParameters'])
        else:
            return None

    def output(self, force=False):
        if self.vtk is not None:
            if force:
                self.vtk()
            else:
                if self.saveTime is None:
                    self.vtk()
                    self.saveTime = self.saveStep
                if self.saveTime <= self.time:
                    self.vtk()
                    self.saveTime += self.saveStep

    # compute solution at next timestep
    def nextTime(self, initialSmoothing=False):
        """
        Computes the solution at the next time step.

        Notes
        ----------
        This does not adapt the grid

        """

        External.assign(self.solution,self.solutionN)

        if self.schemes[1] is not None and not initialSmoothing:
            External.solve(self.schemes[1],target=self.solution.pre)

        assert self.schemes[0] is not None
        if not self.constrained:
            External.solve(self.schemes[0],target=self.solution.phase)
        else:
            from dune.generator import algorithm, path
            from dune.fem.operator import linear

            self.zeros.clear()
            self.schemes[0](self.zeros, self.res)
            for i in range(len(self.solution.phase.as_istl)):
                self.res.as_istl[i] *= -1
            matrix = linear(self.schemes[0]).as_istl
            self.lower_lim.clear()
            if self._uflModel.inspectDict['numPhases'] == 1:
                self.upper_lim.assign(self.solutionN.phase)
            else:
                self.upper_lim.interpolate(self.spaces[0][0].dimRange*[1])

            parameters = self.auxParam['solverParameters']
            args = [self.gridView,
                       matrix, self.solution.phase.as_istl, self.res.as_istl,
                       self.lower_lim.as_istl, self.upper_lim.as_istl,
                       self.dimPhase,100,
                       parameters.get("newton.tolerance",1.0e-10),
                       parameters.get("newton.verbose",False)
                   ]
            try:
                self.tnnmg(*args)
            except AttributeError:
                self.tnnmg = algorithm.load('solveObstacleProblemByTNNMG',
                                            path(__file__) + '/tnnmg.cc',
                                            *args)
                self.tnnmg(*args)

        if self.schemes[2] is not None and not initialSmoothing:
            External.solve(self.schemes[2],target=self.solution.post)

        if not initialSmoothing:
            self._uflModel.time.assign(self._uflModel.time + self._uflModel.dt)
            self.output()

    def initialInterpolate(self):
        """
        initialize solution for start of simulation
        """

        try:
            bulkInitial = self._uflModel.sharpCls.initial(self.x)[1]
        except IndexError:
            bulkInitial = []
        External.interpolate(self.solution, as_vector(self._uflModel.sharpCls.initial(self.x)[0][0:self._uflModel.inspectDict['dimRangePhase']] + bulkInitial) )

    def initialRefine(self, numRefine):
        External.globalRefine(self.gridView,numRefine)
        self.initialInterpolate()

    def adapt(self):
        """
        Performs adaptive refinement of the grid depends on the member variables
        indicator and default refine.
        """
        External.adaptMesh([self.solution],self.indicator, *self.defaultRefine)

    def initialAdapt(self, numRefine, smoothingEpsilon=None):
        if smoothingEpsilon is not None:
            tempepsilon = self.epsilon
            self.epsilon = smoothingEpsilon
            tempmobility = self.mobility
            self.mobility = 0

        for i in range(0, numRefine):
            self.adapt()
            self.initialInterpolate()
            if smoothingEpsilon:
                self.nextTime(True)

        if smoothingEpsilon is not None:
            self.epsilon = tempepsilon
            self.mobility = tempmobility

    def gridSetup(self, numGlobalRefine, numLocalRefine, smoothingEpsilon=None):
        """
        Performs the initial refinement of the grid.

        Parameters
        ----------
        numGlobalRefine : int
            Number of global refinements to do.

        numLocalRefine : int
            Number of adaptive refinements, depends on member variables indicator
            and defaultRefine.
        """
        self.initialRefine(numGlobalRefine)
        self.initialAdapt(numLocalRefine, smoothingEpsilon)
        self.output()

    def checkDependencies(self,form, checkCoeffsNotPresent):
        from ufl.algorithms.formtransformations import compute_form_lhs
        v,u = form.arguments()
        dimRange = u.ufl_shape[0]
        assert dimRange == v.ufl_shape[0]
        depend = dimRange*[True]
        form = compute_form_lhs(form)
        coeff = as_vector([coefficient(self._uflModel.inspectDict["dimDomain"],None) for i in range(dimRange)])
        for i in range(dimRange):
            depend[i] = dimRange*[False]
            testUnit = dimRange*[0]
            testUnit[i] = v[i]
            form_i = replace(form, {v: as_vector(testUnit)})
            form_i = expand_indices(apply_derivatives(apply_algebra_lowering(form_i)))
            form_i = replace(form_i, {u: coeff})
            form_i = (expand_indices(apply_derivatives(apply_algebra_lowering(form_i))))
            _, test = extract_arguments_and_coefficients(form_i)
            for j in range(dimRange):
                depend[i][j] = coeff[j] in test
            for c in checkCoeffsNotPresent:
                assert c not in test
        return depend

    # if dubug flag is set outputs to log file
    def debug(self,output):
        try:
            if(self._debug):
                with open("pfout.log", "a") as myfile:
                    myfile.write(str(datetime.datetime.now()))
                    myfile.write(" - ")
                    myfile.write(output)
                    myfile.write("\n")
        except:
            pass
