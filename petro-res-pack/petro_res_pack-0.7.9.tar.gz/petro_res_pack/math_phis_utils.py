import numpy as np
from .parsing_utils import two_dim_index_to_one
from .res_state import ResState, Properties
import scipy.sparse as sparse


def one_zero_swap(x: int) -> int:
    """
    covering for transforming one to zero
    Args:
        x: int, 1 or 0

    Returns: 0 or 1

    """
    return 1 - x


def get_ax_update(state: ResState, prop: Properties, axis: int) -> np.ndarray:
    """
    For making numerical schemes boundary values are mixed with inner, so this is a mixer
    Args:
        state: reservoir param, for example pressure or saturation
        prop: properties of reservoir (only .nx, .ny are needed)
        axis: if this is for x or y axis

    Returns: cells with values are intersecting for fluid flow over specified axis are
     in neighbouring cells

     for example having
     [[0, 1, 2, 3],
      [3, 4, 5]]
      as pressure vector. and -1 is boundary value
      then full picture is
      [[-1, -1, -1, -1, -1],
       [-1,  0,  1,  2, -1]
       [-1,  3,  4,  5, -1]
       [-1, -1, -1, -1, -1]]
    and values for update along 0-axis are just sequence of boarding elements along 0-axis
    [-1,  0,  1,  2, -1,  3,  4,  5, -1]
    just every REAL element is surrounded by its neighbours (not real too)
    same stuff for 1-axis
    [-1,  0,  3, -1,  1,  4, -1,  2,  5, -1]
    """
    if axis == 0:
        out_bound = np.ones((prop.nx, 1)) * state.bound_v
    elif axis == 1:
        out_bound = np.ones((1, prop.ny)) * state.bound_v
    else:
        assert False

    out = np.append(state.v.reshape((prop.nx, prop.ny)), out_bound, axis=one_zero_swap(axis))
    if axis == 0:
        out = out.reshape(-1)
    elif axis == 1:
        out = out.T.reshape(-1)
    out = np.insert(out, 0, state.bound_v)
    return out


def chose_sat_for_upd(p: np.ndarray, s: np.ndarray) -> np.ndarray:
    """
    Provided with values composed in the following way: the fluid motion (along arbitrary axis)
    is forced by difference in it values (pressures moves, difference in saturation stops moving)
    the func chooses direction (by pressure) and selects main saturation value, which is cell with greater pressure.
    arguments are 1d vectors, just like
    p =   [4,  5,  1,  8, -1, 17, 25,  9,  0]
    s =   [1,  2,  3,  4,  5,  6,  7,  8,  9]
    so main saturation, which defines relative permeability is
    s_main = [2,  2,  4,  4,  6,  7,  7,  8]
    Args:
        p: vector of pressures, shuffled in special (mentioned above) way
        s: vector of saturation, shuffled in special (mentioned above) way

    Returns: array of saturation needed to calculate relative permeability
    (cell with biggest pressure)

    """
    comp_p_get_s = np.dtype({'names': ['p1', 'p2', 's1', 's2'],
                             'formats': [np.double,
                                         np.double,
                                         np.double,
                                         np.double]})
    p_df = np.zeros(len(p) - 1, dtype=comp_p_get_s)
    p_df['p1'] = p[:-1]
    p_df['p2'] = p[1:]

    p_df['s1'] = s[:-1]
    p_df['s2'] = s[1:]

    out = np.where(p_df['p1'] >= p_df['p2'], p_df['s1'], p_df['s2'])
    return out


def build_main_diagonal(k_rel_x, k_rel_y, ph: str,  prop: Properties) -> np.ndarray:
    """
    builder of main diagonal for laplacian
    Args:
        k_rel_x: relative permeabilities for x-axis flow
        k_rel_y: relative permeabilities for y-axis flow
        ph: phase, 'o' or 'w' (oil or water)
        prop: properties of reservoir

    Returns: vecor wich is a diagonal

    """
    main_dia = np.zeros(prop.nx * prop.ny)
    main_dia += np.delete(k_rel_x.reshape((prop.nx, prop.ny + 1)), obj=-1, axis=1).reshape(-1)
    main_dia += np.delete(k_rel_x.reshape((prop.nx, prop.ny + 1)), obj=0, axis=1).reshape(-1)

    main_dia += np.delete(k_rel_y.reshape((prop.ny, prop.nx + 1)), obj=-1, axis=1).T.reshape(-1)
    main_dia += np.delete(k_rel_y.reshape((prop.ny, prop.nx + 1)), obj=0, axis=1).T.reshape(-1)
    main_dia *= prop.k * prop.d * prop.dy / prop.mu[ph] / prop.dx
    return main_dia


