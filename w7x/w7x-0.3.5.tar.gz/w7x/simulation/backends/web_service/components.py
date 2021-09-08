"""
Web service backend of the components code
"""
import logging
import os
import numpy as np

import rna
import tfields
import w7x
from w7x.simulation.components import ComponentsBackend
from w7x.simulation.backends.web_service.base import (
    get_server,
    OsaType,
    to_osa_type,
    to_tfields_type,
)


LOGGER = logging.getLogger(__name__)
WS_SERVER = w7x.config.get_option("components.web_service", "server")
WS_DB = w7x.config.get_option("components.web_service", "database")


class Base(OsaType):
    """
    Base class for components db web service types
    """

    ws_server = WS_DB


class Polygon(Base):
    """
    element.vertices gives you the three points numbers to a triangle.
    This is normally refered to as face
    """

    prop_defaults = {"vertices": None}


class MeshedModel(Base):
    """
    Args:
        multiple ways:
            vertices (list)
            faces (list)

            - or -

            group from ObjFile

            - or -

            tfields.Mesh3D object
    Attributes:
        nodes (Points3D): = vertices (coordinates) of the points.
        elements (list[Polygon]): = faces (always three indices of points for a
            triangle). Starting at 1 here
    Examples:
        use with Mesh3D as inp
        >>> import tfields
        >>> from w7x.simulation.backends.web_service.components import MeshedModel
        >>> m = tfields.Mesh3D([[1,2,3], [3,3,3], [0,0,0], [5,6,7]],
        ...                    faces=[[0, 1, 2], [1, 2, 3]])
        >>> mm = MeshedModel(m)

        Get the osa type, in this case for field line server
        >>> fls = mm.as_input()

        return Mesh3D works
        >>> bool((m == mm.as_mesh3d()).all())
        True

        create with meshed Model from fls works
        >>> m2 = MeshedModel(fls).as_mesh3d()
        >>> assert tfields.Points3D(m2).equal(
        ...     [[ 1.,  2.,  3.],
        ...      [ 3.,  3.,  3.],
        ...      [ 0.,  0.,  0.],
        ...      [ 5.,  6.,  7.]])
        >>> assert tfields.Tensors(m2.faces).equal([[0, 1, 2], [1, 2, 3]])

    """

    prop_defaults = {
        "nodes": None,
        "elements": None,
        "nodesIds": None,
        "elementsIds": None,
    }

    def __init__(self, *args, **kwargs):
        args = list(args)
        if len(args) > 1:
            logging.error(" Implementation did not work.")
            raise NotImplementedError(
                " Implementation with args %s not yet implemented!" % args
            )
        if len(args) == 1 and issubclass(args[0].__class__, tfields.Mesh3D):
            mesh = args.pop(0)
            nodes = to_osa_type(mesh, ws_server=WS_DB)
            faces = mesh.faces + 1
            kwargs["nodes"] = kwargs.pop("nodes", nodes)
            kwargs["elements"] = kwargs.pop(
                "elements", [Polygon(vertices=face) for face in faces]
            )
        super().__init__(*args, **kwargs)

    @classmethod
    def from_mm_id(cls, mm_id):
        """
        Factory method to create from meshed model id
        """
        comp_db_server = get_server(WS_DB)
        # caching mechanism
        with rna.log.timeit(
            "[w7x cache] - Calling getComponentData(" "{mm_id})".format(**locals())
        ):
            component_data = comp_db_server.service.getComponentData(mm_id)
            obj = cls(component_data[0])
        return obj

    @classmethod
    def from_component(cls, component):
        """
        Factory method to create from component
        """
        return cls.from_mm_id(component.id)

    @classmethod
    def mesh3d(cls, mm_id):
        """
        Equivalent to MeshedModel(mm_id).as_mesh3d() but much faster cache
        as compared to cached MeshedModel. tfields loading is fast.

        Returns:
            tfields.Mesh3D
        """
        # caching mechanism
        mm_id_cache_path = os.path.join(
            w7x.config.get_option("global", "cache"),
            "components/mesh_mm_id_" + str(mm_id) + ".npz",
        )
        if os.path.exists(str(mm_id_cache_path)):
            with rna.log.timeit(
                "[w7x cache] - Loading Mesh3D for mm_id" " {mm_id}".format(**locals())
            ):
                obj = tfields.Mesh3D.load(mm_id_cache_path)
        else:
            with rna.log.timeit(
                "[w7x cache] - Calling MeshedModel({mm_id})"
                ".as_mesh3d()".format(**locals())
            ):
                instance = cls.from_mm_id(mm_id)
                obj = instance.as_mesh3d()
                obj.save(mm_id_cache_path)
        return obj

    def as_mesh3d(self):
        """
        Returns:
            tfields.Mesh3D
        """
        # pylint:disable=no-member
        faces = np.array([pol.vertices for pol in self.elements])
        faces -= 1
        # pylint:disable=no-member
        return tfields.Mesh3D(to_tfields_type(self.nodes), faces=faces)


