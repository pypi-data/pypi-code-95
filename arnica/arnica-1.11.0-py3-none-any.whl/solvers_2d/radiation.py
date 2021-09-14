""" Module to test the p1 (radiation) solver for grey gas """

import numpy as np
import scipy.sparse as scp
import scipy.sparse.linalg as linalg
import arnica.utils.mesh_tool as msh
from arnica.solvers_2d.core_fd import Metrics2d
from arnica.solvers_2d import boundary as bndy
from arnica.utils.nparray2xmf import NpArray2Xmf

def filter_stupid_characters(string):
    """filter_stupid_characters"""
    for char in ["$", "\\", " ", "__", "___"]:
        string = string.replace(char, "_")

    if string.startswith("_"):
        string = string[1:-1]

    return string

def get_p1_eq_field(metric, absorption_coeff, spectral_radiance):
    """
    Create the LHS matrix corresponding to P1 equation

    Parameters
    ----------
    metric : an instance of the class Metrics2d containing the gradient operators
    absorption_coeff : absorption coefficient of shape (size_ns * size_we)
    spectral_radiance : field of spectral radiation (size_ns * size_we)

    Returns
    -------
    LHS matrix
    """

    # Left Hand Side
    grad_x = metric.grad_x.toarray()
    grad_y = metric.grad_y.toarray()

    alpha = 1. / absorption_coeff
    beta = - 3. * absorption_coeff

    # div (alpha * grad(.)) operator
    alpha_mat = np.diag(alpha.ravel())
    a_grad_x = np.dot(alpha_mat, grad_x)
    a_grad_y = np.dot(alpha_mat, grad_y)
    term1 = np.dot(grad_x, a_grad_x) + np.dot(grad_y, a_grad_y)

    # (beta * .) operator
    term2 = np.diag(beta.ravel())

    lhs = term1 + term2

    # Right-Hand Side
    abs_gas = absorption_coeff.ravel()
    spec_rad = spectral_radiance.ravel()
    rhs = -12. * np.pi * abs_gas * spec_rad

    return lhs, rhs


def get_p1_eq_field_csr(metric, absorption_coeff, spectral_radiance):
    """
    Create the LHS matrix corresponding to P1 equation
    Book --> Radiative Heat Transfer (Modest, p. 479)
    Parameters
    ----------
    metric : an instance of the class Metrics containing the gradient operators
    absorption_coeff : absorption coefficient of shape (size_ns * size_we)
    spectral_radiance : field of spectral radiation (size_ns * size_we)

    Returns
    -------
    LHS matrix
    """

    # Left Hand Side
    grad_x = metric.grad_x_csr
    grad_y = metric.grad_y_csr

    alpha = 1. / absorption_coeff
    beta = - 3. * absorption_coeff

    # div (alpha * grad(.)) operator
    alpha_mat = scp.csr_matrix(np.diag(alpha.ravel()))
    a_grad_x = alpha_mat.dot(grad_x)
    a_grad_y = alpha_mat.dot(grad_y)
    term1 = grad_x.dot(a_grad_x) + grad_y.dot(a_grad_y)

    # (beta * .) operator
    term2 = scp.csr_matrix(np.diag(beta.ravel()))

    lhs = term1 + term2

    # Right-Hand Side
    abs_gas = absorption_coeff.ravel()
    spec_rad = spectral_radiance.ravel()
    rhs = -12. * np.pi * abs_gas * spec_rad

    return lhs, rhs


def analytical_temperature(abs_coeff, radius, temp_1, temp_2):
    """
    Analytical temperature profile for P1.
    Book --> Radiative Heat Transfer (Modest, p. 479)

    Parameters
    ----------
    abs_coeff : absorption coefficient
    radius : radial coordinates
    temp_1 : temperature of inner cylinder
    temp_2 : temperature of outer cylinder

    Returns
    -------
    Analytical temperature field
    """
    tau1 = abs_coeff * np.amin(radius)
    tau2 = abs_coeff * np.amax(radius)
    tau = abs_coeff * radius

    num = 1. + 3. / 2. * tau2 * np.log(tau2 / tau)
    denum = 1. + tau2 / tau1 + 3. / 2. * tau2 * np.log(tau2 / tau1)

    phi = ((temp_1 ** 4. - temp_2 ** 4.) * num / denum + temp_2 ** 4.)
    phi = phi ** (1. / 4.)

    return phi


