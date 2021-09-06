import numpy as np
from itertools import chain
from matplotlib.path import Path

# gdspy is only needed for the GdsSlab structure
try:
    import gdspy
except ImportError:
    pass

from .material import Medium, PEC, PMC
from .utils import inside_box, inside_box_mesh, cs2span
from .utils.log import log_and_raise, StructureError
from .constants import fp_eps, int_, float_, xyz_dict

class Structure(object):
    """
    Base class for regions defined by geometric shapes in a simulation domain.
    """

    def __init__(self, material, name=None):
        """Base class for structures. Available subclasses:

        - :class:`.Box`
        - :class:`.Sphere`
        - :class:`.Cylinder`
        - :class:`.PolySlab`
        - :class:`.GdsSlab`
        """
        self.material = material
        self.name = str(name) if name else None

        # if bounds are not set (default), self.bounds is None,
        # otherwise it's a (3,2) array specifying bounding box min and max
        # values along each dimension
        self.bounds = None


    def _inside(self, mesh, include_edges=True):
        """Elementwise indicator function for the structure.
        
        Parameters
        ----------
        mesh : tuple
            3-tuple defining the xgrid, ygrid and zgrid.
        include_edges : bool
            Whether a point sitting exactly on a mesh point (within numerical 
            precision) should be returned as inside (True) or outside (False) 
            the structure.
        
        Note
        ----
        ``include_edges`` will in the future be replaced by actual dielectric 
        smoothening.
        
        Returns
        -------
        mask : np.ndarray
            A 3D array of shape (mesh[0].size, mesh[1].size, mesh[2].size) 
            that is 1 inside the structure and 0 outside, and a continuous 
            value between 0 and 1 at interfaces if smoothen==True.
        """

        raise NotImplementedError(
            "inside() needs to be implemented by Structure subclasses"
        )

    def _get_eps_val(self, pec_val, pmc_val, freq=None, component='average'):
        """ Get epsilon value for structure. If the real part of the 
        permittivity is smaller than ``pec_val``, ``pec_val`` is returned."""

        if isinstance(self.material, Medium):
            eps_r = self.material.epsilon(freqs=freq, component=component)
            eps_r[np.real(eps_r) < pec_val] = pec_val
            return eps_r
        elif isinstance(self.material, PEC):
            return pec_val
        elif isinstance(self.material, PMC):
            return pmc_val

    def _set_val_direct(self, mesh, val_arr, val, edges='average'):
        """ Set value ``val`` to all elements of array ``val_arr`` defined 
        over sptial ``mesh``, which are inside the current Structure."""

        if edges=='in' or edges=='average':
            mask = self._inside(mesh, include_edges=True)
        if edges=='average':
            mask += self._inside(mesh, include_edges=False)
            mask = mask.astype(float_)/2
        if edges=='out':
            mask = self._inside(mesh, include_edges=False)
        mask_bool = mask > 0
        mask_in = mask[mask_bool]
        val_arr[mask_bool] = (1 - mask_in)*val_arr[mask_bool] + val*mask_in

    def _set_val(self, mesh, val_arr, val, edges='average'):
        """ Set value ``val`` to all elements of array ``val_arr`` defined 
        over sptial ``mesh``, which are inside the current Structure. This 
        uses ``_set_val_direct`` only after applying the bounding box, if 
        known."""

        # no bounds defined, do the most naive thing
        if self.bounds is None:
            self._set_val_direct(mesh, val_arr, val, edges=edges)
            return

        bound_inds = self._get_bounding_indices(mesh)

        # mesh is completely outside bounds, skip this structure
        if bound_inds is None:
            return
            
        sub_mesh, sub_arr = self._get_sub_problem(mesh, val_arr, bound_inds)
        self._set_val_direct(sub_mesh, sub_arr, val, edges=edges)

    def _get_bounding_indices(self, mesh):
        """ uses self.bounds to compute min and max bounding indices in mesh
        
        Parameters
        ----------
        mesh : tuple
            3-tuple defining the xgrid, ygrid and zgrid.
        
        Returns
        -------
        bound_inds : np.ndarray
            A 3D array of shape (3, 2) 
            bound_inds[d, :] gives the indices into `mesh` that are closest to 
            min and max values in dimension `d`. 
            for safety, min is rounded down to the nearest index and 
            max is rounded up to the nearest index
        """

        # if bounds are not defined for this structure, just return None
        if self.bounds is None:
            return None

        # unpack bounds and slightly increase to capture edge cases
        xb = (self.bounds[0, 0] - 10*fp_eps, self.bounds[0, 1] + 10*fp_eps)
        yb = (self.bounds[1, 0] - 10*fp_eps, self.bounds[1, 1] + 10*fp_eps)
        zb = (self.bounds[2, 0] - 10*fp_eps, self.bounds[2, 1] + 10*fp_eps)
        xs, ys, zs = mesh

        # compute indices within the bounding region in each dimension
        ixs = np.nonzero((xs > xb[0])*(xs <= xb[1]))[0]
        iys = np.nonzero((ys > yb[0])*(ys <= yb[1]))[0]
        izs = np.nonzero((zs > zb[0])*(zs <= zb[1]))[0]

        # check if any conditions gave no matches (bounds outside mesh, skip)
        if any([len(i) == 0 for i in (ixs, iys, izs)]):
            return None

        # get the min and max inside bounding indices in each dimension
        ix_min, ix_max = ixs[0], ixs[-1] + 1
        iy_min, iy_max = iys[0], iys[-1] + 1
        iz_min, iz_max = izs[0], izs[-1] + 1

        # construct bounding indices array for constructing sub mesh & sub arr
        return np.array([[ix_min, ix_max], [iy_min, iy_max], [iz_min, iz_max]])

        

    @staticmethod
    def _get_sub_problem(mesh, arr, bound_inds):
        """ returns a view to sub mesh and sub epsilon array using `bound_inds`
        """

        # unpack bound_inds
        bounds_ix, bounds_iy, bounds_iz = bound_inds
        ix_min, ix_max = bounds_ix
        iy_min, iy_max = bounds_iy
        iz_min, iz_max = bounds_iz

        # get sub mesh
        xs, ys, zs = mesh
        sub_xs = xs[ix_min:ix_max]
        sub_ys = ys[iy_min:iy_max]
        sub_zs = zs[iz_min:iz_max]
        sub_mesh = sub_xs, sub_ys, sub_zs

        # get view into sub epsilon array
        sub_eps = arr[ix_min:ix_max, iy_min:iy_max, iz_min:iz_max]

        return sub_mesh, sub_eps


