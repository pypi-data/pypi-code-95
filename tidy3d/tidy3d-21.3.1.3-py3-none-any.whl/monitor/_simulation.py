import numpy as np
import logging

from ..constants import int_, float_, complex_, fp_eps, xyz_dict, xyz_list
from ..utils.em import poynting_insta, poynting_avg, expand_syms
from ..utils.log import log_and_raise, MonitorError
from ..utils import axes_handed
from ..mode import dot_product, Mode

from .Monitor import ModeMonitor, FreqMonitor, TimeMonitor

def _compute_modes_monitor(self, monitor, Nmodes, target_neff=None, pml_layers=(0, 0)):
    """Compute the eigenmodes of the 2D cross-section of a ModeMonitor object.
    """   

    if isinstance(monitor, ModeMonitor):
        # Set the Yee permittivity if not yet set
        mplane = self._mnt_data(monitor).mode_plane
        if mplane.eps_ex is None:
            mplane._set_yee_sim(self)
        # Compute the mode plane modes
        mplane.compute_modes(Nmodes, target_neff=target_neff, pml_layers=pml_layers)

def _mnt_data(self, monitor):
    """Get the monitor data object from a monitor, if it is in the simulation.
    """
    try:
        mnt_data = self._monitor_ids[id(monitor)]
        return mnt_data
    except KeyError:
        log_and_raise(
            "Monitor has not been added to Simulation!",
            MonitorError
        )

def _load_fields(self, imnt, mdata):
    """ Load the fields returned by the solver. This also applies any 
    symmetries that were present in the simulation. ``mdata`` is an h5py
    group for the corresponding monitor as returned by solver.
    """

    mnt_data = self._monitor_data[imnt]

    # By default just store index and field values, unless changed below
    mnt_data.inds_beg = np.array(mdata["indspan"][0, :])
    mnt_data.inds_end = np.array(mdata["indspan"][1, :])
    # Also store copies because inds_beg and inds_end will change later
    inds_beg = np.copy(mnt_data.inds_beg)
    inds_end = np.copy(mnt_data.inds_end)
    mesh = [np.array(mdata[m]) for m in ['xmesh', 'ymesh', 'zmesh']]

    try:
        _E = np.array(mdata["E"])
    except KeyError:
        _E = mnt_data._E

    try:
        _H = np.array(mdata["H"])
    except KeyError:
        _H = mnt_data._H

    span_inds = np.stack((mnt_data.inds_beg, mnt_data.inds_end), axis=1)

    # Pre-factor to scale integration quantities by to account for symmetries
    int_fact = 1
    for (d, Nd) in enumerate(self.grid.Nxyz):
        if self.symmetries[d] != 0 and span_inds[d, 0] == Nd//2:
            int_fact *= 2

    # Expand the fields to the full domain if there are symmetries present
    E, H, span_inds, mesh = expand_syms(self, _E, _H, span_inds, mesh)

    if 'e' in mnt_data.monitor.store:
        if E.size > 0:
            mnt_data._E = E * mnt_data.source_norm[None, None, None, None, :]
    if 'h' in mnt_data.monitor.store:
        if H.size > 0:
            mnt_data._H = H * mnt_data.source_norm[None, None, None, None, :]
    if 'flux' in mnt_data.monitor.store:
        flux = np.array(mdata["flux"])
        flux *= int_fact
        if flux.size > 0:
            mnt_data._flux = flux * mnt_data.source_norm[:, None]**2 

    mnt_data.inds_beg, mnt_data.inds_end = span_inds.T
    mnt_data.xmesh = mesh[0]
    mnt_data.ymesh = mesh[1]
    mnt_data.zmesh = mesh[2]
    mnt_data.tmesh = np.array(mdata["tmesh"])
    mnt_data.data = True

    # Load mode-related data for ModeMonitors
    if not isinstance(mnt_data.monitor, ModeMonitor):
        return

    try:
        mplane = mnt_data.mode_plane
        ma = np.array(mdata["mode_amps"])
        ma *= int_fact
        mnt_data._mode_amps = ma * mnt_data.source_norm[None, :, None]

    except KeyError:
        pass

    try:
        modes_E = np.array(mdata["modes_E"])
        modes_H = np.array(mdata["modes_H"])
        modes_n = np.array(mdata["modes_n"])
        modes_k = np.array(mdata["modes_k"])
        Nf, Nm = modes_n.shape
        
        for find in range(Nf):
            mplane.modes[find] = []
            for mind in range(Nm):
                E = modes_E[find, mind, :, :, :]
                H = modes_H[find, mind, :, :, :]
                n = modes_n[find, mind]
                k = modes_k[find, mind]
                mplane.modes[find].append(Mode(E, H, n, k))
    except KeyError:
        pass


