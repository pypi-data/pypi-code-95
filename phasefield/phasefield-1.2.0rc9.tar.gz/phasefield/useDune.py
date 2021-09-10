# from ufl_phasefield and InspectSharp
import ufl
from dune.ufl import Constant, Space
# from phasefield_stepper
from dune.ufl import DirichletBC
from dune.fem import adapt, mark, markNeighbors, loadBalance

from dune.grid import cartesianDomain
from dune.alugrid import aluConformGrid as leafGridView
from dune.fem.view import adaptiveLeafGridView as adaptiveGridView
from dune.fem.space import lagrange as solutionSpace
from dune.fem.scheme import galerkin as solutionScheme

from phasefield.external import External

#### mynote: need to way to set the constants in the model for the user
def constant(value,name):
    return Constant(value,name)
def dirichletBC(space,values,part):
    return DirichletBC(space,values,part)
External.constant = constant
External.dirichletBC = dirichletBC

def mesh(domain):
    try:
        domain = cartesianDomain(*domain)
        return adaptiveGridView(leafGridView(*domain))
    except TypeError:
        try:
            return adaptiveGridView(leafGridView(domain))
        except TypeError:
            return adaptiveGridView(leafGridView(*domain))
def adaptMesh(persistentDF, indicator, *args):
    markNeighbors(indicator, *args)
    adapt(persistentDF)
    loadBalance(persistentDF)
def globalRefine(mesh,steps):
    mesh.hierarchicalGrid.globalRefine(steps)
External.mesh = mesh
External.adaptMesh = adaptMesh
External.globalRefine = globalRefine

def discreteFunctionSpace(mesh,dimRange,order,storage):
    return solutionSpace(mesh,dimRange=dimRange,order=order,storage=storage)
def discreteFunction(space,name):
    f = space.interpolate([0,]*space.dimRange,name)
    setattr(f,space.name,f)
    return f
def interpolate(df,expr):
    df.interpolate(expr)
def assign(fromDF,toDF):
    toDF.assign(fromDF)
External.discreteFunctionSpace = discreteFunctionSpace
External.discreteFunction = discreteFunction
External.interpolate = interpolate
External.assign = assign

def scheme(equation, dirichletBCs, solver, parameters):
    if dirichletBCs is None:
        return solutionScheme( equation,
                               solver = solver, parameters = parameters )
    else:
        return solutionScheme( [equation, *dirichletBCs],
                               solver = solver, parameters = parameters )
def solve(scheme,target):
    return scheme.solve(target=target)
External.scheme = scheme
External.solve = solve
