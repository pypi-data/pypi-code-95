from fenics import Constant, DirichletBC
from fenics import RectangleMesh, Point, refine
from fenics import VectorFunctionSpace, Function, project, TestFunction
from fenics import solve as _solve

from ufl import triangle, replace
from ufl.algorithms.analysis import extract_arguments_and_coefficients
from ufl.log import UFLException

from phasefield.external import External

#### mynote: need to way to set the constants in the model for the user
def constant(value,name):
    return Constant(value)
def dirichletBC(space,values,part):
    return DirichletBC(space,values,part)
External.constant = constant
External.dirichletBC = dirichletBC

def mesh(domain):
    return RectangleMesh(Point(domain[0]),Point(domain[1]),domain[2][0],domain[2][1])
def adaptMesh(persistentDF, indicator, *args):
    pass
def globalRefine(mesh,steps):
    # the following doesn't work because each time a new mesh is generated
    # and the spaces remain over the old meshes - perhaps there is some
    # other way?
    # for i in range(int(steps/2)):
    #     mesh = refine(mesh)
    pass
External.mesh = mesh
External.adaptMesh = adaptMesh
External.globalRefine = globalRefine

def discreteFunctionSpace(mesh,dimRange,order,storage):
    return VectorFunctionSpace( mesh, "Lagrange", order, dim=dimRange )
def discreteFunction(space,name):
    f = Function(space)
    setattr(f,space.name,f)
    return f
def interpolate(df,expr):
    df.interpolate(project(expr,V=df.function_space()))
def assign(fromDF,toDF):
    toDF.assign(fromDF)
External.discreteFunctionSpace = discreteFunctionSpace
External.discreteFunction = discreteFunction
External.interpolate = interpolate
External.assign = assign

def scheme(equation, dirichletBCs, solver, parameters):
    return [equation.lhs, equation.rhs, dirichletBCs]
def solve(scheme,target):
    phi = TestFunction(target.function_space())
    try:
        args, coeffs = extract_arguments_and_coefficients(scheme[0])
        lhs = replace(scheme[0], {args[1]:target, args[0]:phi})
    except UFLException:
        lhs = scheme[0]
    try:
        args, coeffs = extract_arguments_and_coefficients(scheme[1])
        rhs = replace(scheme[1], {args[1]:target, args[0]:phi})
    except UFLException:
        rhs = scheme[1]
    return _solve(lhs - rhs == 0, target, scheme[2])
External.scheme = scheme
External.solve = solve