def data(self, monitor):
    """Return a dictionary with all the stored data in a :class:`.Monitor`.
    
    Parameters
    ----------
    monitor : Monitor
        The queried monitor.
    
    Returns
    -------
    monitor_data : dict
        Dictonary with all the data currently in the monitor. For example, in 
        a frequency monitor, after a simulation run, ``monitor_data['E']`` and 
        ``monitor_data['H']`` are 5D arrays of shape ``(3, Nx, Ny, Nz, Nf)`` 
        The first index is the vector component of the field, the next three 
        dimensions index the x, y, z, position in space, and the last index
        is the frequency index at which the data was stored.

        Returned data is organized as follows

        * ``'xmesh'``: (micron) Positions along x where the fields are stored.
        * ``'ymesh'``: (micron) Positions along y where the fields are stored.
        * ``'zmesh'``: (micron) Positions along z where the fields are stored.
        * ``'tmesh'``: (s) Time points at which the fields are stored. Empty 
          array for a frequency monitor.
        * ``'freqs'``: (Hz) Frequencies at which the fields are stored. Empty 
          array for a time monitor.
        * ``'E'``: (V/micron) E-field array (empty if ``'E' not in 
          Monitor.store``).
        * ``'H'``: (A/micron) H-field array (empty if ``'H' not in 
          Monitor.store``).
        * ``'flux'``: (W) flux array with size equal to the size of ``tmesh``
          for a :class:`TimeMonitor` and to the size of ``freqs`` for a
          :class:`FreqMonitor`. Only returned if ``'flux' in Monitor.store``.
        * ``'S'``: (W/micron\\ :sup:`2`) Poynting vector (power flux density) 
          if it has been computed with :meth:`Simulation.poynting`.
        * ``'mode_amps'`` (W\\ :sup:`1/2`) For a :class:`ModeMonitor`,
          the decomposition coefficients into the different modes, in units of
          power amplitude. The shape of the array is ``(2, Nf, Nmodes)``, where
          ``mode_amps[0, :, :]`` are the coefficients for forward-propagating
          modes, and ``mode_amps[1, :, :]`` - for backward-propagating modes.
        * ``'modes'`` For a :class:`ModeMonitor`, a list of length ``Nf`` of
          lists of length ``Nmodes`` of ``Mode`` objects which store the ``E``
          and ``H`` fields of each mode as well as the real and imaginary part
          of the effective index, ``neff`` and ``keff``. The fields are
          oriented in the mode plane axes, such that they are arrays of shape
          (3, Np1, Np2) where ``Np1`` and ``Np2`` are the two in-plane
          directions. The three components are also oriented in-plane as
          ``(parallel_1, parallel_2, normal)``.
    """

    mnt_data = self._mnt_data(monitor)
    return_dict = {
        'xmesh': mnt_data.xmesh,
        'ymesh': mnt_data.ymesh,
        'zmesh': mnt_data.zmesh,
        'tmesh': mnt_data.tmesh,
        'freqs': mnt_data.freqs,
    }

    if isinstance(mnt_data.monitor, ModeMonitor):
        return_dict.update({'modes': mnt_data.mode_plane.modes})

    if mnt_data.data is False:
        return return_dict

    return_dict.update({
        'E': mnt_data.E,
        'H': mnt_data.H,
    })

    if mnt_data.flux.size > 0:
        return_dict.update({'flux': mnt_data.flux})
    if mnt_data.S.size > 0:
        return_dict.update({'S': mnt_data.S})
    if mnt_data.mode_amps.size > 0:
        return_dict.update({'mode_amps': mnt_data.mode_amps})

    return return_dict