def build_close_diagonal(k_rel_x, ph: str, prop: Properties) -> np.ndarray:
    """
        builder of second diagonal (x -axis flow) for laplacian
        Args:
            k_rel_x: relative permeabilities for x-axis flow
            ph: phase, 'o' or 'w' (oil or water)
            prop: properties of reservoir

        Returns: vector which is a second diagonal

        """
    close_dia = k_rel_x.reshape((prop.nx, prop.ny + 1))
    close_dia = np.delete(close_dia, obj=-1, axis=1)
    close_dia = close_dia.reshape(-1)
    close_dia *= prop.mask_close
    close_dia *= prop.k * prop.d * prop.dy / prop.mu[ph] / prop.dx
    return close_dia


def build_dist_diagonal(k_rel_y, ph, prop):
    """
        builder of the most distant (y-axis flow) diagonal for laplacian
        Args:
            k_rel_y: relative permeabilities for y-axis flow
            ph: phase, 'o' or 'w' (oil or water)
            prop: properties of reservoir

        Returns: vector which is a diagonal

        """
    dist_dia = k_rel_y.reshape((prop.ny, prop.nx + 1))
    dist_dia = np.delete(dist_dia, obj=-1, axis=1)
    dist_dia = np.delete(dist_dia, obj=0, axis=1)
    dist_dia = dist_dia.T.reshape(-1)
    dist_dia *= prop.k * prop.d * prop.dy / prop.mu[ph] / prop.dx
    return dist_dia


def get_laplace_one_ph(p: ResState, s: ResState, ph: str, prop: Properties) -> [np.ndarray, float]:
    """
    Function creates laplacian matrix for given reservoir state
    Args:
        p: reservoir pressure
        s: reservoir saturation
        ph: phase, 'o' or 'w'
        prop: properties of reservoir

    Returns: laplacian matrix for update and sigma - important value for time step estimation

    """
    s_x_ext = get_ax_update(s, prop, axis=0)
    p_x_ext = get_ax_update(p, prop, axis=0)
    sat_x = chose_sat_for_upd(p=p_x_ext, s=s_x_ext)

    k_rel_x = prop.k_rel_by_ph(sat_x, ph)
    sigma = k_rel_x.max()
    ##############################################

    s_y_ext = get_ax_update(s, prop, axis=1)
    p_y_ext = get_ax_update(p, prop, axis=1)
    sat_y = chose_sat_for_upd(p=p_y_ext, s=s_y_ext)

    k_rel_y = prop.k_rel_by_ph(sat_y, ph)
    sigma = min(sigma, k_rel_y.max())

    # let's go diagonals
    # main is first
    # for x we need to drop first and last col
    main_dia = build_main_diagonal(k_rel_x, k_rel_y, ph, prop)
    close_dia = build_close_diagonal(k_rel_x, ph, prop)
    dist_dia = build_dist_diagonal(k_rel_y, ph, prop)

    laplacian = sparse.diags(diagonals=[dist_dia, close_dia[1:],
                                        -1 * main_dia,
                                        close_dia[1:], dist_dia
                                        ],
                             offsets=[-1 * prop.ny, -1, 0, 1, prop.ny])
    sigma *= prop.k * prop.d * prop.dy / prop.mu[ph] / prop.dx
    return laplacian, sigma