class Box(Structure):
    """ Box structure, i.e. a 3D rectangular axis-aligned prism.
    """

    def __init__(self, center, size, material, name=None):
        """ Construct.

        Parameters
        ----------
        center : array_like
            (micron): x, y, and z position of the center of the Box.
        size : array_like
            (micron): size in x, y, and z.
        material : Material
            Material of the structure.
        name : str, optional
            Custom name of the structure.
        """
        super().__init__(material, name)
        self.center = np.array(center)
        self.size = np.array(size)
        self.span = cs2span(self.center, self.size)

        # set bounds
        mins = self.center - self.size / 2
        maxs = self.center + self.size / 2
        self.bounds = np.stack((mins, maxs), axis=1)  # (3, 2)

    def _inside(self, mesh, include_edges=True):
        """Returns a mask defining whether the points in ``mesh`` are inside 
        the Box region."""

        tmp_span = np.copy(self.span)
        if include_edges == True:
            tmp_span[:, 0] -= fp_eps
            tmp_span[:, 1] += fp_eps
        else:
            tmp_span[:, 0] += fp_eps
            tmp_span[:, 1] -= fp_eps

        return inside_box(tmp_span, mesh)


class BoxAngled(Structure):
    """ Box structure, i.e. a 3D rectangular block at an angle in x-y plane
    """

    def __init__(self, center, size, angle, material, bounded=True, name=None):
        """ Box positioned at angle in x-y plane
        Parameters
        ----------
        center : array_like
            (micron): x, y, and z position of the center of the Box.
        size : array_like
            (micron): size in x, y, and z.
        angle: float
            (radians) angle to rotate box from x axis
        material : Material
            Material of the structure.
        bounded : bool
            If you want to use the bounded feature 
            (just for testing with and without)
        name : str, optional
            Custom name of the structure.
        """
        super().__init__(material, name)
        self.center = np.array(center)
        self.size = np.array(size)
        self.angle = angle
        if bounded:
            xy_radius = np.max(self.size[:-1])
            z_size = self.size[-1]
            max_xy_size = 2 * xy_radius * np.sqrt(2)
            size = np.array([max_xy_size, max_xy_size, z_size])
            mins = self.center - size / 2
            maxs = self.center + size / 2
            self.bounds = np.stack((mins, maxs), axis=1)  # (3, 2)

    def _inside(self, mesh, include_edges=False):
        """Returns a mask defining whether the points in ``mesh`` are inside 
        the Box region."""

        # expand mesh
        xx, yy, zz = np.meshgrid(*mesh, indexing="ij")

        # centered coordinates
        xxc = xx - self.center[0]
        yyc = yy - self.center[1]
        zzc = zz - self.center[2]

        # rotated coords
        xxp = xxc * np.cos(self.angle) - yyc * np.sin(self.angle)
        yyp = xxc * np.sin(self.angle) + yyc * np.cos(self.angle)

        # return 1 if rotated coordinates are inside of box
        inside_x = np.abs(xxp) < self.size[0] / 2
        inside_y = np.abs(yyp) < self.size[1] / 2
        inside_z = np.abs(zzc) < self.size[2] / 2

        return 1.0 * (inside_x * inside_y * inside_z)