def poynting(self, monitor):
    """Compute the Poynting vector at every point recorded by a 
    :class:`.Monitor`. Returns the instantaneous power flux per unit area at 
    every time for a :class:`.TimeMonitor`, and the time-averaged power flux 
    per unit area at every frequency for a :class:`.FreqMonitor`.
     
    Returns
    -------
    np.ndarray
        (Watt/micron\\ :sup:`2`) The Poynting vector, i.e. the directed power 
        flux per unit area, at every sampling point of the monitor. Same shape 
        as the ``E`` and ``H`` fields stored in the monitor.
    """

    mnt_data = self._mnt_data(monitor)

    if mnt_data.E.size==0:
        log_and_raise(
            "No electric field stored in the monitor.",
            MonitorError
        )
    if mnt_data.H.size==0:
        log_and_raise(
            "No magnetic field stored in the monitor.",
            MonitorError
        )

    if isinstance(monitor, TimeMonitor):
        mnt_data._S = poynting_insta(mnt_data.E, mnt_data.H)
    elif isinstance(monitor, FreqMonitor):
        mnt_data._S = poynting_avg(mnt_data.E, mnt_data.H)

    return mnt_data._S

def flux(self, monitor, normal=None):
    """Compute the area-integrated Poynting flux in a given direction. 
    This is the total power flowing through a plane orthogonal to the 
    ``normal`` direction. If the monitor is larger than one in that 
    direction, the flux at every pixel is returned. Returns the instantaneous 
    power flux at every time for a :class:`.TimeMonitor`, and the 
    time-averaged power flux at every frequency for a :class:`.FreqMonitor`.
    
    Parameters
    ----------
    normal : {'x', 'y', 'z'}, or None
        If ``None``, normal is set to the first dimension along which the 
        Monitor spans a single pixel.
    
    Returns
    -------
    np.ndarray
        (Watt) The Poynting flux, an array of shape ``(Nsample, Np)``, where 
        ``Np`` are the number of points in the monitor volume along the 
        normal direction, while ``Nsample`` is the number of time steps 
        or frequencies in the monitor. If ``Np==1``, the return shape is just
        ``(Nsample, )``.
    """

    mnt_data = self._mnt_data(monitor)

    if normal is None:
        dmin = np.argmin(mnt_data.inds_end - mnt_data.inds_beg)
        normal = xyz_list[dmin]
    try:
        norm_ind = xyz_dict[normal]
    except:
        log_and_raise("'normal' must be one of 'x', 'y', or 'z'.", MonitorError)

    cinds = [0, 1, 2]
    cinds.pop(norm_ind)

    if mnt_data.S.size==0:
        self.poynting(monitor)

    # Compute numerical integral
    coords1 = self.grid.coords[cinds[0]]
    coords1 = coords1[mnt_data.inds_beg[cinds[0]]:mnt_data.inds_end[cinds[0]] + 1]
    dl1 = coords1[1:] - coords1[:-1]
    coords2 = self.grid.coords[cinds[1]]
    coords2 = coords2[mnt_data.inds_beg[cinds[1]]:mnt_data.inds_end[cinds[1]] + 1]
    dl2 = coords2[1:] - coords2[:-1]
    dA = np.outer(dl1, dl2)

    dz = (self.grid.coords[norm_ind][mnt_data.inds_end[norm_ind]] - self.grid.coords[norm_ind][mnt_data.inds_beg[norm_ind]])
    dV = dA * dz

    # Poynting vector in normal direction
    S = mnt_data.S[norm_ind, :, :, :, :]
    # Arrange as Nsample, Nnorm, Ncross1, Ncross2
    S = np.moveaxis(S, (3, norm_ind, cinds[0], cinds[1]), np.arange(4))
    
    # Compute flux
    fl = np.sum(S * dA, axis=(-2, -1)).astype(float_)

    return fl

