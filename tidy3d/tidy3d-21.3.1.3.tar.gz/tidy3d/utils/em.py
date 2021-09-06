import numpy as np

from . import log_and_raise


def poynting_avg(E, H):
    """Compute the time-averaged Poynting vector that gives the energy
    flow per unit area per unit time at every point. ``E`` and ``H`` are
    assumed to be arrays of the same shape, as returned by frequency
    monitors. The first dimension is the field polarization (x, y, z), and
    must have size 3. The last dimension is the number of frequencies.
    """

    if E.shape != H.shape:
        log_and_raise("E and H must have the same dimension.", ValueError)
    if E.shape[0] != 3:
        log_and_raise("First dimension of fields must have size 3.", ValueError)

    return 1 / 2 * np.real(np.cross(E, np.conj(H), axis=0))


def poynting_insta(E, H):
    """Compute the instantaneous Poynting vector that gives the energy
    flow per unit area per unit time at every point in space and time.
    ``E`` and ``H`` are assumed to be arrays of the same shape, as returned by
    time monitors. The first dimension is the field polarization (x, y, z),
    and must have size 3. The last dimension is the number of time steps.
    """

    if E.shape != H.shape:
        log_and_raise("E and H must have the same dimension.", ValueError)
    if E.shape[0] != 3:
        log_and_raise("First dimension of fields must have size 3.", ValueError)

    return np.cross(E, H, axis=0)


def dft_spectrum(time_series, dt, freqs):
    """Computes the frequency spectrum associated to a time series directly
    using the discrete fourier transform.

    Note
    ----
    The DFT spectrum can be computed over an arbitrary list of frequencies,
    but is much more inefficient than FFT. Use sparingly.

    Parameters
    ----------
    time_series: array_like
        1D array of time-dependent data.
    dt : float, optional
        Step in time over which the time series is recorded.
    freqs : array_like
        Array of frequencies to sample the spectrum at.

    Returns
    -------
    spectrum : array_like
        Array of same size as ``freqs`` giving the complex-valued spectrum.
    """

    frs = np.array(freqs)
    tdep = np.array(time_series)
    tmesh = np.arange(tdep.size) * dt
    spectrum = np.sum(
        tdep[:, np.newaxis] * np.exp(2j * np.pi * frs[np.newaxis, :] * tmesh[:, np.newaxis]),
        0,
    ).ravel()

    return dt / np.sqrt(2 * np.pi) * spectrum


def x_to_center(Ex):
    """Interpolate Ex positions to the center of a Yee lattice"""
    return (Ex + np.roll(Ex, -1, 1) + np.roll(Ex, -1, 2) + np.roll(np.roll(Ex, -1, 1), -1, 2)) / 4


def y_to_center(Ey):
    """Interpolate Ey positions to the center of a Yee lattice"""
    return (Ey + np.roll(Ey, -1, 0) + np.roll(Ey, -1, 2) + np.roll(np.roll(Ey, -1, 0), -1, 2)) / 4


def z_to_center(Ez):
    """Interpolate Ez positions to the center of a Yee lattice"""
    return (Ez + np.roll(Ez, -1, 0) + np.roll(Ez, -1, 1) + np.roll(np.roll(Ez, -1, 0), -1, 1)) / 4


def E_to_center(E):
    """Interpolate an E-field array of shape (3, Nx, Ny, Nz, ...) to the
    center of the Yee grid. Returns array of same shape."""

    Ex_interp = x_to_center(E[0, ...])
    Ey_interp = y_to_center(E[1, ...])
    Ez_interp = z_to_center(E[2, ...])

    return np.stack((Ex_interp, Ey_interp, Ez_interp), axis=0)