def dump_solution(metric, incident_radiation_sol, s_r_sum, s_r_div,
                  analytic_spectral_radiance, analytic_temperature, q_r_flux):
    """
    Dump generic postprocessing data

    Parameters
    ----------
    metric: metric object
    incident_radiation_sol: G field
    S_r_sum: radiative source term computed using method 1 (cf function)
    S_r_div: radiative source term computed using method 2 (cf function)
    analytic_spectral_radiance: Ib calculated from analytic_temperature
    analytic_temperature: initial temperature
    q_r_flux: radiative heat flux (x, y and normal)

    Returns
    -------
    None
    """
    out_h5 = NpArray2Xmf("radiation_solution.h5")
    out_h5.create_grid(metric.x_coor, metric.y_coor,
                       np.zeros(metric.shp2d))

    # Inputs
    out_h5.add_field(analytic_spectral_radiance, "Ib_gas")
    out_h5.add_field(analytic_temperature, "T_init")

    # Output
    out_h5.add_field(incident_radiation_sol, "G")

    # Post-processing data
    q_r_x = q_r_flux[0].reshape(metric.shp2d)
    q_r_y = q_r_flux[1].reshape(metric.shp2d)
    q_r_n = q_r_flux[2].reshape(metric.shp2d)
    out_h5.add_field(s_r_sum, "Sr")
    out_h5.add_field(s_r_div.reshape(metric.shp2d), "S_r_div")
    out_h5.add_field(q_r_x, "Heat flux x")
    out_h5.add_field(q_r_y, "Heat flux y")
    out_h5.add_field(q_r_n, "Heat flux normal")
    out_h5.dump()


def dump_solution_test_case(metric, q_r_flux, params):
    """
    Dump Analytical-test-case-related data.

    Parameters
    ----------
    metric: metric object
    q_r_flux: heat flux
    params: dict of parameters

    Returns
    -------
    None
    """
    # Analytical test case
    out_h5 = NpArray2Xmf("radiation_solution_test_case.h5")
    out_h5.create_grid(metric.x_coor, metric.y_coor, np.zeros(metric.shp2d))
    adim_flux_x = adim_flux_test_case(q_r_flux[0].reshape(metric.shp2d),
                                      params)
    adim_flux_y = adim_flux_test_case(q_r_flux[1].reshape(metric.shp2d),
                                      params)
    adim_flux_n = adim_flux_test_case(q_r_flux[2].reshape(metric.shp2d),
                                      params)
    out_h5.add_field(adim_flux_x, "Adim heat flux x")
    out_h5.add_field(adim_flux_y, "Adim heat flux y")
    out_h5.add_field(adim_flux_n, "Adim heat flux normal")
    out_h5.dump()



def get_heat_flux_inner(x_coor, y_coor, q_n):
    """get_heat_flux_inner"""
    rad = np.sqrt(x_coor ** 2. + y_coor ** 2.)
    r_min = 1.
    tol = 1e-7

    mask = np.where(rad < r_min + tol)
    idx = np.argmin(x_coor[mask])
    heat_flux_inner = q_n[mask]

    return float(-1. * heat_flux_inner[idx])


def get_heat_source_term(g_solution, absorption_coefficient,
                         spectral_radiance):
    """
    Computes radiative heat source term

    Parameters
    ----------
    g_solution : solution of incident radiation
    absorption_coefficient: field of absorption coefficient
    spectral_radiance: field of spectral radiance

    Returns
    -------
    heat source term
    """
    print("\t>> Compute radiative energy source term")
    radiative_source_term = 4. * np.pi * spectral_radiance - g_solution
    radiative_source_term *= absorption_coefficient
    return radiative_source_term


def get_source_term_div(heat_fluxes, metric):
    """
    Compute the radiative in the conventional way by taking the divergence of
    the radiative heat flux vector

    Parameters
    ----------
    heat_fluxes: numpy arrays containing heat fluxes in x, y, and projected
    onto the boundaries
    metric: object containing information relative to metric (gradients,
    coordinates, etc.)

    Returns
    source_term: radiative source term
    -------

    """
    q_x = heat_fluxes[0]
    q_y = heat_fluxes[1]

    grad_x = metric.grad_x_csr
    grad_y = metric.grad_y_csr
    radiative_source_term_div = grad_x.dot(q_x) + grad_y.dot(q_y)

    return radiative_source_term_div


