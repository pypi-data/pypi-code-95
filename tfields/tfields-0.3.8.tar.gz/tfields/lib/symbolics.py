"""
sympy helper functions
"""
import sympy
from sympy.logic.boolalg import BooleanFunction


def split_expression(expr):
    """
    Return the expression split up in the basic boolean functions.
    """
    if isinstance(expr, sympy.Not):
        expr = expr.to_nnf()
    if isinstance(expr, BooleanFunction):
        expressions = expr.args
    else:
        expressions = [expr]
    return expressions


def to_planes(expr):
    """
    Resolve BooleanFunctions to retrieve multiple planes
    Examples:
        >>> import sympy
        >>> from tfields.lib.symbolics import to_planes, to_plane
        >>> x, y, z = sympy.symbols('x y z')
        >>> eq1 = 2*x > 0
        >>> eq2 = 2*y + 3*z <= 4
        >>> p12 = to_planes(eq1 & eq2)
        >>> p1 = to_plane(eq1)
        >>> p12[0] == p1
        True
        >>> p2 = to_plane(eq2)
        >>> p12[1] == p2
        True

    """
    expressions = split_expression(expr)
    return [to_plane(e) for e in expressions]


def to_plane(expr):
    """
    Tranlate the expression (coordinate form) to normal form  and return as Plane
    Examples:
        Get 3-d plane for linear equations
        >>> import sympy
        >>> from tfields.lib.symbolics import to_plane
        >>> x, y, z = sympy.symbols('x y z')
        >>> eq1 = 2*x - 4
        >>> p1 = to_plane(eq1)
        >>> assert eq1, p1.equation()

        # multiple dimensions work
        >>> eq2 = x + 2*y + 3*z - 4
        >>> p2 = to_plane(eq2)
        >>> assert eq2, p2.equation()

        The base point is calculated independent of the coords
        >>> eq3 = 2*y + 3*z - 4
        >>> p3 = to_plane(eq3)
        >>> assert eq3, p3.equation()

        Inequalities will be treated like equations
        >>> ie1 = 2*y + 3*z > 4
        >>> p4 = to_plane(ie1)
        >>> assert ie1.lhs - ie1.rhs, p4.equation()

    Returns: sympy.Plane
    """
    x, y, z = sympy.symbols('x y z')

    # convert inequalities
    if "Than" in str(expr.__class__):
        expr = expr.rhs - expr.lhs

    poly = expr.as_poly(x, y, z, domain='RR')
    if poly is None:
        raise ValueError("Expression {expr} can not be described as a polygon."
                         .format(**locals()))

    coords = (x, y, z)
    degrees = tuple(poly.degree(c) for c in coords)

    if any([d > 1 for d in degrees]):
        raise TypeError("Expression {0} can not be represented as plane"
                        "since the poly dimension is > 1 for one variable!"
                        .format(expr))

    norm = tuple(expr.coeff(coord) for coord in coords)

    # now we need any point on the plane
    # find the variable to solve for
    reduced_expr = expr.copy()
    non_zero_coord = None
    for coord, degree in zip(coords, degrees):
        if degree == 0 or non_zero_coord is not None:
            if degree > 0:
                reduced_expr = reduced_expr.subs(coord, 0.)
        else:
            non_zero_coord = coord
    non_zero_value = sympy.solve(reduced_expr, non_zero_coord)[0]
    point = sympy.Point3D(*[non_zero_value if non_zero_coord == coord else 0.
                            for coord in coords])

    return sympy.Plane(point, normal_vector=norm)
