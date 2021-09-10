"""
inspect.py the following dictionary varaibles are set for use in other classes

dimDomain       - (Int) Dimension of the domain
numPhases       - (Int) Number of phases present
dimRangePhase   - (Int) Range for balance laws usually 1 less than numPhases unless numPhases = 1
dimRangeBalance - (Int) Number of balance laws
isotropic       - (Bool) True if enery is isotropic otherwise false
theta           - (Bool) checks if gammaTheta is defined for time dis
bulkargs        - (Int) Number of arguments the bulk density takes
EdistArgNum     - (Int) Number of arguments Edist takes
QdistArgNum     - (Int) Number of arguments Qdist takes
FdistArgNum     - (Int) Number of arguments Fdist takes
EdistDiff       - (Bool) True if Edist is the same in every phase
QdistDiff       - (Bool) True if Qdist is the same in every phase
FdistDiff       - (Bool) True if Fdist is the same in every phase
neuman          - (Bool) True if neuman function exists false otherwise
"""
import numpy as np
from inspect import signature
import datetime
import ufl

def cell(dimDomain):
    if dimDomain == 1:
        return ufl.Cell("interval", dimDomain)
    elif dimDomain == 2:
        return ufl.Cell("triangle", dimDomain)
    elif dimDomain == 3:
        return ufl.Cell("tetrahedron", dimDomain)
    else:
        return dimDomain.ufl_cell()
def uflSpace(dimDomain, dimRange):
    return ufl.VectorElement(family="Lagrange", cell=cell(dimDomain), degree=1, dim=dimRange)
def coefficient(dimDomain,dimRange=None):
    if dimRange is not None:
        return ufl.Coefficient(uflSpace(dimDomain, dimRange))
    else:
        return ufl.Coefficient(dimDomain)