def get_heat_fluxes(absorption_coefficient, metric, g_solution):
    """
    Computes radiative heat fluxes

    Parameters
    ----------
    absorption_coefficient
    metric : Metrics object
    g_solution : solution of incident radiation

    Returns
    -------

    x and y heat fluxes
    """

    print("\n\t\t>> Compute heat fluxes")
    alpha = 1. / absorption_coefficient

    gamma = np.diag((-alpha.ravel() / 3.))
    gamma_csr = scp.csr_matrix(gamma)

    gamma_grad_x = gamma_csr.dot(metric.grad_x_csr)
    gamma_grad_y = gamma_csr.dot(metric.grad_y_csr)

    g_sol_csr = g_solution.ravel()

    heat_flux_x = gamma_grad_x.dot(g_sol_csr)
    heat_flux_y = gamma_grad_y.dot(g_sol_csr)

    heat_flux_n_bc = metric.n_x.dot(heat_flux_x) + metric.n_y.dot(
        heat_flux_y)

    return heat_flux_x, heat_flux_y, heat_flux_n_bc


def analytical_test_case(metric, params):
    """
    This functions returns fields corresponding to the 2 concentric
    cylinder with grey gas (Modest's book, 2nd edition, p. 477)

    Parameters
    ----------
    metric: metric object
    params: dict of parameters

    Returns
    -------
    analytic_temperature: temperature field
    analytic_spectral_radiance: spectral radance compute from temperature
    absorption_field: absorption coefficient field
    """

    t_west = params["boundaries"]["West"]["Values"]["Wall_temperature"]
    t_east = params["boundaries"]["East"]["Values"]["Wall_temperature"]

    radius = np.sqrt(metric.x_coor ** 2. + metric.y_coor ** 2.)
    print("\n\t--> Compute temperature field")

    analytic_temperature = analytical_temperature(
        params["field"]["absorption_coefficient"], radius, t_west, t_east)

    print("\n\t--> Compute spectral radiance")
    analytic_spectral_radiance = get_spectral_radiance(analytic_temperature)

    kappa_cst = params["field"]["absorption_coefficient"]
    absorption_field = np.ones_like(metric.x_coor) * kappa_cst

    return analytic_temperature, analytic_spectral_radiance, absorption_field


def temperature_slope(x_coor, y_coor, t_hot, t_cold, mesh_kind):
    """
    Compute initial temperature field as a temperature slope
    Parameters
    ----------
    x_coor:  x coordinates
    y_coor: y coordinates
    t_hot: higher value of temperature
    t_cold: lower value of temperature
    mesh_kind: mesh kind (either 'cyl' or 'rect'

    Returns
    -------
    temperature field (same shape that x_coor)
    """

    temperature = np.zeros_like(x_coor)

    if mesh_kind == "cyl":
        radius = np.sqrt(np.square(x_coor) + np.square(y_coor))
        temperature = (t_hot - t_cold) * (radius - 1) + t_cold
    elif mesh_kind == "rect":
        temperature = (t_hot - t_cold) * x_coor + t_cold

    return temperature


def get_spectral_radiance(temp):
    """
    Compute blackbody thermal radiation intensity
    Parameters
    ----------
    temp : temperature

    Returns
    -------
    blackbody thermal radiation intensity
    """
    sigma = 5.670373e-8
    return temp ** 4. / np.pi * sigma