class Sphere(Structure):
    """ Sphere structure.
    """

    def __init__(self, center, radius, material, name=None):
        """ Construct.

        Parameters
        ----------
        center : array_like
            (micron): x, y, z position of the center of the sphere.
        radius : float
            (micron) Radius of the sphere.
        material : Material
            Material of the structure.
        name : str, optional
            Custom name of the structure.
        """
        super().__init__(material, name)
        self.center = np.array(center, dtype=float_)
        self.radius = radius
        mins = self.center - 2 * self.radius
        maxs = self.center + 2 * self.radius
        self.bounds = np.stack((mins, maxs), axis=1)

    def _inside(self, mesh, include_edges=True):
        """Returns a mask defining whether the points in ``mesh`` are inside 
        the Sphere."""

        xc, yc, zc = self.center

        # this line is abstruse
        r = self.radius * (1 + (include_edges - 0.5) * 2 * fp_eps)

        # cleaned this up:
        #
        # return np.where((x - mesh[0][:, np.newaxis, np.newaxis])**2 +
        #             (y - mesh[1][np.newaxis, :, np.newaxis])**2 +
        #             (z - mesh[2][np.newaxis, np.newaxis, :])**2 < r**2, 1, 0)
        # becomes:

        xx, yy, zz = np.meshgrid(*mesh, indexing="ij")
        return ((xx - xc) ** 2 + (yy - yc) ** 2 + (zz - zc) ** 2 < r ** 2)


class Cylinder(Structure):
    """ Cylinder structure.
    """

    def __init__(self, center, axis, radius, height, material, name=None):
        """Construct.

        Parameters
        ----------
        center : array_like
            (micron): x, y, z position of the center of the cylinder.
        axis : str
            ``'x'``, ``'y'``, or ``'z'``.
        radius : float
            (micron) Radius of the cylinder.
        height : float
            (micron) Height of the cylinder along its axis.
        material : Material
            Material of the structure.
        name : str, optional
            Custom name of the structure.
        """
        super().__init__(material, name)
        self.center = np.array(center, dtype=float_)
        self.axis = axis
        self.radius = radius
        self.height = height

        # set bounds
        if axis == "x":
            sizes = np.array([height, 2 * radius, 2 * radius])
        elif axis == "y":
            sizes = np.array([2 * radius, height, 2 * radius])
        elif axis == "z":
            sizes = np.array([2 * radius, 2 * radius, height])
        else:
            # do this error checking elsewhere
            log_and_raise(
                f"Given axis {axis}, must be in ['x', 'y', 'z'].",
                StructureError
            )

        mins = self.center - sizes / 2
        maxs = self.center + sizes / 2
        self.bounds = np.stack((mins, maxs), axis=1)  # (3, 2)

    def _inside(self, mesh, include_edges=True):
        """Returns a mask defining whether the points in ``mesh`` are inside 
        the Cylinder."""

        ax = xyz_dict[self.axis]
        d_cross = [0, 1, 2]
        d_cross.pop(ax)
        d_a = self.center[ax]
        d1, d2 = self.center[d_cross]
        r = self.radius * (1 + (include_edges - 0.5) * 2 * fp_eps)
        h = self.height * (1 + (include_edges - 0.5) * 2 * fp_eps)

        m = [
            mesh[0][:, np.newaxis, np.newaxis],
            mesh[1][np.newaxis, :, np.newaxis],
            mesh[2][np.newaxis, np.newaxis, :],
        ]
        m_a = m[ax]
        m1 = m[d_cross[0]]
        m2 = m[d_cross[1]]

        return np.where(((d1 - m1)**2 + (d2 - m2)**2 < r**2) *  
                            (np.abs(d_a - m_a) < h/2), 1, 0)