class InspectSharp:
    def __init__(self, SharpDef):
        self.SharpDef = SharpDef
        """
        Takes sharp class as the input and setups up dictionary of deductions
        throws errors if not consistent
        """
        self._debug =True

        self.inspectDict = {}

        self.calcDimDomain()

        self.calcDimRange()

        self.checkSurfaceMat()

        self.bulkForce()

        self.checkCompareBalance()

        self.checkNeuman()

    def calcDimDomain(self):
        """
        Do some checks on the dimension of the domain to check its consistent and then set
        """
        # If the user has provided the domain as a dgf file use the second parameter
        # as the dimension of the domain
        try:
            self.inspectDict['dimDomain'] = self.SharpDef.omega.dimgrid
        except AttributeError:
            try:
                self.inspectDict['dimDomain'] = self.SharpDef.dimDomain
            except AttributeError:
                try:
                    if len(self.SharpDef.omega)==2:
                        self.inspectDict['dimDomain'] = self.SharpDef.omega[1]
                    elif len(self.SharpDef.omega)==3:
                        self.inspectDict['dimDomain'] = len(self.SharpDef.omega[0])
                    else:
                        raise ValueError("The definition of omega is not consistent, "\
                            +"either provide a `dimDomain` attribute, "\
                            +"use a [[p0],[p1],[N]] tripple or "\
                            +"provide a (file name,dimDomain) pair")
                except TypeError:
                    raise ValueError("The definition of omega isn't consistent")

        # otherwise continue and assume the user is providing a cartesian domain
        # first check all three parameters are the same size

    def calcDimRange(self):
        """
        Calculates the dim range by testing the size of the return list from
        the distributions and initial conditions
        """
        x = ufl.as_vector([1,]*self.inspectDict["dimDomain"])
        result = [len(c) for c in self.SharpDef.initial(x)]
        if len(result) == 1:
            if hasattr(self.SharpDef,"distQ"): # no phases
                self.inspectDict['dimRangeBalance'] = result[0]
                self.inspectDict['numPhases'] = 0
            else: # no balance laws
                self.inspectDict['dimRangeBalance'] = 0
                self.inspectDict['numPhases'] = result[0]
        else:
            self.inspectDict['dimRangeBalance'] = result[1]
            self.inspectDict['numPhases'] = result[0]
        self.inspectDict['dimRangePhase'] = max(self.inspectDict['numPhases']-1,1)

    def checkSurfaceMat(self):
        """
        Checks if the energy is iso or anisotropic
        and if isotropic whether it is admissible
        """
        if self.inspectDict['dimRangePhase'] == 0:
            return None

        # Checks to see whether the user has defined the surface tension in
        # terms of theta a.k.a is zero homogeneous
        if "gammaTheta" in dir(self.SharpDef):
            self.inspectDict['isotropic'] = False
            self.inspectDict['theta'] = True
            return None

        phi = coefficient(self.inspectDict['dimDomain'],self.inspectDict['dimRangePhase'])
        expr = self.SharpDef.gamma(ufl.grad(phi[0]))

        mat = np.array(expr)

        if not mat.shape == mat.T.shape:
            raise ValueError('The matrix of surface tensions must be a square matrix')

        if not np.allclose(mat, mat.T, atol=1.e-8):
            raise ValueError('The matrix of surface tensions must be symetric')

        if type(np.sum(expr)) == np.int64:
            self.inspectDict['isotropic'] = True
        elif ufl.checks.is_scalar_constant_expression(np.sum(expr)):
            self.inspectDict['isotropic'] = True
        else:
            self.inspectDict['isotropic'] = False

    def bulkForce(self):
        """
        sets the bulk force to numer of args
        """
        # check if a excists if it does
        if "a" in dir(self.SharpDef):
            self.inspectDict['bulkargs'] = len(signature(self.SharpDef.a).parameters)
        else:
            self.inspectDict['bulkargs'] = 0

    def checkCompareBalance(self):
        if self.inspectDict['dimRangeBalance'] == 0:
            return

        u = coefficient(self.inspectDict['dimDomain'],self.inspectDict['dimRangeBalance'])
        x = coefficient(self.inspectDict['dimDomain'],1)
        # set defauly values

        # variables are true if they are the same in every phase

        # the number of arguments each function takes
        self.inspectDict['EdistArgNum'] = None
        self.inspectDict['QdistArgNum'] = None
        self.inspectDict['FdistArgNum'] = None

        for i in range(0, self.inspectDict['dimRangeBalance']):
            self.inspectDict['EdistDiff', i] = False
            self.inspectDict['QdistDiff', i] = False
            self.inspectDict['FdistDiff', i] = False

        if self.inspectDict['dimRangeBalance'] !=0 :
            self.inspectDict['QdistArgNum'] =  len(signature(self.SharpDef.distQ).parameters)
            self.inspectDict['FdistArgNum'] =  len(signature(self.SharpDef.distF).parameters)

        if self.inspectDict['dimRangeBalance'] != 0 and self.inspectDict['numPhases'] != 1:

            argsQ = (u, u)[0:self.inspectDict['QdistArgNum']]
            argsF = (u, x, u)[0:self.inspectDict['FdistArgNum']]

            for i in range(0, self.inspectDict['dimRangeBalance']):
                if compare(self.SharpDef.distE(u)[i][0], self.SharpDef.distE(u)[i][1]):
                    self.inspectDict['EdistDiff',i] = True
                    self.debug("E dists are the same: " + str(i))

                if compare(self.SharpDef.distQ(*argsQ)[i][0], self.SharpDef.distQ(*argsQ)[i][1]):
                    self.inspectDict['QdistDiff',i] = True
                    self.debug("Q dists are the same: " + str(i))

                if compare(self.SharpDef.distF(*argsF)[i][0], self.SharpDef.distF(*argsF)[i][1]):
                    self.inspectDict['FdistDiff',i] = True
                    self.debug("F dists are the same: " + str(i))

    # if dubug flat is set outputs to log file
    def debug(self, output):
        try:
            if(self._debug):
                with open("pfout.log", "a") as myfile:
                    myfile.write(str(datetime.datetime.now()))
                    myfile.write(" - ")
                    myfile.write(output)
                    myfile.write("\n")
        except Exception as e:
            print(e)
            pass

    def checkNeuman(self):
        neuman = getattr(self.SharpDef, "neuman", None)
        if callable(neuman):
            self.inspectDict['neuman'] = True
        else:
            self.inspectDict['neuman'] = False

def compare(x, y):
    """
    Compares two ufl expressions by  renumbering the indicies and returns true if they
    are the same and false if they are different
    """

    # if scalar expressions, first try if direct comparison works otherwise check ufl expressions
    try:
        return x == y
    except:
        try:
            return (ufl.algorithms.renumbering.renumber_indices(x) ==
                    ufl.algorithms.renumbering.renumber_indices(y))
        except: # can't be compared so we return false
            return False