def postproc_radiation(metric, incident_radiation_sol, absorption_field,
                       analytic_spectral_radiance):
    """
    Generic post proc for P1 solver

    Parameters
    ----------
    metric: object containing metrics (coord, gradients, etc.)
    incident_radiation_sol: G solution
    absorption_field: kappa field
    analytic_spectral_radiance: Ib for test case

    Returns
    -------
    Radiative heat fluxes and source terms
    """

    heat_fluxes = get_heat_fluxes(absorption_field, metric,
                                  incident_radiation_sol)

    # There are 2 ways of computing the radiative source term
    # Way 1 : Eq. (5) in :
    #
    #   "C. Paul, D. C. Haworth, and M. F. Modest. A simplified CFD model
    #    for spectral radiative heat transfer in high-pressure
    #    hydrocarbon-air combustion systems. Proc. Combust. Inst.,
    #    000 :1–8, 2018.
    radiative_source_term = get_heat_source_term(incident_radiation_sol,
                                                 absorption_field,
                                                 analytic_spectral_radiance)

    # Way 2 : Generic definition of the flux S_r = - div(q_r)
    #
    #   "M.F. Modest , D.C. Haworth , Radiative Heat Transfer in Turbulent
    #    Combustion Systems , Springer, 2016."
    radiative_source_term_div = get_source_term_div(heat_fluxes, metric)

    return heat_fluxes, radiative_source_term, radiative_source_term_div


def postproc_analytical_test_case(metric, params, heat_fluxes):
    """
    This functions returns the non dimensional normal heat flux of the inner
    cylinder in the analytices test case (2 concentric cylinders with grey gas
    (Modest's book, 2nd edition, p. 477))

    Returns
    -------
    Non-dimensional normal heat flux at the inner cylinder wall.
    """
    q_n = adim_flux_test_case(heat_fluxes[2].reshape(metric.shp2d), params)
    heat_flux_scalar = get_heat_flux_inner(metric.x_coor, metric.y_coor, q_n)

    return heat_flux_scalar


def adim_flux_test_case(dim_data, params):
    """
    Non-dimensional conversion of heat fluxes

    Parameters
    ----------
    dim_data: dimensional data
    params: parameter dictionary

    Returns
    -------
    non dimensional data
    """

    def adim_factor(temp1, temp2):
        """
        Factor use to non-dimensionalize results

        Parameters
        ----------
        temp1: temperature of cylinder one
        temp2: temperature of cylinder two

        Returns
        -------
        factor to adimensionalize data as in analytical test case
        """
        sigma = 5.670373e-8
        return 1. / (sigma * (temp1 ** 4. - temp2 ** 4.))

    t_west = params["boundaries"]["West"]["Values"]["Wall_temperature"]
    t_east = params["boundaries"]["East"]["Values"]["Wall_temperature"]
    factor = adim_factor(t_west, t_east)
    return dim_data * factor


def compute_robin_values_p1(absorption_coeff, t_wall, emissivity=1):
    """
    Compute values of the Marshak boundary condition in the Robin formalism:

                    a * (df / dn) + b * f + c = O

    Parameters
    ----------
    absorption_coeff: absorption coefficient field
    t_wall: temperature of the boundary wall
    emissivity: emissivity of the wall (1 if it is a black body)

    Returns
    -------
    a_value: pre-normal-derivative coefficient
    b_value: f-linear coefficient
    c_value: constant coefficient (does not depend on f)
    """

    a_value = (2. - emissivity) / emissivity * 2.
    a_value /= (3. * absorption_coeff)
    b_value = 1.
    c_value = - 4. * np.pi * get_spectral_radiance(t_wall)

    return a_value, b_value, c_value


def set_bc_p1(bc_params, absorption_coeff):
    """
    Apply Marshak boundary conditions for the P1 solver from physical params

    Parameters
    ----------
    bc_params: dictionary of boundary parameters
    absorption_coeff: absorption coefficient field

    Returns
    -------
    bc_params: updated dictionary of boundary parameters
    """

    for _, bc_dict in bc_params.items():

        if bc_dict["type"] == 'Robin':
            t_wall = bc_dict["Values"]["Wall_temperature"]

            if "Emissivity" in bc_dict["Values"].keys():
                emissivity = bc_dict["Values"]["Emissivity"]
                bc_val = compute_robin_values_p1(absorption_coeff, t_wall,
                                                 emissivity=emissivity)
            else:
                # Treat wall as black wall by default
                bc_val = compute_robin_values_p1(absorption_coeff, t_wall)

            bc_dict["bc_values"] = bc_val

    return bc_params