class PolySlab(Structure):
    """ A structure defined as polygon in x and y, and extruded in z.
    """

    def __init__(self, material, vertices, z_cent=0, z_size=1,
            z_min=None, z_max=None, name=None):
        """Construct.
        
        Parameters
        ----------
        material : Material
            Material of the structure.
        vertices : array_like
            (micron) Shape (N, 2) defining the polygon vertices in the xy-plane.
        z_cent : float
            (micron) Center of the polygonal slab in z.
        z_size : float
            (micron) Thickness of the slab in z.
        z_min : None, optional
            (micron) Beginning of the slab along z.
        z_max : None, optional
            (micron) End of the slab along z.
        name : str, optional
            Custom name of the structure.

        Note
        ----
        If ``z_min`` and ``z_max`` are provided, they override ``z_cent`` and
        ``z_size``.
        """

        """
        dilation : float, optional
            (microns) constant dilation (+) or contraction (-) applied to 
            polygon vertices.            
        slant_angle : float, optional
            (degrees) Sidewall angle; 0 is straight vertical sidewalls,
            slant_angle > 0 indicates a smaller polygon at z_max.
        """
        dilation, slant_angle = 0, 0

        super().__init__(material, name)

        if z_min is not None and z_max is not None:
            self.z_cent = (z_min + z_max)/2
            self.z_size = z_max - z_min
        elif z_min is None and z_max is None:
            self.z_cent = z_cent
            self.z_size = z_size
        else:
            log_and_raise("Both z_min and z_max must be provided.", StructureError)

        self.vertices = np.array(vertices, dtype=float_) # raw vertices
        self.base = _orient(_shift_vertices(self.vertices, -dilation))
        self.top = _shift_vertices(self.base, self.z_size*np.tan(slant_angle))

        self.slant_angle = slant_angle
        self.dilation = dilation

        x_min, y_min = np.min(np.concatenate((self.base, self.top), axis=0), axis=0)
        x_max, y_max = np.max(np.concatenate((self.base, self.top), axis=0), axis=0)
        z_min = self.z_cent - self.z_size / 2
        z_max = self.z_cent + self.z_size / 2

        mins = np.array([x_min, y_min, z_min])
        maxs = np.array([x_max, y_max, z_max])

        self.bounds = np.stack((mins, maxs), axis=1)

    def _inside(self, mesh, include_edges=True):
        """Returns a mask defining whether the points in ``mesh`` are inside 
        the PolySlab."""

        z_size = self.z_size * (1 + (include_edges - 0.5) * 2 * fp_eps)
        xm, ym = np.meshgrid(mesh[0], mesh[1])
        xy_points = np.vstack((xm.ravel(), ym.ravel())).T

        below_top = mesh[2] <= self.z_cent + z_size / 2
        above_bot = mesh[2] >= self.z_cent - z_size / 2
        mask_z = below_top * above_bot

        # vertices of the polygon base
        if include_edges == True:
            vertices = _shift_vertices(self.base, -fp_eps)
        else:
            vertices = _shift_vertices(self.base, fp_eps)

        # get mask for original (or dilated, if applied) polyslab
        path = Path(vertices)
        mask_xy = path.contains_points(xy_points).reshape(xm.shape).T
        mask_xyz = mask_xy[..., None] * mask_z[None, None, ...]

        # apply side angle
        if not np.isclose(self.slant_angle, 0):

            # compute all shifted polygons for each z positions in supplied mesh
            zs = mesh[2]
            heights = zs - (self.z_cent - z_size / 2)
            slant_angle_rad = self.slant_angle / 180 * np.pi
            dists = heights * np.tan(slant_angle_rad)
            polygons = _shift_vertices(vertices, dists)

            # for each polygon in the set of z positions, update mask 
            for zi, (h, vertices_z) in enumerate(zip(heights, polygons)):

                # if within z bounds
                if h >= 0 and h <= z_size:

                    # grab shifted mask at z
                    path_at_z = Path(vertices_z)
                    mask_xy_at_z_flat = path_at_z.contains_points(xy_points)
                    mask_xy_at_z = mask_xy_at_z_flat.reshape(xm.shape).T

                    # apply to master mask
                    mask_xyz[..., zi] = mask_xy_at_z

        return np.where(mask_xyz > 0, 1, 0)