def get_j_matrix(s: ResState, p: ResState, pos_r: dict, ph: str, prop: Properties, openness: np.ndarray,
                 j_matrix: np.ndarray) -> None:
    """
    over write J matrix as from lectures
    Args:
        s: saturation of reservoir
        p: pressure in reservoir
        pos_r: dictionary position -> radius of wells
        ph: phase "o" (oil) or "w" (water)
        prop: properties of reservoir
        openness: openness of each well. 1 if in sell there is no well
        j_matrix: matrix from lectures, will be over wrote

    Returns: nothing

    """

    r_ref = get_r_ref(prop)
    for pos in pos_r:
        dia_pos = two_dim_index_to_one(i=pos[0], j=pos[1], ny=prop.ny)
        _p = 4 * np.pi * prop.k / prop.b[ph] / prop.mu[ph]
        _p *= r_ref * pos_r[pos]
        _p /= (r_ref - pos_r[pos])

        _p *= prop.k_rel_ph_local_pressure_decision(s_1=s[pos[0], pos[1]], s_2=s[pos[0], pos[1]],
                                                    p_1=p[pos[0], pos[1]], p_2=p[pos[0], pos[1]],
                                                    ph=ph)

        j_matrix[dia_pos] = _p
    j_matrix *= openness
    # return out.reshape((prop.nx * prop.ny, 1))


def get_r_ref(prop: Properties) -> float:
    """
    For estimating flow to well it's necessary to define radius on which initial condition (solve derivatives)
    matches
    Args:
        prop: properties of reservoir

    Returns:

    """
    return 1 / (1 / prop.dx + np.pi / prop.d)


def get_q_bound(p: ResState, s: ResState, ph: str, prop: Properties) -> np.ndarray:
    """
    q from bounds into reservoir
    Args:
        p: pressure as ResState
        s: saturation as ResState
        ph: phase, "o" (oil) or "w" (water)
        prop: properties of reservoir

    Returns: vector dimension just as p.v.shape (nx *ny, 1)

    """
    q_b = np.zeros((prop.nx * prop.ny, 1))
    for row in range(prop.nx):
        # (row, -0.5)
        k_r = prop.k_rel_ph_local_pressure_decision(s_1=s[row, -0.5], s_2=s[row, 0],
                                                    p_1=p[row, -0.5], p_2=p[row, 0],
                                                    ph=ph)

        dia_ = two_dim_index_to_one(i=row, j=0, ny=prop.ny)
        q_b[dia_, 0] += prop.k * k_r / prop.dx * p[row, -0.5] * prop.d * prop.dy / prop.mu[ph]
        # (row, ny-0.5)
        k_r = prop.k_rel_ph_local_pressure_decision(s_1=s[row, prop.ny - 1], s_2=s[row, prop.ny - 0.5],
                                                    p_1=p[row, prop.ny - 1], p_2=p[row, prop.ny - 0.5],
                                                    ph=ph)
        dia_ = two_dim_index_to_one(i=row, j=prop.ny - 1, ny=prop.ny)
        q_b[dia_, 0] += prop.k * k_r / prop.dx * p[row, prop.ny - 0.5] * prop.d * prop.dy / prop.mu[ph]

    for col in range(prop.ny):
        # (-0.5, col)
        k_r = prop.k_rel_ph_local_pressure_decision(s_1=s[-0.5, col], s_2=s[0, col],
                                                    p_1=p[-0.5, col], p_2=p[0, col],
                                                    ph=ph)
        dia_ = two_dim_index_to_one(i=0, j=col, ny=prop.ny)
        q_b[dia_, 0] += prop.k * k_r / prop.dx * p[prop.nx - 0.5, col] * prop.d * prop.dy / prop.mu[ph]
        # (nx-0.5, col)
        k_r = prop.k_rel_ph_local_pressure_decision(s_1=s[prop.nx - 1, col], s_2=s[prop.nx - 0.5, col],
                                                    p_1=p[prop.nx - 1, col], p_2=p[prop.nx - 0.5, col],
                                                    ph=ph)
        dia_ = two_dim_index_to_one(i=prop.nx - 1, j=col, ny=prop.ny)
        q_b[dia_, 0] += prop.k * k_r / prop.dx * p[prop.nx - 0.5, col] * prop.d * prop.dy / prop.mu[ph]
        # corners to zero
    # return q_b.reshape((prop.nx * prop.ny, 1))
    return q_b