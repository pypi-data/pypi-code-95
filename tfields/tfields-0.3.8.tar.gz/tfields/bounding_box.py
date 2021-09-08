import copy
import logging
import numpy as np
import sympy
import tfields


class Node(object):
    """
    This class allows to increase the performance with cuts in
    x,y and z direction
    An extension to arbitrary cuts might be possible in the future

    Args:
        parent: Parent node of self
        mesh: Mesh corresponding to the node
        cut_expr: Cut that determines the seperation in left and right node
        cuts: List of cuts for the children nodes

    Attrs:
        parent (Node)
        remaining_cuts (dict): key specifies dimension, value the cuts that
            are still not done
        cut_expr (dict): part of parents remaining_cuts. The dimension defines
            what is meant by left and right


    Examples:
        >>> import tfields
        >>> mesh = tfields.Mesh3D.grid((5.6, 6.2, 3),
        ...                            (-0.25, 0.25, 4),
        ...                            (-1, 1, 10))

        >>> cuts = {'x': [5.7, 6.1],
        ...         'y': [-0.2, 0, 0.2],
        ...         'z': [-0.5, 0.5]}

        >>> tree = tfields.bounding_box.Node(mesh,
        ...                                  cuts,
        ...                                  at_intersection='keep')
        >>> leaves = tree.leaves()
        >>> leaves = tfields.bounding_box.Node.sort_leaves(leaves)
        >>> meshes = [leaf.mesh for leaf in leaves]
        >>> templates = [leaf.template for leaf in leaves]
        >>> special_leaf = tree.find_leaf([5.65, -0.21, 0])

    """

    def __init__(
        self,
        mesh,
        cuts,
        coord_sys=None,
        at_intersection="split",
        delta=0.0,
        parent=None,
        box=None,
        internal_template=None,
        cut_expr=None,
    ):
        self.parent = parent
        # initialize
        self.mesh = copy.deepcopy(mesh)
        if self.is_root():
            cuts = copy.deepcopy(cuts)  # dicts are mutable
        self.remaining_cuts = cuts
        logging.debug(cuts)

        self.delta = delta
        if box is None:
            vertices = np.array(self.mesh)
            self.box = {
                "x": [min(vertices[:, 0]) - delta, max(vertices[:, 0]) + delta],
                "y": [min(vertices[:, 1]) - delta, max(vertices[:, 1]) + delta],
                "z": [min(vertices[:, 2]) - delta, max(vertices[:, 2]) + delta],
            }
        else:
            self.box = box
        self.left = None
        self.right = None
        self.at_intersection = at_intersection
        self._internal_template = internal_template
        if self.is_leaf():
            self._template = None
        if self.is_root():
            self._trim_to_box()
        self.cut_expr = cut_expr
        self.left_template = None
        self.right_template = None
        self.coord_sys = coord_sys
        # start the splitting process
        self._build()

    def _build(self):
        if not self.is_last_cut():
            self._choose_next_cut()
            self._split()

    def is_leaf(self):
        if self.left is None and self.right is None:
            return True
        else:
            return False

    def is_root(self):
        if self.parent is None:
            return True
        else:
            return False

    def is_last_cut(self):
        for key in self.remaining_cuts:
            if len(self.remaining_cuts[key]) != 0:
                return False
        return True

    def in_box(self, point):
        x, y, z = point
        for key in ["x", "y", "z"]:
            value = locals()[key]
            if value < self.box[key][0] or self.box[key][1] < value:
                return False
        return True

    @property
    def root(self):
        if self.is_root:
            return self
        return self.parent.root

    @classmethod
    def sort_leaves(cls, leaves_list):
        """
        sorting the leaves first in x, then y, then z direction
        """
        sorted_leaves = sorted(
            leaves_list, key=lambda x: (x.box["x"][1], x.box["y"][1], x.box["z"][1])
        )
        return sorted_leaves

    def _trim_to_box(self):
        # 6 cuts to remove outer part of the box
        x, y, z = sympy.symbols("x y z")
        eps = 0.0000000001
        x_cut = (float(self.box["x"][0] - eps) <= x) & (
            x <= float(self.box["x"][1] + eps)
        )
        y_cut = (float(self.box["y"][0] - eps) <= y) & (
            y <= float(self.box["y"][1] + eps)
        )
        z_cut = (float(self.box["z"][0] - eps) <= z) & (
            z <= float(self.box["z"][1] + eps)
        )
        section_cut = x_cut & y_cut & z_cut

        self.mesh, self._internal_template = self.mesh.cut(
            section_cut, at_intersection=self.at_intersection, return_template=True
        )

    def leaves(self):
        """
        Recursive function to create a list of all leaves

        Returns:
            list: of all leaves descending from this node
        """
        if self.is_leaf():
            return [self]
        else:
            if self.left is not None:
                leftLeaves = self.left.leaves()
            else:
                leftLeaves = []
            if self.right is not None:
                rightLeaves = self.right.leaves()
            else:
                rightLeaves = []
            return tfields.lib.util.flatten(leftLeaves + rightLeaves)

    def find_leaf(self, point, _in_recursion=False):
        """
        Returns:
            Node / None:
                Node: leaf note, containinig point
                None: point outside root box
        """
        x, y, z = point
        if self.is_root():
            if not self.in_box(point):
                return None
        else:
            if not _in_recursion:
                raise RuntimeError("Only root node can search for all leaves")

        if self.is_leaf():
            return self
        if len(self.cut_expr) > 1:
            raise ValueError("cut_expr is too long")
        key = list(self.cut_expr)[0]
        value = locals()[key]
        if value <= self.cut_expr[key]:
            return self.left.find_leaf(point, _in_recursion=True)
        return self.right.find_leaf(point, _in_recursion=True)

    def _split(self):
        """
        Split the node in two new nodes, if there is no cut_expr set and
        remaing cuts exist.
        """
        if self.cut_expr is None and self.remaining_cuts is None:
            raise RuntimeError(
                "Cannot split the mesh without cut_expr and" "remaining_cuts"
            )
        else:
            # create cut expression
            x, y, z = sympy.symbols("x y z")
            if "x" in self.cut_expr:
                left_cut_expression = x <= self.cut_expr["x"]
                right_cut_expression = x >= self.cut_expr["x"]
                key = "x"
            elif "y" in self.cut_expr:
                left_cut_expression = y <= self.cut_expr["y"]
                right_cut_expression = y >= self.cut_expr["y"]
                key = "y"
            elif "z" in self.cut_expr:
                left_cut_expression = z <= self.cut_expr["z"]
                right_cut_expression = z >= self.cut_expr["z"]
                key = "z"
            else:
                raise KeyError()

            # split the cuts into left / right
            left_cuts = self.remaining_cuts.copy()
            right_cuts = self.remaining_cuts.copy()
            left_cuts[key] = [
                value
                for value in self.remaining_cuts[key]
                if value <= self.cut_expr[key]
            ]
            right_cuts[key] = [
                value
                for value in self.remaining_cuts[key]
                if value > self.cut_expr[key]
            ]
            left_box = copy.deepcopy(self.box)
            right_box = copy.deepcopy(self.box)
            left_box[key][1] = self.cut_expr[key]
            right_box[key][0] = self.cut_expr[key]

            # actually cut!
            left_mesh, self.left_template = self.mesh.cut(
                left_cut_expression,
                at_intersection=self.at_intersection,
                return_template=True,
            )
            right_mesh, self.right_template = self.mesh.cut(
                right_cut_expression,
                at_intersection=self.at_intersection,
                return_template=True,
            )

            # two new Nodes
            self.left = Node(
                left_mesh,
                left_cuts,
                parent=self,
                internal_template=self.left_template,
                cut_expr=None,
                coord_sys=self.coord_sys,
                at_intersection=self.at_intersection,
                box=left_box,
            )
            self.right = Node(
                right_mesh,
                right_cuts,
                parent=self,
                internal_template=self.right_template,
                cut_expr=None,
                coord_sys=self.coord_sys,
                at_intersection=self.at_intersection,
                box=right_box,
            )

    def _choose_next_cut(self):
        """
        Set self.cut_expr by choosing the dimension with the most remaining
        cuts. Remove that cut from remaining cuts
        """
        largest = 0
        for key in self.remaining_cuts:
            if len(self.remaining_cuts[key]) > largest:
                largest = len(self.remaining_cuts[key])
                largest_key = key

        median = sorted(self.remaining_cuts[largest_key])[
            int(0.5 * (len(self.remaining_cuts[largest_key]) - 1))
        ]
        # pop median cut from remaining cuts
        self.remaining_cuts[largest_key] = [
            x for x in self.remaining_cuts[largest_key] if x != median
        ]
        self.cut_expr = {largest_key: median}

    def _convert_map_index(self, index):
        """
        Recursively getting the map fields index from root
        Args:
            index (int): map field index on leaf
                (index with respect to parent node, not to root)
        Returns:
            int: map field index
        """
        if self.is_root():
            return index
        else:
            return_value = self.parent._convert_map_index(
                self.parent._internal_template.maps[3].fields[0][int(index)]
            )
            return return_value

    def _convert_field_index(self, index):
        """
        Recursively getting the fields index from root

        Args:
            index (int): field index on leaf
                (index with respect to parent node, not to root)

        Returns:
            int: field index
        """
        if self.is_root():
            return index
        else:
            return_value = self.parent._convert_field_index(
                self.parent._internal_template.fields[0][int(index)]
            )
            return return_value

    @property
    def template(self):
        """
        Get the global template for a leaf. This can be applied to the root mesh
        with the cut method to retrieve exactly this leaf mesh again.

        Returns:
            tfields.Mesh3D: mesh with first scalars as an instruction on how to build
                this cut (scalars point to faceIndices on mother mesh). Can be
                used with Mesh3D.cut
        """

        if not self.is_leaf():
            raise RuntimeError("Only leaf nodes can return a template")

        if self._template is None:
            template = self._internal_template.copy()

            template_field = []
            if template.fields:
                for idx in template.fields[0]:
                    template_field.append(self._convert_field_index(idx))
                template.fields = [tfields.Tensors(template_field, dim=1, dtype=int)]

            template_map_field = []
            if len(template.maps[3]) > 0:
                for idx in template.maps[3].fields[0]:
                    template_map_field.append(self._convert_map_index(idx))
                template.maps[3].fields = [
                    tfields.Tensors(template_map_field, dim=1, dtype=int)
                ]
            self._template = template
        return self._template


