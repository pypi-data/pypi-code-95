import numpy as np
import trimesh


def reindex_zerobased_slow(mesh, vert_indices, face_indices):
    """Returns a submesh with reindexed faces."""
    selected_vertices = mesh.vertices[vert_indices]
    selected_faces = np.array(mesh.faces[face_indices])
    for reindex, index in zip(np.arange(len(selected_vertices)), vert_indices):
        selected_faces[np.where(selected_faces == index)] = reindex

    submesh = trimesh.base.Trimesh(
        vertices=selected_vertices,
        faces=selected_faces,
        process=False,
        validate=False)
    return submesh


def reindex_zerobased(mesh, vert_indices, face_indices):
    """Returns a submesh with reindexed faces."""
    if len(vert_indices) == 0:
        return trimesh.base.Trimesh()

    selected_vertices = mesh.vertices[vert_indices]
    selected_faces = np.array(mesh.faces[face_indices])
    selected_faces = reindex_array(selected_faces, vert_indices)

    submesh = trimesh.base.Trimesh(
        vertices=selected_vertices,
        faces=selected_faces,
        process=False,
        validate=False)
    return submesh


def compute_relative_indexes(mesh, sub_mesh):
    """Returns vertex_indexes and face_indexes such that
    mesh.vertices[vertex_indices] ~ sub_mesh.vertices
    mesh.faces[face_indexes] ~ sub_mesh.faces."""

    # get vertex indexes in mesh by searching for identical vertices
    vertex_indexes = np.where(in2d(mesh.vertices, sub_mesh.vertices))[0]
    face_indexes = mesh.vertex_faces[vertex_indexes]
    face_indexes = np.unique(face_indexes[face_indexes > -1])

    # fix face indexing by removing faces with vertices
    # in mesh but not in sub_mesh
    fix_mask = np.all(
        np.isin(mesh.vertices[mesh.faces[face_indexes]],
                sub_mesh.vertices[sub_mesh.faces]),
        axis=(2, 1)
    )

    return vertex_indexes, face_indexes[fix_mask]


def test_compute_relative_indexes():
    test_faces = np.array([[0, 1, 2], [2, 3, 4]])
    test_verts = np.array([[0, 0, 0], [0, 1, 0], [1, 0, 0], [2, 1, 0], [2, 0, 0], ])

    test_mesh = trimesh.base.Trimesh(
        vertices=test_verts,
        faces=test_faces,
        process=False,
        validate=False)

    sub_meshes = test_mesh.split(only_watertight=False)
    assert len(sub_meshes) == 2

    for sub_mesh in sub_meshes:
        vertex_indexes, face_indexes = compute_relative_indexes(test_mesh, sub_mesh)
        assert np.all(test_mesh.vertices[vertex_indexes] == sub_mesh.vertices, axis=1)


def in2d_memhuge(ar1, ar2):
    """
    Tests whether values from ar1 are also in ar2.

    :param ar1: (M,) first 2d array
    :param ar2: second 2d array

    Returns
    -------
    idx : (M,) ndarray, bool
        The values `ar1[idx]` are in `ar2`.
    """
    ar1 = np.asarray(ar1)
    ar2 = np.asarray(ar2)
    idx = (ar1[:, np.newaxis] == ar2[np.newaxis, ...]).all(axis=2).any(axis=1)

    return idx


def asvoid(arr):
    """
    Based on http://stackoverflow.com/a/16973510/190597 (Jaime, 2013-06)
    View the array as dtype np.void (bytes). The items along the last axis are
    viewed as one value. This allows comparisons to be performed on the entire row.
    """
    arr = np.ascontiguousarray(arr)
    if np.issubdtype(arr.dtype, np.floating):
        """ Care needs to be taken here since
        np.array([-0.]).view(np.void) != np.array([0.]).view(np.void)
        Adding 0. converts -0. to 0.
        """
        arr += 0.
    return arr.view(np.dtype((np.void, arr.dtype.itemsize * arr.shape[-1])))


def in2d(a, b, assume_unique=False):
    a = asvoid(a)
    b = asvoid(b)
    return np.in1d(a, b, assume_unique)


def reindex_array(arr, idx):
    """
    Substitutes values in arr by values in [0, 1, ..., |idx|] = reidx
    such that arr[i] == reidx[idx[i]] iff arr[i] == idx[i]

    :param arr: n-d array with values in idx
    :param idx: indexing array

    Returns
    -------
    reindexed_arr : ndarray, bool
            The values `ar1[idx]` are in `ar2`.
    """
    reindexer = np.zeros(np.max(idx) + 1).astype(int)  # get the number of requested indexes
    reindexer[idx] = np.arange(len(idx))  # map old indexes to zero-based new ones
    reindexed_arr = reindexer[arr]  # reindex by asking for the new index

    return reindexed_arr


def get_reindexer(needles, haystack, raise_on_missing=True, return_missing=False):
    """Computes relative indexes `reindexer` of len(needles)
    such that haystack[reindexer[idx]] == needles[idx]
    for any idx in 0 .. |len(needles)-1|

    Needles can be 2d array (m, d),
    haystack can be 2d array (M, d), commonly M >> m
    """
    needles = np.asarray(needles)
    haystack = np.asarray(haystack)

    assert len(needles.shape) == len(haystack.shape) == 2, 'only 2d arrays are accepted'
    assert needles.shape[1] == haystack.shape[1], 'shapes of elements in needles and haystack must coincide'

    reindexer = -1 * np.ones(len(needles)).astype(np.int32)
    missing_indexes = []  # filled
    for zbi, needle in enumerate(needles):
        indicator = np.all(haystack == needle, axis=1)
        if np.any(indicator):
            reindexer[zbi] = np.where(indicator)[0]
        else:
            missing_indexes.append(zbi)

    if raise_on_missing and missing_indexes:
        raise ValueError("missing indexes: {}".format(str(missing_indexes)))

    if return_missing:
        return reindexer, np.array(missing_indexes)
    else:
        return reindexer


def get_mesh_by_edges_subset(mesh, edge_indicator):
    adj_indexes = get_reindexer(
        needles=mesh.edges_unique[edge_indicator],
        haystack=mesh.face_adjacency_edges,
    )
    sub_faces = mesh.faces[
        mesh.face_adjacency[adj_indexes]
    ].reshape(-1, 3)

    sub_vert_indexes = np.unique(sub_faces.ravel())
    sub_face_indexes = np.unique(mesh.face_adjacency[adj_indexes].ravel())
    sub_mesh = reindex_zerobased(mesh, sub_vert_indexes, sub_face_indexes)
    return sub_mesh
