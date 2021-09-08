#!/usr/bin/env
# encoding: utf-8
"""
Author:     Daniel Boeckenhoff
Mail:       daniel.boeckenhoff@ipp.mpg.de

Triangulated mesh class and methods
"""
import logging
import os
import numpy as np
import tfields

# obj imports
from tfields.lib.decorators import cached_property


def _dist_from_plane(point, plane):
    return plane["normal"].dot(point) + plane["d"]


def _segment_plane_intersection(point0, point1, plane):
    """
    Get the intersection between the ray spanned by point0 and point1 with the plane.
    Args:
        point0: array of length 3
        point1: array of length 3
        plane:
    Returns:
        points, direction
            points (list of arrays of length 3): 3d points
    """
    distance0 = _dist_from_plane(point0, plane)
    distance1 = _dist_from_plane(point1, plane)
    point0_on_plane = abs(distance0) < np.finfo(float).eps
    point1_on_plane = abs(distance1) < np.finfo(float).eps
    points = []
    direction = 0
    if point0_on_plane:
        points.append(point0)

    if point1_on_plane:
        points.append(point1)
    # remove duplicate points
    if len(points) > 1:
        points = np.unique(points, axis=0)
    if point0_on_plane and point1_on_plane:
        return points, direction

    if distance0 * distance1 > np.finfo(float).eps:
        return points, direction

    direction = np.sign(distance0)
    if abs(distance0) < np.finfo(float).eps:
        return points, direction
    if abs(distance1) < np.finfo(float).eps:
        return points, direction
    if abs(distance0 - distance1) > np.finfo(float).eps:
        t = distance0 / (distance0 - distance1)
    else:
        return points, direction

    points.append(point0 + t * (point1 - point0))
    # remove duplicate points
    if len(points) > 1:
        points = np.unique(points, axis=0)
    return points, direction


def _intersect(triangle, plane, vertices_rejected):
    """
    Intersect a triangle with a plane. Give the info, which side of the
    triangle is rejected by passing the mask vertices_rejected
    Returns:
        list of list. The inner list is of length 3 and refers to the points of
        new triangles. The reference is done with varying types:
            int: reference to triangle index
            complex: reference to duplicate point. This only happens in case
                two triangles are returned. Then only in the second triangle
            iterable: new vertex

    TODO:
        align norm vectors with previous face
    """
    n_true = vertices_rejected.count(True)
    lonely_bool = True if n_true == 1 else False
    index = vertices_rejected.index(lonely_bool)
    s0, d0 = _segment_plane_intersection(triangle[0], triangle[1], plane)
    s1, d1 = _segment_plane_intersection(triangle[1], triangle[2], plane)
    s2, d2 = _segment_plane_intersection(triangle[2], triangle[0], plane)

    single_index = index
    couple_indices = [j for j in range(3) if not vertices_rejected[j] == lonely_bool]

    # TODO handle special cases. For now triangles with at least two points on plane are excluded
    new_vertices = None

    if len(s0) == 2:
        # both points on plane
        return new_vertices
    if len(s1) == 2:
        # both points on plane
        return new_vertices
    if len(s2) == 2:
        # both points on plane
        return new_vertices
    if lonely_bool:
        # two new triangles
        if len(s0) == 1 and len(s1) == 1:
            new_vertices = [
                [couple_indices[0], s0[0], couple_indices[1]],
                [couple_indices[1], complex(1), s1[0]],
            ]
        elif len(s1) == 1 and len(s2) == 1:
            new_vertices = [
                [couple_indices[0], couple_indices[1], s1[0]],
                [couple_indices[0], complex(2), s2[0]],
            ]
        elif len(s0) == 1 and len(s2) == 1:
            new_vertices = [
                [couple_indices[0], couple_indices[1], s0[0]],
                [couple_indices[1], s2[0], complex(2)],
            ]
    else:
        # one new triangle
        if len(s0) == 1 and len(s1) == 1:
            new_vertices = [[single_index, s1[0], s0[0]]]
        elif len(s1) == 1 and len(s2) == 1:
            new_vertices = [[single_index, s2[0], s1[0]]]
        elif len(s0) == 1 and len(s2) == 1:
            new_vertices = [[single_index, s0[0], s2[0]]]
    return new_vertices