class HistoryNote(Base):
    """
    History note
    """

    prop_defaults = {
        "comment": None,  # str
        "author": None,  # str
        "date": None,  # datetime
        "method": None,  # str
    }


class ComponentStorageInfo(Base):
    """
    Component storage informations
    """

    prop_defaults = {
        "comment": None,  # str
        "polygonTypes": None,  # List[int]
        "numNodes": None,  # int
        "id": None,  # str
        "machine": "w7x",  # str, ws default is None
        "min": None,  # List[float]
        "numElements": None,  # int
        "state": None,  # str
        "location": None,  # str
        "accuracy": None,  # float
        "max": None,  # List[float]
        "name": None,  # str
        "subids": None,  # List[str]
        "author": None,  # str
        "method": None,  # str
        "resolution": None,  # float
        "history": None,  # List(HistoryNote)
    }


class FullComponentEntry(Base):
    """
    Full component entry, bringing together information and data about a component
    """

    prop_defaults = {
        "info": None,  # ComponentStorageInfo
        "data": None,  # MeshedModel
    }


class ComponentsWebServiceBackend(ComponentsBackend):
    """
    Backend implementation
    """

    @staticmethod
    @w7x.node
    def _get_mesh(mm_id):
        return MeshedModel.mesh3d(mm_id)

    @staticmethod
    def _module(state, **kwargs):
        component = kwargs.pop("component")
        mm_id = component.id
        comp_db_server = get_server(
            w7x.config.get_option("components.web_service", "server")
        )
        component_info = comp_db_server.service.getComponentInfo(mm_id)[0]
        return int(component_info.location.replace("m ", ""))

    @staticmethod
    @w7x.node
    # pylint:disable=too-many-locals
    def _mesh_slice(component, phi) -> tfields.TensorMaps:
        mesh_server = get_server(WS_SERVER)

        mesh_set = mesh_server.types.SurfaceMeshSet()
        wrap = mesh_server.types.SurfaceMeshWrap()
        reference = mesh_server.types.DataReference()
        reference.dataId = "10"
        wrap.reference = reference
        mesh_set.meshes = [
            wrap,
        ]

        # append mm_id_wrap
        mm_id_wrap = mesh_server.types.SurfaceMeshWrap()
        mm_id_reference = mesh_server.types.DataReference()
        mm_id_reference.dataId = str(component.id)
        mm_id_wrap.reference = mm_id_reference
        mesh_set.meshes.append(mm_id_wrap)

        # ask web service for result and process it to right format
        # careful: Returns None if there is no component.
        res = mesh_server.service.intersectMeshPhiPlane(phi, mesh_set)

        # pylint:disable=too-many-nested-blocks
        if isinstance(res, list):
            vertex_index_offset = 0
            vertex_list = []
            nodes = []
            edges = []
            if res[0] is None:
                return tfields.TensorMaps([])
            if str(type(res[0])) == "<class 'osa.xmltypes.PolygonPlaneIntersection'>":
                # Result is from MeshPhiIntersection
                for intersection in res:
                    # res.surfs has entries for every phi
                    vertex_points = to_tfields_type(intersection.vertices)
                    vertex_points.transform(tfields.bases.CYLINDER)
                    # phi is correct with rounding precision before.
                    # This way it is perfectly correct
                    vertex_points[:, 1].fill(phi)
                    while True:
                        # This while is only active if duplicates are found to be mappable to len
                        # 1 or 2
                        if len(vertex_points) == 1:
                            nodes.append(
                                np.arange(len(vertex_points)) + vertex_index_offset
                            )
                        elif len(vertex_points) == 2:
                            edges.append(
                                np.arange(len(vertex_points)) + vertex_index_offset
                            )
                        else:
                            duplicates = tfields.lib.util.duplicates(
                                vertex_points, axis=0
                            )
                            if len(set(duplicates)) <= 2:
                                vertex_points = vertex_points[list(set(duplicates))]
                                continue
                            raise ValueError("More than two edges given")
                        break

                    vertex_list.append(vertex_points)
                    vertex_index_offset += len(vertex_points)

                slices = tfields.TensorMaps(tfields.Tensors.merged(*vertex_list))
                slices.maps[1] = tfields.Tensors(nodes, dim=1)
                slices.maps[2] = tfields.Tensors(edges, dim=2)
                return slices
            LOGGER.error("Can not handle result list content.")
        elif res is None:
            LOGGER.debug(
                "Result was None. Probably there was no"
                "intersection of the mesh with this plane."
            )
        else:
            LOGGER.error("Result is not of the right type")
        return None