class Searcher(Node):
    def __init__(self, mesh, n_sections=None, delta=0.0, cut_length=None):
        """
        Special cutting tree root node.
        Provides a fast point in mesh search algorithm (Searcher.in_faces)

        Args:
            n_sections (None or list of len 3):
                None: auto search n_sections
                list: number of sections in the index dimension
            delta (float): safety margin around the mesh to search in
            cut_length (None / float): characteristic cell size. Be carefull,
                to choose it high enough. If it is smaller than the largest
                triangle, a box could lie in the triangle without containing it.
        """
        minima = mesh.min(axis=0) - 0.0001
        maxima = mesh.max(axis=0) + 0.0001

        if n_sections is None or any([ns is None for ns in n_sections]):
            if cut_length is None:
                # project all triangels to have one point at 0, 0, 0
                triangles = mesh.triangles().copy()
                triangles.fields = []

                ab, ac = triangles.edges()
                bc = ac - ab
                side_lengths = np.concatenate(
                    [np.linalg.norm(side, axis=1) for side in [ab, ac, bc]]
                )
                # import mplTools as mpl
                # axis= tfields.plotting.gca(2)
                # mpl.plotHistogram(side_lengths, axis=axis)
                # mpl.plt.show()
                # quit()
                characteristic_side_length = np.max(side_lengths)
                cut_length = characteristic_side_length * 1.1

            elongation = maxima - minima
            n_sections_auto = np.round(elongation / cut_length).astype(int)

            if n_sections is not None:
                for i, ns in enumerate(n_sections):
                    if ns is not None:
                        n_sections_auto[i] = int(ns)
            n_sections = n_sections_auto
        elif cut_length is not None:
            raise ValueError("cut_length not used.")

        # build dictionary with cuts per dimension
        cut = {}
        for i, key in enumerate(["x", "y", "z"]):
            n_cuts = n_sections[i] + 1
            # [1:-1] because no need to cut at min or max
            values = np.linspace(minima[i], maxima[i], n_cuts)[1:-1]
            cut[key] = values

        return super(Searcher, self).__init__(
            mesh, cut, at_intersection="keep", delta=delta
        )

    def in_faces(self, tensors, delta=-1, assign_multiple=False):
        """
        TODO-0:
            * check case of point+-delta outside box!

        Examples:
            >>> import tfields
            >>> import numpy as np
            >>> mesh = tfields.Mesh3D.grid((0, 1, 2), (1, 2, 2), (2, 3, 2))
            >>> tree = tfields.bounding_box.Searcher(mesh)
            >>> points = tfields.Tensors([[0.5, 1, 2.1],
            ...                           [0.5, 0, 0],
            ...                           [0.5, 2, 2.1],
            ...                           [0.5, 1.5, 2.5]])
            >>> box_res = tree.in_faces(points, delta=0.0001)
            >>> usual_res = mesh.in_faces(points, delta=0.0001)
            >>> assert np.array_equal(box_res, usual_res)

        """
        if not self.is_root():
            raise ValueError("in_faces may only be called by root Node.")
        assert self.at_intersection == "keep", "Intersection method must be 'keep'"
        assert not assign_multiple, "Not yet implemented. Does interfere with delta."
        if delta == -1:
            delta = self.delta

        indices = np.full(tensors.shape[0], -1, dtype=int)
        if self.mesh.nfaces() == 0:
            if assign_multiple:
                return [[-1] * len(indices)]
            else:
                return indices

        with tensors.tmp_transform(self.mesh.coord_sys):
            for i, point in enumerate(iter(tensors)):
                leaf = self.find_leaf(point)
                if leaf is None:
                    continue
                if leaf.template.nfaces() == 0:
                    continue
                leaf_mask = leaf.template.triangles()._in_triangles(point, delta)
                original_face_indices = leaf.template.maps[3].fields[0][leaf_mask]
                if len(original_face_indices):
                    indices[i] = original_face_indices[0]
                    # if len(original_face_indices) > 1 -> assign_multiple_faces
        return indices


if __name__ == "__main__":
    import doctest

    # doctest.run_docstring_examples(Searcher.in_faces, globals())
    doctest.testmod()