def H_to_center(H):
    """Interpolate an H-field array of shape (3, Nx, Ny, Nz, ...) to the
    center of the Yee grid. Returns array of same shape."""

    Hx_interp = (H[0, ...] + np.roll(H[0, ...], -1, 1)) / 2
    Hy_interp = (H[1, ...] + np.roll(H[1, ...], -1, 2)) / 2
    Hz_interp = (H[2, ...] + np.roll(H[2, ...], -1, 3)) / 2

    return np.stack((Hx_interp, Hy_interp, Hz_interp), axis=0)


def eps_to_center(eps_xx, eps_yy, eps_zz):
    """Interpolate eps_r to the center of the Yee lattice."""

    # # Simple averaging of one x, y, z values per cell.
    # return (eps_xx + eps_yy + eps_zz)/3

    # Average all 4 eps_xx, 4 eps_yy, and 4 eps_zz values around the
    # cell center, similar to the monitor field recording.
    return (x_to_center(eps_xx) + y_to_center(eps_yy) + z_to_center(eps_zz)) / 3


def expand_syms(sim, E, H, span_inds, mesh):
    """Expand E field based on simulation symmetries, if touching a symmetry
    plane.

    Parameters
    ----------
    sim : Simulation
        Simulation to which the field relates.
    E : np.ndarray
        Shape (3, Nx, Ny, Nz, Ns).
    H : np.ndarray
        Shape (3, Nx, Ny, Nz, Ns).
    span_inds : np.ndarray
        Indexes in the simulation grid within which the field lies, starting
        from the symmetry plane if present.
    mesh : List of array_like
        The x, y, z locations at which the fields are recorded.
    """

    inds_beg = span_inds[:, 0]
    inds_end = span_inds[:, 1]
    Nxyz = sim.grid.Nxyz

    # Auxiliary variable for slicing along a given axis
    slices = (slice(None),) * 5

    """If symmetries are present, we need to offset the stored fields 
    by half the simulation size in the symmetry direction. Also, if a 
    monitor starts at the symmetry axis, we double its size and 
    pad it with the fields with the correct symmetry eigenvalues. """
    for dim, sym in enumerate(sim.symmetries):

        # Auxiliary variable for symmetry eigenvalue along current axis
        svals = np.ones((3, 1, 1, 1, 1))
        svals[dim] = -1
        if sym == 1:
            svals *= -1

        if sym == -1 or sym == 1:

            if span_inds[dim, 0] == Nxyz[dim] // 2:

                inds_beg[dim] -= span_inds[dim, 1] - span_inds[dim, 0]
                sl = list(slices)
                sl[dim + 1] = slice(-1, None, -1)
                # Stack mesh
                mesh_add = sim.center[dim] - mesh[dim][-1::-1]
                mesh[dim] = np.hstack((mesh_add, mesh[dim]))
                # Stack fields
                if E.size > 0:
                    E = np.concatenate((-svals * E[tuple(sl)], E), axis=dim + 1)
                if H.size > 0:
                    H = np.concatenate((svals * H[tuple(sl)], H), axis=dim + 1)

    return (E, H, np.stack((inds_beg, inds_end), axis=1), mesh)


def nk_to_eps(n, k):
    """Convert refractive index (n, k) to complex permittivity.
    """
    return (n + 1j * k) ** 2


def eps_to_nk(eps):
    """Convert complex permittivity to refractive index (n, k).
    """

    nk_complex = np.sqrt(eps)
    return nk_complex.real, nk_complex.imag


def eps_pole_residue(poles, freqs):
    """The pole-residue contribution to the permittivity at a set of
    frequencies. We use the convention exp(-1j w t) and so positive imaginary
    part of eps(w) means loss. This is opposite from the original definition
    in Han et al., IEEE MICROWAVE AND WIRELESS COMPONENTS LETTERS (2006).
    """

    w = 2*np.pi*np.array(freqs)
    eps = np.zeros_like(w, dtype=np.complex128)
    for (a, c) in poles:
        eps -= c/(1j*w + a)
        eps -= c.conjugate()/(1j*w + a.conjugate())

    return eps