def decompose(self, mode_monitor):
    """Compute the decomposition of the fields recorded in a 
    :class:`.ModeMonitor` into the eigenmodes in the monitor plane.  

    Parameters
    ----------
    mode_monitor : ModeMonitor
        ModeMonitor object to compute the decomposition for.
    
    Returns
    -------
    np.ndarray
        A tuple of two arrays giving the overlap coefficients of the mode 
        fields with the forward- and backward-propagating eigenmodes, 
        respectively. Each array has shape ``(Nfreqs, Nmodes)``, where 
        ``Nfreqs`` is the number of frequencies in the monitor.
    """

    if not isinstance(mode_monitor, ModeMonitor):
        log_and_raise("'ModeMonitor' instance expected.", TypeError)

    mnt_data = self._mnt_data(mode_monitor)
    Nmodes = mnt_data.Nmodes
    target_neff = mnt_data.target_neff
    mplane = mnt_data.mode_plane

    if Nmodes > len(mplane.modes[0]):
        self.compute_modes(mode_monitor, Nmodes, target_neff)

    if mnt_data.data is False:
        log_and_raise("No data loaded in monitor.", RuntimeError)

    Nfreqs = len(mnt_data.freqs)
    positive_coeff = np.zeros((Nfreqs, Nmodes), dtype=complex_)
    negative_coeff = np.zeros((Nfreqs, Nmodes), dtype=complex_)

    for ifreq in range(Nfreqs):
        # Need to get the monitor field of shape (3, Ncross1, Ncross2)
        E = mnt_data.E[mplane.new_ax[0:2], :, :, :, ifreq]
        H = mnt_data.H[mplane.new_ax[0:2], :, :, :, ifreq]
        # +/-1 factor on H due to axes change
        H *= axes_handed(mplane.new_ax)
        fields_monitor = (np.squeeze(E, axis=1 + mnt_data.norm_ind),
                        np.squeeze(H, axis=1 + mnt_data.norm_ind))

        for imode, mode in enumerate(mplane.modes[ifreq]):
            # Fields of the mode snapped to Yee grid centers
            (Em, Hm) = mode.fields_to_center()

            # Overlap with positive-direction mode
            positive_coeff[ifreq, imode] = dot_product(
                                    (Em, Hm), fields_monitor,
                                    mplane.grid.coords)
            # Overlap with negative-direction mode.
            # Note: the sign of the fields is correct only for the tangential 
            # components, but those are the only ones entering the dot product.
            negative_coeff[ifreq, imode] = dot_product(
                                    (np.conj(Em), -np.conj(Hm)), 
                                    fields_monitor,
                                    mplane.grid.coords)

    return positive_coeff, negative_coeff

def set_monitor_modes(self, monitor, Nmodes=None, target_neff=None):
    """Set the number ``Nmodes`` of modes with effective index closest
    to ``target_neff`` to be used in the modal decomposition in the monitor.
    
    Parameters
    ----------
    monitor : ModeMonitor
        A mode monitor in the simulation.
    Nmodes : None or int, optional
        Number of modes to compute. If ``None``, uses ``monitor.Nmodes``.
    target_neff : None or float, optional
        Look for modes with effective index closest to ``target_neff``. If
        ``None``, the modes are computed in order of decreasing index.
    """

    mnt_data = self._mnt_data(monitor)
    mplane = mnt_data.mode_plane

    if isinstance(monitor, ModeMonitor):

        if Nmodes is not None:
            mnt_data.Nmodes = Nmodes
        mnt_data.target_neff = target_neff

    else:
        log_and_raise(
            "Input 0 must be an instance of a ModeMonitor.", MonitorError
        )