def main_p1_solver(params):
    """
    Radiation solver (P1 Approximation)

    Parameters :
    ------------
    params : dict of setup parameters

    """
    print("\n\tmain ---> Generate Grid")
    x_coor, y_coor = msh.get_mesh(params["mesh"])

    if "dilate_grid" in params.keys():
        if params["dilate_grid"]:
            x_coor, y_coor, _ = msh.dilate_center(x_coor, y_coor)

    print("\n\tmain ---> Define Boundaries")
    bnd = bndy.Boundary2d(params["boundaries"])

    print("\n\tmain ---> Compute Metrics")
    metric = Metrics2d(x_coor, y_coor, periodic_ns=bnd.periodic_ns,
                       periodic_we=bnd.periodic_we)

    fields = analytical_test_case(metric, params)
    analytic_temperature, analytic_spectral_radiance, absorption_field = fields

    print("\n\tmain --> Build LHS and RHS")
    lhs_csr, rhs_csr = get_p1_eq_field_csr(metric, absorption_field,
                                           analytic_spectral_radiance)

    print("\n\tmain ---> Apply BC")
    # We take the mean value of the absorption_field so far (ok for grey gas)
    params["boundaries"] = set_bc_p1(params["boundaries"],
                                     np.mean(absorption_field))

    lhs_csr_bc, rhs_csr_bc = bndy.apply_bc(lhs_csr, rhs_csr, metric,
                                           params["boundaries"])

    print("\n\tmain ---> Solving...")
    solution_1d, _ = linalg.bicgstab(lhs_csr_bc, rhs_csr_bc, atol='legacy')
    incident_radiation_sol = solution_1d.reshape(metric.shp2d)

    print("\n\tmain ---> Postproc...")
    q_r_flux, s_r_sum, s_r_div = postproc_radiation(metric,
                                                    incident_radiation_sol,
                                                    absorption_field,
                                                    analytic_spectral_radiance)

    heat_flux_scalar = postproc_analytical_test_case(metric, params, q_r_flux)

    print("\n\tmain ---> Write Solution")
    dump_solution(metric, incident_radiation_sol, s_r_sum, s_r_div,
                  analytic_spectral_radiance, analytic_temperature, q_r_flux)

    dump_solution_test_case(metric, q_r_flux, params)

    results = {}
    results['solution_1d'] = solution_1d
    results['incident_radiation_sol'] = incident_radiation_sol
    results['q_r_flux'] = q_r_flux
    results['s_r_sum'] = s_r_sum
    results['s_r_div'] = s_r_div
    results['heat_flux_scalar'] = heat_flux_scalar

    print("\n\tmain --> Done! =)")

    return heat_flux_scalar, results


if __name__ == "__main__":
    T_WEST = 500.
    T_EAST = 1500.

    # Mesh definition
    MESH_RECT = {"kind": 'rect',
                 "x_max": 1.,
                 "y_max": 1.,
                 "x_res": 5.,
                 "y_res": 6.,
                 }

    MESH_CYL = {"kind": 'cyl',
                "r_min": 1.,
                "r_max": 2.,
                "theta_min": 0.,
                "theta_max": 2. * np.pi,
                "n_pts_rad": 15
                }

    # Boundary conditions
    # Default
    BOUNDARY = {"North": {"type": "Periodic", 'Values': {}},
                "West": {"type": "Periodic", 'Values': {}},
                "South": {"type": "Periodic", 'Values': {}},
                "East": {"type": "Periodic", 'Values': {}}}

    BOUNDARY["West"]["type"] = "Robin"
    BOUNDARY["West"]["Values"] = {"Emissivity": 1.,
                                  "Wall_temperature": 500.}

    BOUNDARY["East"]["type"] = "Robin"
    BOUNDARY["East"]["Values"] = {"Emissivity": 1.,
                                  "Wall_temperature": 1500.}

    # Input fields: Temperature, pressure, etc.
    FIELD = {"absorption_coefficient": 1.,
             "temperature": [T_WEST, T_EAST]}

    # Create parameter dictionary
    PARAMS = {}
    PARAMS["boundaries"] = BOUNDARY
    PARAMS["field"] = FIELD

    # Setup simulation with rectangular mesh
    # PARAMS["mesh"] = MESH_RECT

    # Setup simulation with cylindrical mesh
    PARAMS["mesh"] = MESH_CYL

    # emissivity = PARAMS["boundaries"]["Values"]["Emissivity"]
    # t_wall = PARAMS["boundaries"][["Values"]["Wall_temperature"]

    Q_INNER = main_p1_solver(PARAMS)