class Mesh3D(tfields.TensorMaps):
    # pylint: disable=R0904
    """
    Points3D child used as vertices combined with faces to build a geometrical mesh of triangles
    Examples:
        >>> import tfields
        >>> import numpy as np
        >>> m = tfields.Mesh3D([[1,2,3], [3,3,3], [0,0,0], [5,6,7]], faces=[[0, 1, 2], [1, 2, 3]])
        >>> m.equal([[1, 2, 3],
        ...          [3, 3, 3],
        ...          [0, 0, 0],
        ...          [5, 6, 7]])
        True
        >>> np.array_equal(m.faces, [[0, 1, 2], [1, 2, 3]])
        True

        conversion to points only
        >>> tfields.Points3D(m).equal([[1, 2, 3],
        ...                            [3, 3, 3],
        ...                            [0, 0, 0],
        ...                            [5, 6, 7]])
        True

        Empty instances
        >>> m = tfields.Mesh3D([]);

        going from Mesh3D to Triangles3D instance is easy and will be cached.
        >>> m = tfields.Mesh3D([[1,0,0], [0,1,0], [0,0,0]], faces=[[0, 1, 2]]);
        >>> assert m.triangles().equal(tfields.Triangles3D([[ 1.,  0.,  0.],
        ...                                               [ 0.,  1.,  0.],
        ...                                               [ 0.,  0.,  0.]]))

        a list of scalars is assigned to each face
        >>> mScalar = tfields.Mesh3D([[1,0,0], [0,1,0], [0,0,0]],
        ...     faces=([[0, 1, 2]], [.5]));
        >>> np.array_equal(mScalar.faces.fields, [[ 0.5]])
        True

        adding together two meshes:
        >>> m2 = tfields.Mesh3D([[1,0,0],[2,0,0],[0,3,0]],
        ...                     faces=([[0,1,2]], [.7]))
        >>> msum = tfields.Mesh3D.merged(mScalar, m2)
        >>> msum.equal([[ 1.,  0.,  0.],
        ...             [ 0.,  1.,  0.],
        ...             [ 0.,  0.,  0.],
        ...             [ 1.,  0.,  0.],
        ...             [ 2.,  0.,  0.],
        ...             [ 0.,  3.,  0.]])
        True
        >>> assert np.array_equal(msum.faces, [[0, 1, 2], [3, 4, 5]])

        Saving and reading
        >>> from tempfile import NamedTemporaryFile
        >>> outFile = NamedTemporaryFile(suffix='.npz')
        >>> m.save(outFile.name)
        >>> _ = outFile.seek(0)
        >>> m1 = tfields.Mesh3D.load(outFile.name, allow_pickle=True)
        >>> bool(np.all(m == m1))
        True
        >>> assert np.array_equal(m1.faces, np.array([[0, 1, 2]]))

    """

    def __new__(cls, tensors, *fields, **kwargs):
        kwargs["dim"] = 3
        if "maps" in kwargs and "faces" in kwargs:
            raise ValueError("Conflicting options maps and faces")
        faces = kwargs.pop("faces", None)
        maps = kwargs.pop("maps", None)
        if faces is not None:
            if len(faces) == 0:
                # faces = []
                faces = np.empty((0, 3))
            maps = [faces]
        if maps is not None:
            kwargs["maps"] = maps
        obj = super(Mesh3D, cls).__new__(cls, tensors, *fields, **kwargs)
        if len(obj.maps) > 1:
            raise ValueError("Mesh3D only allows one map")
        if obj.maps and (len(obj.maps) > 1 or obj.maps.keys()[0] != 3):
            raise ValueError("Face dimension should be 3")
        return obj

    def _save_obj(self, path, **kwargs):
        """
        Save obj as wavefront/.obj file
        """
        obj = kwargs.pop("object", None)
        group = kwargs.pop("group", None)

        cmap = kwargs.pop("cmap", "viridis")
        map_index = kwargs.pop("map_index", None)

        path = path.replace(".obj", "")
        directory, name = os.path.split(path)

        if map_index is not None:
            scalars = self.maps[3].fields[map_index]
            min_scalar = scalars[~np.isnan(scalars)].min()
            max_scalar = scalars[~np.isnan(scalars)].max()
            vmin = kwargs.pop("vmin", min_scalar)
            vmax = kwargs.pop("vmax", max_scalar)
            if vmin == vmax:
                if vmin == 0.0:
                    vmax = 1.0
                else:
                    vmin = 0.0
            import matplotlib.colors as colors
            import matplotlib.pyplot as plt

            norm = colors.Normalize(vmin, vmax)
            color_map = plt.get_cmap(cmap)
        else:
            # switch for not coloring the triangles and thus not producing the
            # materials
            norm = None

        if len(kwargs) != 0:
            raise ValueError("Unused arguments.")

        if norm is not None:
            mat_name = name + "_frame_{0}.mat".format(map_index)
            scalars[np.isnan(scalars)] = min_scalar - 1
            sorted_scalars = scalars[scalars.argsort()]
            sorted_scalars[sorted_scalars == min_scalar - 1] = np.nan
            sorted_faces = self.faces[scalars.argsort()]
            scalar_set = np.unique(sorted_scalars)
            scalar_set[scalar_set == min_scalar - 1] = np.nan
            mat_path = os.path.join(directory, mat_name)
            with open(mat_path, "w") as mf:
                for s in scalar_set:
                    if np.isnan(s):
                        mf.write("newmtl nan")
                        mf.write("Kd 0 0 0\n\n")
                    else:
                        mf.write("newmtl mtl_{0}\n".format(s))
                        mf.write(
                            "Kd {c[0]} {c[1]} {c[2]}\n\n".format(c=color_map(norm(s)))
                        )
        else:
            sorted_faces = self.faces

        # writing of the obj file
        with open(path + ".obj", "w") as f:
            f.write("# File saved with tfields Mesh3D._save_obj method\n\n")
            if norm is not None:
                f.write("mtllib ./{0}\n\n".format(mat_name))
            if obj is not None:
                f.write("o {0}\n".format(obj))
            if group is not None:
                f.write("g {0}\n".format(group))
            for vertex in self:
                f.write("v {v[0]} {v[1]} {v[2]}\n".format(v=vertex))

            last_scalar = None
            for i, face in enumerate(sorted_faces + 1):
                if norm is not None:
                    if not last_scalar == sorted_scalars[i]:
                        last_scalar = sorted_scalars[i]
                        f.write("usemtl mtl_{0}\n".format(last_scalar))
                f.write("f {f[0]} {f[1]} {f[2]}\n".format(f=face))

    @classmethod
    def _load_stl(cls, path):
        """
        Factory method
        Given a path to a stl file, construct the object
        """
        return tfields.Triangles3D.load(path).mesh()

    @classmethod
    def _load_obj(cls, path, *group_names):
        """
        Factory method
        Given a path to a obj/wavefront file, construct the object
        """
        import csv

        log = logging.getLogger()

        with open(path, mode="r") as f:
            reader = csv.reader(f, delimiter=" ")
            groups = []
            group = None
            vertex_no = 1
            for line in reader:
                if not line:
                    continue
                if line[0] == "#":
                    continue
                if line[0] == "g":
                    if group:
                        groups.append(group)
                    group = dict(name=line[1], vertices={}, faces=[])
                elif line[0] == "v":
                    if not group:
                        log.debug("No group found. Setting default 'Group'")
                        group = dict(name="Group", vertices={}, faces=[])
                    vertex = list(map(float, line[1:4]))
                    group["vertices"][vertex_no] = vertex
                    vertex_no += 1
                elif line[0] == "f":
                    face = []
                    for v in line[1:]:
                        w = v.split("/")
                        face.append(int(w[0]))
                    group["faces"].append(face)
            else:
                groups.append(group)

        vertices = []
        for g in groups[:]:
            vertices.extend(g["vertices"].values())

        if len(group_names) != 0:
            groups = [g for g in groups if g["name"] in group_names]

        faces = []
        for g in groups:
            faces.extend(g["faces"])
        faces = np.add(np.array(faces), -1).tolist()

        """
        Building the class from retrieved vertices and faces
        """
        if len(vertices) == 0:
            return cls([])
        faceLenghts = [len(face) for face in faces]
        for i in reversed(range(len(faceLenghts))):
            length = faceLenghts[i]
            if length == 3:
                continue
            if length == 4:
                log.warning(
                    "Given a Rectangle. I will split it but "
                    "sometimes the order is different."
                )
                faces.insert(i + 1, faces[i][2:] + faces[i][:1])
                faces[i] = faces[i][:3]
            else:
                raise NotImplementedError()
        mesh = cls(vertices, faces=faces)
        if group_names:
            mesh = mesh.cleaned()
        return mesh

    @classmethod
    def plane(cls, *base_vectors, **kwargs):
        """
        Alternative constructor for creating a plane from
        Args:
            *base_vectors: see grid constructors in core. One base_vector has
                to be one-dimensional
            **kwargs: forwarded to __new__
        """
        vertices = tfields.Tensors.grid(*base_vectors, **kwargs)

        base_vectors = tfields.lib.grid.ensure_complex(*base_vectors)
        base_vectors = tfields.lib.grid.to_base_vectors(*base_vectors)
        fix_coord = None
        for coord in range(3):
            if len(base_vectors[coord]) > 1:
                continue
            if len(base_vectors[coord]) == 0:
                continue
            fix_coord = coord
        if fix_coord is None:
            raise ValueError("Describe a plane with one variable fiexed")

        var_coords = list(range(3))
        var_coords.pop(var_coords.index(fix_coord))

        faces = []
        base0, base1 = base_vectors[var_coords[0]], base_vectors[var_coords[1]]
        for i1 in range(len(base1) - 1):
            for i0 in range(len(base0) - 1):
                idx_top_left = len(base1) * (i0 + 0) + (i1 + 0)
                idx_top_right = len(base1) * (i0 + 0) + (i1 + 1)
                idx_bot_left = len(base1) * (i0 + 1) + (i1 + 0)
                idx_bot_right = len(base1) * (i0 + 1) + (i1 + 1)
                faces.append([idx_top_left, idx_top_right, idx_bot_left])
                faces.append([idx_top_right, idx_bot_left, idx_bot_right])
        inst = cls.__new__(cls, vertices, faces=faces)
        return inst

    @classmethod
    def grid(cls, *base_vectors, **kwargs):
        """
        Construct 'cuboid' along base_vectors
        Examples:
            Building symmetric geometries were never as easy:

            Approximated sphere with radius 1, translated in y by 2 units
            >>> sphere = tfields.Mesh3D.grid((1, 1, 1),
            ...                              (-np.pi, np.pi, 12),
            ...                              (-np.pi / 2, np.pi / 2, 12),
            ...                              coord_sys='spherical')
            >>> sphere.transform('cartesian')
            >>> sphere[:, 1] += 2

            Oktaeder
            >>> oktaeder = tfields.Mesh3D.grid((1, 1, 1),
            ...                                (-np.pi, np.pi, 5),
            ...                                (-np.pi / 2, np.pi / 2, 3),
            ...                                coord_sys='spherical')
            >>> oktaeder.transform('cartesian')

            Cube with edge length of 2 units
            >>> cube = tfields.Mesh3D.grid((-1, 1, 2),
            ...                            (-1, 1, 2),
            ...                            (-5, -3, 2))

            Cylinder
            >>> cylinder = tfields.Mesh3D.grid((1, 1, 1),
            ...                                (-np.pi, np.pi, 12),
            ...                                (-5, 3, 12),
            ...                                coord_sys='cylinder')
            >>> cylinder.transform('cartesian')

        """
        if not len(base_vectors) == 3:
            raise AttributeError("3 base_vectors vectors required")

        base_vectors = tfields.lib.grid.ensure_complex(*base_vectors)
        base_vectors = tfields.lib.grid.to_base_vectors(*base_vectors)

        indices = [0, -1]
        coords = range(3)
        baseLengthsAbove1 = [len(b) > 1 for b in base_vectors]
        # if one plane is given: rearrange indices and coords
        if not all(baseLengthsAbove1):
            indices = [0]
            for i, b in enumerate(baseLengthsAbove1):
                if not b:
                    coords = [i]
                    break

        base_vectors = list(base_vectors)
        planes = []
        for ind in indices:
            for coord in coords:
                basePart = base_vectors[:]
                basePart[coord] = np.array([base_vectors[coord][ind]], dtype=float)
                planes.append(cls.plane(*basePart, **kwargs))
        inst = cls.merged(*planes, **kwargs)
        return inst

    @property
    def faces(self):
        if self.maps:
            return self.maps[3]
        else:
            logging.warning(
                "No faces found. Mesh has {x} vertices.".format(x=len(self))
            )
            return tfields.Maps.to_map([], dim=3)

    @faces.setter
    def faces(self, faces):
        mp = tfields.Maps.to_map(faces, dim=3)
        self.maps[tfields.dim(mp)] = mp

    @cached_property()
    def _triangles(self):
        """
        with the decorator, this should be handled like an attribute though it
        is a method

        """
        if self.faces.size == 0:
            return tfields.Triangles3D([])
        tris = tfields.Tensors(self[self.maps[3].flatten()])
        fields = self.maps[3].fields
        return tfields.Triangles3D(tris, *fields)

    def triangles(self):
        """
        Cached method to retrieve the triangles, belonging to this mesh
        Examples:
            >>> import tfields
            >>> mesh = tfields.Mesh3D.grid((0, 1, 3), (1, 2, 3), (2, 3, 3))
            >>> assert mesh.triangles() is mesh.triangles()

        """
        return self._triangles

    def centroids(self):
        return self.triangles().centroids()

    @cached_property()
    def _planes(self):
        if self.faces.size == 0:
            return tfields.Planes3D([])
        return tfields.Planes3D(self.centroids(), self.triangles().norms())

    def planes(self):
        return self._planes

    def nfaces(self):
        return self.faces.shape[0]

    def in_faces(self, points, delta, **kwargs):
        """
        Check whether points lie within triangles with Barycentric Technique
        see Triangles3D.in_triangles. If multiple requests are done on huge meshes,
        this can be hugely optimized by requesting the property
        self.tree or setting it to self.tree = <saved tree> before calling in_faces.
        """
        key = "mesh_tree"
        if hasattr(self, "_cache") and key in self._cache:
            log = logging.getLogger()
            log.info("Using cached decision tree to speed up point - face mapping.")
            indices = self.tree.in_faces(points, delta, **kwargs)
        else:
            indices = self.triangles().in_triangles(points, delta, **kwargs)
        return indices

    @property
    def tree(self):
        """
        Cached property to retrieve a bounding_box Searcher. This searcher can
        hugely optimize 'in_faces' searches

        Examples:
            >>> import numpy as np
            >>> import tfields
            >>> mesh = tfields.Mesh3D.grid((0, 1, 3), (1, 2, 3), (2, 3, 3))
            >>> _ = mesh.tree
            >>> assert hasattr(mesh, '_cache')
            >>> assert 'mesh_tree' in mesh._cache
            >>> face_indices = mesh.in_faces(tfields.Points3D([[0.2, 1.2, 2.0]]),
            ...                      0.00001)

            You might want to know the number of points per face
            >>> unique, counts = np.unique(face_indices, return_counts=True)
            >>> dict(zip(unique, counts))  # one point on triangle number 16
            {16: 1}
        """
        if not hasattr(self, "_cache"):
            self._cache = {}
        key = "mesh_tree"
        if key in self._cache:
            tree = self._cache[key]
        else:
            tree = tfields.bounding_box.Searcher(self)
            self._cache[key] = tree
        return tree

    @tree.setter
    def tree(self, tree):
        if not hasattr(self, "_cache"):
            self._cache = {}
        key = "mesh_tree"
        self._cache[key] = tree

    def remove_faces(self, face_delete_mask):
        """
        Remove faces where face_delete_mask is True
        """
        face_delete_mask = np.array(face_delete_mask, dtype=bool)
        self.faces = self.faces[~face_delete_mask]
        self.faces.fields = self.faces.fields[~face_delete_mask]

    def template(self, sub_mesh):
        """
        'Manual' way to build a template that can be used with self.cut
        Returns:
            Mesh3D: template (see cut), can be used as template to retrieve
                sub_mesh from self instance
        Examples:
            >>> import tfields
            >>> from sympy.abc import y
            >>> mp = tfields.TensorFields([[0,1,2],[2,3,0],[3,2,5],[5,4,3]],
            ...                           [1, 2, 3, 4])
            >>> m = tfields.Mesh3D([[0,0,0], [1,0,0], [1,1,0], [0,1,0], [0,2,0], [1,2,0]],
            ...                     maps=[mp])
            >>> m_cut = m.cut(y < 1.5, at_intersection='split')
            >>> template = m.template(m_cut)
            >>> assert m_cut.equal(m.cut(template))

        TODO:
            fields template not yet implemented
        """
        cents = tfields.Tensors(sub_mesh.centroids())
        face_indices = self.in_faces(cents, delta=None)
        inst = sub_mesh.copy()
        if inst.maps:
            inst.maps[3].fields = [tfields.Tensors(face_indices, dim=1)]
        else:
            inst.maps = [
                tfields.TensorFields([], tfields.Tensors([], dim=1), dim=3, dtype=int)
            ]
        return inst

    def project(
        self,
        tensor_field,
        delta=None,
        merge_functions=None,
        point_face_assignment=None,
        return_point_face_assignment=False,
    ):
        """
        Project the points of the tensor_field to a copy of the mesh
        and set the face values accord to the field to the maps field.
        If no field is present in tensor_field, the number of points in a mesh
        is counted.

        Args:
            tensor_field (Tensors | TensorFields)
            delta (float | None): forwarded to Mesh3D.in_faces
            merge_functions (callable): if multiple Tensors lie in the same face,
                they are mapped with the merge_function to one value
            point_face_assignment (np.array, dtype=int): array assigning each
                point to a face. Each entry position corresponds to a point of the
                tensor, each entry value is the index of the assigned face
            return_point_face_assignment (bool): if true, return the
                point_face_assignment

        Examples:
            >>> import tfields
            >>> import numpy as np
            >>> mp = tfields.TensorFields([[0,1,2],[2,3,0],[3,2,5],[5,4,3]],
            ...                           [1, 2, 3, 4])
            >>> m = tfields.Mesh3D([[0,0,0], [1,0,0], [1,1,0], [0,1,0], [0,2,0], [1,2,0]],
            ...                     maps=[mp])
            >>> points = tfields.Tensors([[0.5, 0.2, 0.0],
            ...                           [0.5, 0.02, 0.0],
            ...                           [0.5, 0.8, 0.0],
            ...                           [0.5, 0.8, 0.1]])  # not contained

            Projecting points onto the mesh gives the count
            >>> m_points = m.project(points, delta=0.01)
            >>> list(m_points.maps[3].fields[0])
            [2, 1, 0, 0]

            TensorFields with arbitrary size are projected,
            combinging the fields automatically
            >>> fields = [tfields.Tensors([1,3,42, -1]),
            ...           tfields.Tensors([[0,1,2], [2,3,4], [3,4,5], [-1] * 3]),
            ...           tfields.Tensors([[[0, 0]] * 2,
            ...                            [[2, 2]] * 2,
            ...                            [[3, 3]] * 2,
            ...                            [[9, 9]] * 2])]
            >>> tf = tfields.TensorFields(points, *fields)
            >>> m_tf = m.project(tf, delta=0.01)
            >>> assert m_tf.maps[3].fields[0].equal([2, 42, np.nan, np.nan], equal_nan=True)
            >>> assert m_tf.maps[3].fields[1].equal([[1, 2, 3],
            ...                                      [3, 4, 5],
            ...                                      [np.nan] * 3,
            ...                                      [np.nan] * 3],
            ...                                     equal_nan=True)
            >>> assert m_tf.maps[3].fields[2].equal([[[1, 1]] * 2,
            ...                                      [[3, 3]] * 2,
            ...                                      [[np.nan, np.nan]] * 2,
            ...                                      [[np.nan, np.nan]] * 2],
            ...                                     equal_nan=True)

            Returning the calculated point_face_assignment can speed up multiple
            results
            >>> m_tf, point_face_assignment = m.project(tf, delta=0.01,
            ...     return_point_face_assignment=True)
            >>> m_tf_fast = m.project(tf, delta=0.01, point_face_assignment=point_face_assignment)
            >>> assert m_tf.equal(m_tf_fast, equal_nan=True)

        """
        if not issubclass(type(tensor_field), tfields.Tensors):
            tensor_field = tfields.TensorFields(tensor_field)
        inst = self.copy()

        # setup empty map fields and collect fields
        n_faces = len(self.maps[3])
        point_indices = np.arange(len(tensor_field))
        if not hasattr(tensor_field, "fields") or len(tensor_field.fields) == 0:
            # if not fields is existing use int type fields and empty_map_fields
            # in order to generate a sum
            fields = [np.full(len(tensor_field), 1, dtype=int)]
            empty_map_fields = [tfields.Tensors(np.full(n_faces, 0, dtype=int))]
            if merge_functions is None:
                merge_functions = [np.sum]
        else:
            fields = tensor_field.fields
            empty_map_fields = []
            for field in fields:
                cls = type(field)
                kwargs = {key: getattr(field, key) for key in cls.__slots__}
                shape = (n_faces,) + field.shape[1:]
                empty_map_fields.append(cls(np.full(shape, np.nan), **kwargs))
            if merge_functions is None:
                merge_functions = [lambda x: np.mean(x, axis=0)] * len(fields)

        # build point_face_assignment if not given.
        if point_face_assignment is not None:
            if len(point_face_assignment) != len(tensor_field):
                raise ValueError("Template needs same lenght as tensor_field")
        else:
            point_face_assignment = self.in_faces(tensor_field, delta=delta)

        point_face_assignment_set = set(point_face_assignment)

        # merge the fields according to point_face_assignment
        map_fields = []
        for field, map_field, merge_function in zip(
            fields, empty_map_fields, merge_functions
        ):
            for i, f_index in enumerate(point_face_assignment_set):
                if f_index == -1:
                    # point could not be mapped
                    continue
                point_in_face_indices = point_indices[point_face_assignment == f_index]
                res = field[point_in_face_indices]
                if len(res) == 1:
                    map_field[f_index] = res
                else:
                    map_field[f_index] = merge_function(res)
            map_fields.append(map_field)
        inst.maps[3].fields = map_fields
        if return_point_face_assignment:
            return inst, point_face_assignment
        return inst

    def _cut_sympy(self, expression, at_intersection="remove", _in_recursion=False):
        """
        Partition the mesh with the cuts given and return the template
        """
        eps = 0.000000001
        # direct return if self is empty
        if len(self) == 0:
            return self.copy(), self.copy()

        inst = self.copy()

        """
        add the indices of the vertices and maps to the fields. They will be
        removed afterwards
        """
        if not _in_recursion:
            inst.fields.append(tfields.Tensors(np.arange(len(inst))))
            for mp in inst.maps.values():
                mp.fields.append(tfields.Tensors(np.arange(len(mp))))

        # mask for points that do not fulfill the cut expression
        mask = inst.evalf(expression)
        # remove the points

        if not any(~mask):
            # no vertex is valid
            inst = inst[mask]
        elif all(~mask):
            # all vertices are valid
            inst = inst[mask]
        elif at_intersection == "keep":
            expression_parts = tfields.lib.symbolics.split_expression(expression)
            if len(expression_parts) > 1:
                new_mesh = inst.copy()
                for expr_part in expression_parts:
                    inst, _ = inst._cut_sympy(
                        expr_part, at_intersection=at_intersection, _in_recursion=True
                    )
            elif len(expression_parts) == 1:
                face_delete_indices = set([])
                for i, face in enumerate(inst.maps[3]):
                    """
                    vertices_rejected is a mask for each face that is True, where
                    a Point is on the rejected side of the plane
                    """
                    vertices_rejected = [~mask[f] for f in face]
                    if all(vertices_rejected):
                        # delete face
                        face_delete_indices.add(i)
                mask = np.full(len(inst.maps[3]), True, dtype=bool)
                for face_idx in range(len(inst.maps[3])):
                    if face_idx in face_delete_indices:
                        mask[face_idx] = False
                inst.maps[3] = inst.maps[3][mask]
            else:
                raise ValueError("Sympy expression is not splitable.")
            inst = inst.cleaned()
        elif at_intersection == "split" or at_intersection == "split_rough":
            """
            add vertices and faces that are at the border of the cuts
            """
            expression_parts = tfields.lib.symbolics.split_expression(expression)
            if len(expression_parts) > 1:
                new_mesh = inst.copy()
                if at_intersection == "split_rough":
                    """
                    the following is, to speed up the process. Problem is, that
                    triangles can exist, where all points lie outside the cut,
                    but part of the area
                    still overlaps with the cut.
                    These are at the intersection line between two cuts.
                    """
                    face_inters_mask = np.full((inst.faces.shape[0]), False, dtype=bool)
                    for i, face in enumerate(inst.faces):
                        vertices_rejected = [-mask[f] for f in face]
                        face_on_edge = any(vertices_rejected) and not all(
                            vertices_rejected
                        )
                        if face_on_edge:
                            face_inters_mask[i] = True
                    new_mesh.remove_faces(-face_inters_mask)

                for expr_part in expression_parts:
                    inst, _ = inst._cut_sympy(
                        expr_part, at_intersection="split", _in_recursion=True
                    )
            elif len(expression_parts) == 1:
                # build plane from cut expression
                plane_sympy = tfields.lib.symbolics.to_plane(expression)
                norm_sympy = np.array(plane_sympy.normal_vector).astype(float)
                d = -norm_sympy.dot(np.array(plane_sympy.p1).astype(float))
                plane = {"normal": norm_sympy, "d": d}

                # initialize empty containers
                norm_vectors = inst.triangles().norms()
                new_vertices = np.empty((0, 3))
                new_faces = np.empty((0, 3))
                new_fields = [
                    tfields.Tensors(
                        np.empty((0,) + field.shape[1:]), coord_sys=field.coord_sys
                    )
                    for field in inst.fields
                ]
                new_map_fields = [[] for field in inst.maps[3].fields]
                new_norm_vectors = []

                # copy TODO?
                vertices = np.array(inst)
                faces = np.array(inst.maps[3])
                fields = [np.array(field) for field in inst.fields]
                faces_fields = [np.array(field) for field in inst.maps[3].fields]

                face_delete_indices = set([])  # indexing not intersected faces
                for i, face in enumerate(inst.maps[3]):
                    """
                    vertices_rejected is a mask for each face that is True
                    where a point is on the rejected side of the plane
                    """
                    vertices_rejected = [~mask[f] for f in face]
                    if any(vertices_rejected):
                        # delete face
                        face_delete_indices.add(i)
                    if any(vertices_rejected) and not all(vertices_rejected):
                        # face on edge
                        n_true = vertices_rejected.count(True)
                        lonely_bool = True if n_true == 1 else False

                        triangle_points = [vertices[f] for f in face]
                        """
                        Add the intersection points and faces
                        """
                        intersection = _intersect(
                            triangle_points, plane, vertices_rejected
                        )
                        last_idx = len(vertices)
                        for tri_list in intersection:
                            new_face = []
                            for item in tri_list:
                                if isinstance(item, int):
                                    # reference to old vertex
                                    new_face.append(face[item])
                                elif isinstance(item, complex):
                                    # reference to new vertex that has been
                                    # concatenated already
                                    new_face.append(last_idx + int(item.imag))
                                else:
                                    # new vertex
                                    new_face.append(len(vertices))
                                    vertices = np.append(
                                        vertices, [[float(x) for x in item]], axis=0
                                    )
                                    fields = [
                                        np.append(
                                            field,
                                            np.full((1,) + field.shape[1:], np.nan),
                                            axis=0,
                                        )
                                        for field in fields
                                    ]
                            faces = np.append(faces, [new_face], axis=0)
                            faces_fields = [
                                np.append(field, [field[i]], axis=0)
                                for field in faces_fields
                            ]
                            faces_fields[-1][-1] = i

                face_map = tfields.TensorFields(
                    faces, *faces_fields, dtype=int, coord_sys=inst.maps[3].coord_sys
                )
                inst = tfields.Mesh3D(
                    vertices, *fields, maps=[face_map], coord_sys=inst.coord_sys
                )
                mask = np.full(len(inst.maps[3]), True, dtype=bool)
                for face_idx in range(len(inst.maps[3])):
                    if face_idx in face_delete_indices:
                        mask[face_idx] = False
                inst.maps[3] = inst.maps[3][mask]
            else:
                raise ValueError("Sympy expression is not splitable.")
            inst = inst.cleaned()
        elif at_intersection == "remove":
            inst = inst[mask]
        else:
            raise AttributeError(
                "No at_intersection method called {at_intersection} "
                "implemented".format(**locals())
            )

        if _in_recursion:
            template = None
        else:
            template_field = inst.fields.pop(-1)
            template_maps = []
            for mp in inst.maps.values():
                t_mp = tfields.TensorFields(tfields.Tensors(mp), mp.fields.pop(-1))
                template_maps.append(t_mp)
            template = tfields.Mesh3D(
                tfields.Tensors(inst), template_field, maps=template_maps
            )
        return inst, template

    def _cut_template(self, template):
        """
        Args:
            template (tfields.Mesh3D)

        Examples:
            >>> import tfields
            >>> import numpy as np

            Build mesh
            >>> mmap = tfields.TensorFields([[0, 1, 2], [0, 3, 4]],
            ...                             [[42, 21], [-42, -21]])
            >>> m = tfields.Mesh3D([[0]*3, [1]*3, [2]*3, [3]*3, [4]*3],
            ...                    [0.0, 0.1, 0.2, 0.3, 0.4],
            ...                    [0.0, -0.1, -0.2, -0.3, -0.4],
            ...                    maps=[mmap])

            Build template
            >>> tmap = tfields.TensorFields([[0, 3, 4], [0, 1, 2]],
            ...                             [1, 0])
            >>> t = tfields.Mesh3D([[0]*3, [-1]*3, [-2]*3, [-3]*3, [-4]*3],
            ...                    [1, 0, 3, 2, 4],
            ...                    maps=[tmap])

            Use template as instruction to make a fast cut
            >>> res = m._cut_template(t)
            >>> assert np.array_equal(res.fields,
            ...                       [[0.1, 0.0, 0.3, 0.2, 0.4],
            ...                        [-0.1, 0.0, -0.3, -0.2, -0.4]])

            >>> assert np.array_equal(res.maps[3].fields[0],
            ...                       [[-42, -21], [42, 21]])

        """
        # Possible Extension (small todo): check: len(field(s)) == len(self/maps)

        # Redirect fields
        fields = []
        if template.fields:
            template_field = np.array(template.fields[0])
            if len(self) > 0:
                """
                if new vertices have been created in the template, it is
                in principle unclear what fields we have to refer to.
                Thus in creating the template, we gave np.nan.
                To make it fast, we replace nan with 0 as a dummy and correct
                the field entries afterwards with np.nan.
                """
                nan_mask = np.isnan(template_field)
                template_field[nan_mask] = 0  # dummy reference to index 0.
                template_field = template_field.astype(int)
                for field in self.fields:
                    projected_field = field[template_field]
                    projected_field[nan_mask] = np.nan  # correction for nan
                    fields.append(projected_field)

        # Redirect maps and their fields
        maps = []
        for mp, template_mp in zip(self.maps.values(), template.maps.values()):
            mp_fields = []
            for field in mp.fields:
                if len(template_mp) == 0 and len(template_mp.fields) == 0:
                    mp_fields.append(field[0:0])  # np.empty
                else:
                    mp_fields.append(field[template_mp.fields[0].astype(int)])
            new_mp = tfields.TensorFields(tfields.Tensors(template_mp), *mp_fields)
            maps.append(new_mp)

        inst = tfields.Mesh3D(tfields.Tensors(template), *fields, maps=maps)
        return inst

    def cut(self, *args, **kwargs):
        """
        cut method for Mesh3D.
        Args:
            expression (sympy logical expression | Mesh3D):
                sympy locical expression: Sympy expression that defines planes
                    in 3D
                Mesh3D: A mesh3D will be interpreted as a template, i.e. a
                    fast instruction of how to cut the triangles.
                    It is the second part of the tuple, returned by a previous
                    cut with a sympy locial expression with 'return_template=True'.
                    We use the vertices and maps of the Mesh as the skelleton of
                    the returned mesh. The fields are mapped according to
                    indices in the template.maps[i].fields.
            coord_sys (coordinate system to cut in):
            at_intersection (str): instruction on what to do, when a cut will intersect a triangle.
                Options:    'remove' (Default) - remove the faces that are on the edge
                            'keep' - keep the faces that are on the edge
                            'split' - Create new triangles that make up the old one.
            return_template (bool): If True: return the template
                            to redo the same cut fast
        Examples:
            define the cut
            >>> import numpy as np
            >>> import tfields
            >>> from sympy.abc import x,y,z
            >>> cut_expr = x > 1.5

            >>> m = tfields.Mesh3D.grid((0, 3, 4),
            ...                         (0, 3, 4),
            ...                         (0, 0, 1))
            >>> m.fields.append(tfields.Tensors(np.linspace(0, len(m) - 1,
            ...                                             len(m))))
            >>> m.maps[3].fields.append(
            ...     tfields.Tensors(np.linspace(0,
            ...                                 len(m.maps[3]) - 1,
            ...                                 len(m.maps[3]))))
            >>> mNew = m.cut(cut_expr)
            >>> len(mNew)
            8
            >>> mNew.nfaces()
            6
            >>> float(mNew[:, 0].min())
            2.0

            Cutting with the 'keep' option will leave triangles on the edge
            untouched:
            >>> m_keep = m.cut(cut_expr, at_intersection='keep')
            >>> float(m_keep[:, 0].min())
            1.0
            >>> m_keep.nfaces()
            12

            Cutting with the 'split' option will create new triangles on the edge:
            >>> m_split = m.cut(cut_expr, at_intersection='split')
            >>> float(m_split[:, 0].min())
            1.5
            >>> len(m_split)
            15
            >>> m_split.nfaces()
            15

            Cut with 'return_template=True' will return the exact same mesh but
            additionally an instruction to conduct the exact same cut fast (template)
            >>> m_split_2, template = m.cut(cut_expr, at_intersection='split',
            ...                                    return_template=True)
            >>> m_split_template = m.cut(template)
            >>> assert m_split.equal(m_split_2, equal_nan=True)
            >>> assert m_split.equal(m_split_template, equal_nan=True)
            >>> assert len(template.fields) == 1
            >>> assert len(m_split.fields) == 1
            >>> assert len(m_split_template.fields) == 1
            >>> assert m_split.fields[0].equal(
            ...     list(range(8, 16)) + [np.nan] * 7, equal_nan=True)
            >>> assert m_split_template.fields[0].equal(
            ...     list(range(8, 16)) + [np.nan] * 7, equal_nan=True)

            This seems irrelevant at first but consider, the map field or the
            tensor field changes:
            >>> m_altered_fields = m.copy()
            >>> m_altered_fields[0] += 42
            >>> assert not m_split.equal(m_altered_fields.cut(template))
            >>> assert tfields.Tensors(m_split).equal(
            ...     m_altered_fields.cut(template))
            >>> assert tfields.Tensors(m_split.maps[3]).equal(
            ...     m_altered_fields.cut(template).maps[3])

            The cut expression may be a sympy.BooleanFunction:
            >>> cut_expr_bool_fun = (x > 1.5) & (y < 1.5) & (y >0.2) & (z > -0.5)
            >>> m_split_bool = m.cut(cut_expr_bool_fun,
            ...                      at_intersection='split')

        Returns:
            copy of cut mesh
            * optional: template

        """
        return super().cut(*args, **kwargs)

    def disjoint_parts(self, return_template=False):
        """
        Returns:
            disjoint_parts(List(cls)), templates(List(cls))

            >>> import tfields
            >>> a = tfields.Mesh3D(
            ...     [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]],
            ...     maps=[[[0, 1, 2], [0, 2, 3]]])
            >>> b = a.copy()

            >>> b[:, 0] += 2
            >>> m = tfields.Mesh3D.merged(a, b)
            >>> parts = m.disjoint_parts()
            >>> aa, ba = parts
            >>> assert aa.maps[3].equal(ba.maps[3])
            >>> assert aa.equal(a)
            >>> assert ba.equal(b)
        """
        mp_description = self.disjoint_map(3)
        parts = self.parts(mp_description)
        if not return_template:
            return parts
        else:
            templates = []
            for i, part in enumerate(parts):
                template = part.copy()
                template.maps[3].fields = [tfields.Tensors(mp_description[1][i])]
                templates.append(template)
            return parts, templates


if __name__ == "__main__":  # pragma: no cover
    import doctest

    doctest.testmod()