class GdsSlab(Structure):
    """ A structure defined through a GDS cell imported through ``gdspy``. 
    All polygons and paths included in the cell are assumed to lie in the 
    xy-plane, with the same center and size in z, and made of the same
    material. Optionally, the integer ``gds_layer`` and ``gds_dtype`` index
    can be provided. If not, all structures in the cell are imported.
    """

    def __init__(self, material, gds_cell, gds_layer=None, gds_dtype=None,
            gds_scale=1., z_cent=0, z_size=1, z_min=None, z_max=None, 
            name=None):
        """Construct.
        
        Parameters
        ----------
        material : Material
            Material of the structure.
        gds_cell : gdspy.Cell
            A GDS Cell containing all polygons and paths to be imported.
        gds_layer : int, optional
            Layer index to select by. If ``None``, all indexes are taken.
        gds_dtype : None, optional
            Data type index to select by. If ``None``, all indexes are taken.
        gds_scale : float, optional
            (micron) Length scale in units of micron.
        z_cent : float
            (micron) Center of the structure in z.
        z_size : float
            (micron) Thickness of the structure in z.
        z_min : None, optional
            (micron) Beginning of the structure along z.
        z_max : None, optional
            (micron) End of the structure along z.
        name : str, optional
            Custom name of the structure.

        Note
        ----
        If ``z_min`` and ``z_max`` are provided, they override ``z_cent`` and
        ``z_size``.
        """

        """
        dilation : float, optional
            (microns) constant dilation (+) or contraction (-) applied to 
            polygon vertices.
        slant_angle : float, optional
            (degrees) Sidewall angle; 0 is straight vertical sidewalls,
            slant_angle > 0 indicates a smaller polygon at z_max.
        """
        dilation, slant_angle = 0, 0

        super().__init__(material, name)
        self.gds_cell = gds_cell
        self.gds_layer = gds_layer
        self.gds_dtype = gds_dtype
        self.gds_scale = gds_scale

        vert_dict = gds_cell.get_polygons(by_spec=True)
        vertices = []
        for spec, verts in vert_dict.items():
            if ((spec[0] == self.gds_layer or self.gds_layer is None) and
                    (spec[1] == self.gds_dtype or self.gds_dtype is None)):
                vertices += verts

        self.poly_slabs = []
        for poly_verts in vertices:
            self.poly_slabs.append(
                PolySlab(
                    material=material,
                    vertices=poly_verts*self.gds_scale,
                    z_cent=z_cent,
                    z_size=z_size,
                    z_min=z_min,
                    z_max=z_max,
                )
            )

    def _inside(self, mesh, include_edges=True):
        """Returns a mask defining whether the points in ``mesh`` are inside 
        the PolySlab."""

        mask = np.zeros([np.array(m).size for m in mesh])
        for poly in self.poly_slabs:
            mask += poly._inside(mesh, include_edges)

        return np.where(mask > 0, 1, 0)


""" ============== Various polygon helper functions ================="""

def _area(vertices):
    """Compute the signed polygon area.
    """
    vert_shift = np.roll(vertices.copy(), axis=0, shift=-1)
    term1 = vertices[:, 0]*vert_shift[:, 1]
    term2 = vertices[:, 1]*vert_shift[:, 0]

    return np.sum(term1 - term2) * 0.5

def _orient(vertices):
    """Return a positively-oriented polygon.
    """
    if _area(vertices) > 0:
        return vertices
    else:
        return vertices[::-1, :]

def _shift_vertices(vertices, dists):
    """ shifts the vertices of a polygon inward uniformly by distances 
    `dists`.  Returns new polygon vertices, one for each dist.
    """

    # cast dists to array just to be safe (if float)
    dists = np.array(dists)

    if np.all(np.isclose(dists, 0)):
        return vertices

    def rot90(v):
        """ 90 degree rotation of 2d vector
            vx -> vy
            vy -> -vx
        """
        vxs, vys = v
        return np.stack((-vys, vxs), axis=0)
    
    def cross(v1, v2):
        return np.cross(v1, v2, axis=0)
    
    def normalize(v):
        return v / (np.linalg.norm(v, axis=0) + fp_eps)
    
    num_verts = vertices.shape[0]
    
    vs = vertices.T.copy()
    vsp = np.roll(vs.copy(), axis=-1, shift=-1)
    vsm = np.roll(vs.copy(), axis=-1, shift=+1)
    
    asp = normalize(vsp - vs)
    asm = normalize(vs - vsm)

    vs_new = vs + dists[..., None, None] * rot90(asm)
    det = cross(asp, asm)

    det_nz = 1.0 - 1.0 * np.isclose(det, 0)

    tmp = (cross(asm, rot90(asm-asp)) / (det + 1e-9))
    corrections = (1 - np.isclose(det, 0)) * dists[..., None, None] * tmp

    return np.swapaxes(vs_new + corrections * asm, -2, -1)