"""Core classes of Fledge.

Todo:
    * Spaces should be non-generic?

"""
# flake8: noqa
from __future__ import annotations

import collections
import logging
from abc import ABC
from abc import abstractmethod
from copy import deepcopy
from typing import Any
from typing import Dict
from typing import final
from typing import Generic
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import Union

import networkx as nx  # type: ignore
from pyvis.network import Network  # type: ignore

from .exceptions import NoPathError
from .exceptions import NotInvertibleError
from .exceptions import NotReversibleError
from .named import Named
from .registry import Registry

log = logging.getLogger(__name__)


# Type variables for spaces
Q = TypeVar("Q", bound="Space")
R = TypeVar("R", bound="Space")
S = TypeVar("S", bound="Space")
S_co = TypeVar("S_co", covariant=True, bound="Space")
T = TypeVar("T", bound="Space")

# Type variables for the types of spaces.
Q_t = TypeVar("Q_t")
R_t = TypeVar("R_t")
S_t = TypeVar("S_t")
T_t = TypeVar("T_t")

# Type variables bound to the various core classes.
N = TypeVar("N", bound="Node")
N_co = TypeVar("N_co", covariant=True)
N_new = TypeVar("N_new", bound="Node")
N0 = TypeVar("N0", bound="Node")
N1 = TypeVar("N1", bound="Node")
N2 = TypeVar("N2", bound="Node")
N3 = TypeVar("N3", bound="Node")
F0 = TypeVar("F0", bound="Frame")
F1 = TypeVar("F1", bound="Frame")
F2 = TypeVar("F2", bound="Frame")
F = TypeVar("F", bound="Frame")
F_co = TypeVar("F_co", bound="Frame")
F_contra = TypeVar("F_contra", contravariant=True)
F_new = TypeVar("F_new", bound="Frame")
B = TypeVar("B", bound="Body")
E = TypeVar("E", bound="Edge")
E_new = TypeVar("E_new", bound="Edge")


# Type variables bound to types of nodes
N_t = TypeVar("N_t")
N1_t = TypeVar("N1_t")
N2_t = TypeVar("N2_t")
F_t = TypeVar("F_t")
F1_t = TypeVar("F1_t")
F2_t = TypeVar("F2_t")
B_t = TypeVar("B_t")


Ref = TypeVar("Ref", bound="Reference")
Ref_new = TypeVar("Ref_new", bound="Reference")
Tr = TypeVar("Tr", bound="Transform")
Tr_new = TypeVar("Tr_new", bound="Transform")
P = TypeVar("P", bound="Projection")
Proj = TypeVar("Proj", bound="Projection")

# registries.
_space_registry = Registry()
_projection_registry = Registry()


def get_space(space: Union[str, S]) -> S:
    """Get a space by name."""
    if isinstance(space, str):
        return _space_registry[space]
    elif isinstance(space, Space):
        return space
    else:
        return TypeError


def get_projection(projection: Union[str, P]) -> P:
    """Get a projection by name."""
    if isinstance(projection, str):
        return _projection_registry[projection]
    elif isinstance(projection, Projection):
        return projection
    else:
        raise TypeError


# TODO: Nodes can be generic, NOT spaces, I think, only spaces and edges.


class Space(Named):
    """A space is a set of objects.

    To be precise, a space is a subset of nodes in the reference graph. `fledge.Space` represents
    this abstraction by containing all the frames internally. It does not contain references to
    non-frame nodes, but it does support membership tests for these types, by checking the `space`
    attribute of the node.

    A `Space` represents a physical space, like a room or a 2D sheet of paper. It contains nodes and
    can be refered to by a name. Spaces are created when someone instantiates a Frame without
    providing a space, or if the space name has not been made yet.

    All space instances are mutually disjoint, by definition, since the .

    """

    _frames: Dict[str, Frame]

    def __init__(self, name: Optional[str] = None) -> None:
        """TODO: docs."""
        Named.__init__(self, name)
        _space_registry.add(self)

        self._frames = dict()

    @final
    def rename(self, name: str) -> None:
        """Rename the space."""
        _space_registry.remove(name)
        super(Space, self).rename(name)
        _space_registry.add(self)

    def get(self, frame: Union[str, Frame[Any]]) -> Frame:
        """Get the frame by name or instance.

        If a `Frame` instance is provided, this merely checks that `frame` is in `self`.

        """
        if isinstance(frame, Frame):
            name = frame.name
        elif isinstance(frame, str):
            name = frame
        else:
            raise TypeError

        return self._frames[name]

    def add(self, frame: Frame) -> None:
        """Add the frame to the space."""
        if not isinstance(self, frame.space_type_bound):
            raise TypeError(f"cannot add {frame} to {self}")

        self._frames[frame.name] = frame

    def remove(self, frame: Union[str, Frame]) -> None:
        """Destroy the given frame."""
        if isinstance(frame, str):
            del self._frames[frame]
        elif isinstance(frame, Frame):
            del self._frames[frame.name]
        else:
            raise TypeError

    def __contains__(self, item: Union[str, Node]) -> bool:
        """Determine whether `item` is in the space.

        In GeoFrame, all nodes must store a reference to their set. Thus, this
        method simply checks whether the node's space IS this one.

        """
        if isinstance(item, str):
            return item in self._frames
        elif isinstance(item, Frame):
            return item.name in self._frames
        elif isinstance(item, Node):
            return item.space == self
        else:
            return NotImplemented

    def __getitem__(self, frame: Union[str, Frame]) -> Frame:
        """TODO: docs."""
        return self.get(frame)

    def __setitem__(self, name: str, frame: Frame):
        """TODO: docs."""
        if frame.name != name:
            raise ValueError
        self._frames[name] = frame

    def __iter__(self):
        """TODO: docs."""
        return iter(self._frames.values())

    def __len__(self):
        """TODO: docs."""
        return len(self._frames)

    def __str__(self):
        """TODO: docs."""
        return f'{self.__class__.__name__}("{self.name}")'

    def frames(self):
        return self._frames.values()

    def names(self):
        return self._frames.keys()

    def items(self):
        return self._frames.items()


class Node(Generic[S_co]):
    """A node represents an object in a physical space.

    A node can only belong to one space. All nodes contain references to the space they are in, but
    only frames are referenced by their space.

    Args:
        space: the name of the space this node is in. If not provided, or name
            does not already refer to this space, a new space is created of type
            `self.space_type_bound`.

    Attributes:
        defining_edge: the edge from `defining_frame` to `self`, if it exists.
        defining_frame: the frame which defines this node, if it exists.
        space: the space this node is in. If a name is provided, and the name is
            not used, a new
            space is created. If None, and `defining_frame` is provided as an
            instance, defining_frame.space is used.
        incoming_projections: mapping from projection names to projections.
        space_type_bound: This node can only belong to subtypes of `space_type_variable`. This class
            variable should be fixed for each class. It must correspond to the type of the Node.

    """

    # If the Node is not a generic node, then this must be provided in the class definition.
    space_type_bound: type = Space

    # Attributes
    _defining_edge: Optional[Edge]
    _defining_frame: Optional[Frame]
    space: S_co
    incoming_projections: Dict[Projection, Frame] = dict()

    def __init__(
        self,
        defining_edge: Optional[Edge] = None,
        defining_frame: Union[None, str, Frame] = None,
        space: Union[None, str, S_co] = None,
    ) -> None:
        """TODO: docs."""
        if space is None:
            if isinstance(defining_frame, Frame):
                self.space = defining_frame.space
            elif isinstance(defining_frame, str):
                raise ValueError(
                    f"If `space` not provided, `defining_frame` must be a Frame object. Got the name: {defining_frame}"
                )
            else:
                raise ValueError(
                    f"If `space` not provided, `defining_frame` must be provided directly."
                )
        elif isinstance(space, str):
            if space in _space_registry:
                self.space = get_space(space)
            else:
                self.space = self.space_type_bound(name=space)
        elif isinstance(space, Space):
            if not issubclass(type(space), self.space_type_bound):
                raise TypeError(
                    f"{self.__class__.__name__} nodes must be in a space that subclasses "
                    f"{self.space_type_bound.__name__}"
                )

            self.space = space
        else:
            raise TypeError

        self._defining_edge = None
        self._defining_frame = None
        self.set_definition(defining_edge, defining_frame)

    @property
    def defining_edge(self) -> Optional[Edge]:
        """TODO."""
        return self._defining_edge

    @property
    def defining_frame(self) -> Optional[Frame]:
        """TODO."""
        return self._defining_frame

    def set_definition(self, edge: Optional[Edge], frame: Union[None, str, Frame]):
        """Set the defining edge or frame for this node.

        Performs checks to ensure that both or neither are defined. Note that Bodies should have an
        additional check that neither are None.

        Note that this cannot be used to remove definitions. That is, a value of None will not
        override an existing definition. For that, use the `orphan()` method.

        """
        # First, get the actual edge and frame being set to. If these are None, then the stored values are used.
        if edge is None:
            e = self._defining_edge
        else:
            # Check output type of the edge.
            if not isinstance(self, edge.output_type):
                raise TypeError(
                    f"{edge} connects to {edge.output_type.__name__} nodes, cannot connect to: {self}"
                )

            e = edge

        if frame is None:
            f = self._defining_frame
        elif isinstance(frame, str):
            if frame in self.space:
                f = self.space.get(frame)
            else:
                raise RuntimeError("frame not in space")
        else:
            f = frame

        if f is None and e is None:
            pass
        elif f is not None and e is not None:
            # Check f and e are compatible.
            if not issubclass(type(f), e.input_type_bound):
                raise TypeError(
                    f"input nodes to {e} must subclass {e.input_type_bound.__name__}, got: {f}"
                )
        else:
            RuntimeError(f"Must define both frame and edge; got frame {f}, edge {e}")

        self._defining_frame = f
        self._defining_edge = e

    # TODO: re-add to flake8
    def connect(  # noqa: C901
        self,
        edge: Edge,
        frame: Union[None, str, Frame] = None,
        space: Union[None, str, Space] = None,
    ) -> None:
        """Add or modify an incoming edge to this Node.

        Reposition this node by redefining its incoming edge, possibly in
        another frame.

        Note that this does not create a new frame but rather redefines this
        existing one. To create a new frame, use
        `defining_frame.traverse(defining_edge)`.

        Args:
            edge: The new incoming edge which will define the frame.
            frame: The frame to define this frame in. If None, `self.defining_frame` is
                used. If `self.defining_frame is None` (i.e. `self` is a source node), then an
                existing frame or the name of an existing frame must be provided.
            space: Must be provided if edge is a projection and only the name of the source frame is
                provided, to find the instance of the frame. Otherwise not needed.

        Raises:
            RuntimeError: If the space is not provided for frame lookup by string.
            TypeError: If the types being connected do not align.
            ValueError: If insufficient args are provided.

        """
        TypeError(
            "Nodes cannot be connected. They are singular (useless) objects in space with no frame of reference."
        )

    @final
    def in_frame(  # noqa: C901
        self,
        frame: Union[str, Frame],
        projection: Union[None, str, Projection, list[Union[str, P]]] = None,
    ) -> Edge:
        """Get the representation of the object in the given frame.

        If no projection is provided, `in_frame()` will return a new edge which leads to the same
        node (theoretically) but from the given frame, in the same space.

        If a projection is provided, `in_frame()` will return a new node by taking that projection
        from the projection's input space to `self.space`, returning an edge to a *wholly different*
        node in `frame.space`.

        If multiple projections are provided, only one is considered at a time. This is useful if
        the path to the desired frame passes through more than one intermediate space.

        If the desired frame is reachable *without* traversing the given projection,

        In general, the projection needs to be provided that links `self.space` to `frame.space`.
        This is because multiple projections might link the spaces, each of which would lead to a
        `different` end-node. GeoFrame resolves this ambiguity by only allowing one projection to be
        allowed to be traversed at a time.

        Args:
            frame: the desired frame to represent `self` in, or the name of the frame.
            projection: a projection or list of projections which are valid to cross, in order.

        Returns:
            Edge: The edge from `frame` to `self`.

        Raises:
            NoPathError: if there is no path to the desired frame utilizing the projection. This is
                also raised if the desired frame is reachable without using a projection provided,
                to prevent confusion about which space a frame is in.
            RuntimeError: If errors are encountered in the reference graph.

        """
        # TODO: don't combine edges unless you need to, just keep a list of the edges and then combine
        # the ones on the chosen path.
        projections: collections.deque[Projection]
        desired_frame: Optional[Frame]
        edge: Edge
        discovered: set[Frame]
        queue: collections.deque[tuple[Frame, Edge]]
        df: Frame

        if projection is None:
            projections = collections.deque()
        elif isinstance(projection, (str, Projection)):
            projections = collections.deque([get_projection(projection)])
        elif isinstance(projection, list):
            projections = collections.deque(map(get_projection, projection))
        else:
            raise TypeError

        if len(projections) == 0:
            # There are no projections, so the frame must be in the starting space
            desired_frame = self.space.get(frame)
        else:
            # We may not know the desired frame yet. Only when projections is empty
            desired_frame = None

        if isinstance(self, Frame):
            edge = self.identity()
            discovered = set([self])
            queue = collections.deque([(self, edge)])
        elif self.defining_edge is None or self.defining_frame is None:
            raise NoPathError(f"node has no frame of reference: {self}")
        else:
            edge = self.defining_edge
            discovered = set([self.defining_frame])
            queue = collections.deque([(self.defining_frame, self.defining_edge)])

        while len(queue) > 0:

            f, e = queue.popleft()
            if not isinstance(f, Frame):
                raise RuntimeError(f"not a frame: {f}")

            # We have finally arrived at the desired space. Get the desired frame.
            if len(projections) == 0 and desired_frame is None:
                desired_frame = f.space.get_frame(frame)

            # There are no more projections to traverse, and the desired frame is found.
            if len(projections) == 0 and f == desired_frame:
                break

            # Enqueue the frame that f is in, if it is not a source.
            if (
                f.defining_frame is not None
                and f.defining_edge is not None
                and f.defining_frame not in discovered
            ):
                if f.defining_frame.space != f.space:
                    raise RuntimeError(f"mismatch spaces: {f.defining_frame.space}, {f.space}")
                discovered.add(f.defining_frame)
                queue.append((f.defining_frame, f.defining_edge @ e))

            # enqueue all frames that are defined by f
            for df in f.defined_frames:
                if df.defining_edge is None:
                    raise RuntimeError
                if df not in discovered and df.defining_edge.invertible():
                    if df.space != f.space:
                        raise RuntimeError(f"mismatch spaces: {df.space}, {f.space}")
                    discovered.add(df)
                    queue.append((df, df.defining_edge.inverse() @ e))

            # Check if projections[0] is among the projections coming into f.
            for p, incoming_f in self.incoming_projections.items():
                if p == projections[0]:
                    # Follow the projection into the new space. (Search starts over)
                    if incoming_f.space == f.space:
                        raise RuntimeError("projections cannot connect frames in the same space")
                    queue.clear()
                    queue.append((incoming_f, p @ e))
                    projections.popleft()
                    break

        return e

    @final
    def into(
        self,
        frame: Union[str, Frame],
        **kwargs,
    ) -> Node:
        """Creates a new node defined in the new frame in the same location as this one.

        The difference between `in_frame()` and `into()` is that `in_frame()` returns the edge
        representation without creating a new node. `into()` returns a new node which could be
        manipulated independently of the old one.

        """
        f = self.space.get(frame)
        return f.traverse(self.in_frame(frame), **kwargs)

    def orphan(self) -> None:
        """Orphan this node by disconnecting it from all other nodes.

        Sub-classes should override this.

        """
        self._defining_frame = None
        self._defining_edge = None

    def is_source(self) -> bool:
        """Whether the node has a defining edge (and frame)."""
        return self.defining_edge is not None and self.defining_frame is not None

    def is_orphan(self) -> bool:
        """Should encompass any other incoming or outgoing edges for a frame."""
        return self.is_source()

    def vis_properties(self) -> Dict[str, Any]:
        """Get the dictionary of custom properties to set for this node.

        Returns:
            Dict[str, Any]: Keyword arguments passed.
        """
        return dict(shape="dot")

    #
    # Convenience methods
    #

    # TODO: use x[f] to mean x.in_frame(f) and x.over(p) to mean x.in_frame(<frame pointed to by p>,
    # p). This means spaces must contain a mapping from the named projections to the frames they
    # point to.
    #
    def __getitem__(
        self,
        frame: Union[str, F],
    ) -> E:
        """Get the edge from `self` to `frame`.

        Args:
            frame (Union[str, F]): A frame name or instance in the same space as `self`.

        Raises:
            NotImplementedError: TODO.
        """
        raise NotImplementedError


class Frame(Node[S_co]):
    """A Frame provides a frame of reference to describe an object or `Body` in that space.

    A Frame has in-degree <= 1 (not counting the self-loop, which all Frames have) and any
    out-degree. Frames are similar to Bodies, in that they usually have one incoming edge and can be
    referenced in other frames, but they are not the same. A frame may have no incoming edges, and
    Frames cannot be projected onto other spaces.

    since they will be defined in connection to another frame, except for the "world" frame, which
    has no incoming edges. (There may be more than one world frame.)

    That is, most Frames are also Bodies, from the perspective of their own reference frame.

    Frames can be sources in the graph, a "world frame". A "world" is a connected component of the
    overall universe, which is directed and acyclic, where the "world frame" is the source node.

    Frames can be subclassed to specify how a point would be represented in that frame, and to have
    non-generic frames that only exist in one kind of space (e.g. CartesianFrame3D, which only
    exists in Euclidean3D space.) Sub-classes are responsible for calling super().

    Sub-classes may wish to override:
    * `identity()`
    * `space_type_bound`, a class variable.

    """

    # Attributes
    defined_frames: set[Frame]
    defining_edge: Transform

    def __init__(
        self,
        defining_edge: Optional[Edge] = None,
        defining_frame: Union[None, str, Frame] = None,
        space: Union[None, str, S_co] = None,
        name: Optional[str] = None,
    ) -> None:
        """A frame .

        Args:
            defining_edge (Optional[E], optional): The edge from `defining_frame` to self.
                Must be provided if frame is not None.
            defining_frame (Optional[Union[str, F]], optional): The reference frame defining this one,
                if it exists. A Frame does not need to be defined in terms of another frame.
                Defaults to None.
            space (Optional[Union[str, S]], optional): The space (or name of the space) that this frame is in.
                This is only needed when `defining_frame` is a `str`, or if this Frame is an orphan,
                but its space has already been created.
                Then it should be specified, or else a new space is created using.
                If `space` and `defining_frame` are not provided, a new space is created using
                `self.space_type_bound`.
                If `defining_frame` is provided, that space is used.
                If both provided, they must match. Defaults to None.
            name (Optional[str], optional): Optional name for the frame. Defaults to None.

        Raises:
            ValueError: If `space` is None and a name is given for `defining_frame`.
        """
        if space is None and defining_frame is not None:
            if not isinstance(defining_frame, Frame):
                raise ValueError(
                    "If `space` is not provided, the Frame instance must be provided directly."
                )
            space = defining_frame.space

        # creates the space, if it doesn't exist or is None
        super(Frame, self).__init__(
            defining_edge=defining_edge,
            defining_frame=defining_frame,
            space=space,
        )

        # Make a unique name, if not provided.
        if name is None:
            name = f"{self.__class__.__name__}_{len(self.space.frames())}"

        self.name = name
        self.space.add(self)

        # initialize internal graph connections
        self.defined_frames = set()
        self.incoming_projections = dict()

    def __hash__(self):
        """Allows the frame to hashed using its space name and name."""
        return hash(self.space.name + self.name)

    def rename(self, name: str) -> None:
        """Rename the frame and update the space.

        Sub-classes may wish to modify the name somehow. They are responsible for calling
        `super().rename(name)`.
        """

        self.space.remove(self)
        self.name = name
        self.space.add(self)

    def identity(self) -> Identity:
        """Get an identity transform on edges from this frame.

        Should be overridden by sub-classes to get identities on those frame types.

        """
        return Identity()

    def orphan(self):
        """Orphan this frame by removes all edges to/from it, except to bodies."""
        self.frame.defined_frames.remove(self)
        for f in self.defined_frames:
            f.defining_frame = None
            f.defining_edge = None

    def is_orphan(self) -> bool:
        """Whether the frame is completely unconnected."""
        return (
            self.is_source and len(self.defined_frames) == 0 and len(self.incoming_projections) == 0
        )

    def connect(
        self,
        edge: Edge,
        frame: Union[None, str, Frame] = None,
        space: Union[None, str, Space] = None,
    ) -> None:
        """TODO."""
        if isinstance(edge, Projection):
            # An incoming projection is added to `incoming_projections`
            if frame is None:
                raise RuntimeError(
                    "the source frame must be provided when connecting an incoming projection"
                )
            # Get the frame instance.
            if isinstance(frame, str):
                if space is None:
                    raise ValueError("must provide the space of the input frame for lookup")
                s = get_space(space)
                f = s.get(frame)
            else:
                f = frame
            # Add the edge to the incoming projections, as well as its reverse.
            self.incoming_projections[edge] = f
            if edge.reversible():
                f.incoming_projections[edge.reverse()] = self

        elif isinstance(edge, Transform):
            # An incoming transform
            if space is not None and get_space(space) != self.space:
                raise RuntimeError("space mismatch")
            self.set_definition(edge, frame)

        elif isinstance(edge, Reference):
            raise TypeError("cannot connect a Frame with a Reference edge")

        else:
            raise TypeError

    def traverse(self, edge: Edge, name: Optional[str] = None) -> Union[Frame, Body]:
        """Define new bodies or frames in the same space as this one, by traversing an edge.

        Sub-classes may wish to implement wrappers around connect, like `CartesianFrame3D.point()`,
        which would create a new point, but they should not override connect.

        The traverse method is unique to Frame nodes, since edges can only begin at frames.

        Args:
            edge: the edge to follow. If a transform or reference, this is the defining edge of
                the resulting node. Cannot be a projection.
            kwargs: other information to pass to the output node constructor.

        Returns:
            Union[Frame, Body]: A new node in the reference graph, either a frame or a body.

        Raises:
            TypeError: If the frame type is not a subclass of `edge.input_frame_type`.
            ValueError: If `edge` is a projection.
        """
        if not issubclass(type(self), edge.input_type_bound):
            raise TypeError(
                f"cannot connect {self} using {edge}, because the edge requires nodes that subclass"
                f" {edge.input_type_bound}"
            )

        if isinstance(edge, Projection):
            raise ValueError(
                "projections cannot be traversed because they require knowing both endpoints"
            )

        new_node: Union[Frame, Body]
        if issubclass(edge.output_type, Frame):
            new_node = edge.output_type(
                defining_edge=edge.copy(),
                defining_frame=self,
                space=self.space,
                name=name,
            )
            self.defined_frames.add(new_node)
        elif issubclass(edge.output_type, Body):
            new_node = edge.output_type(
                defining_edge=edge.copy(), defining_frame=self, space=self.space
            )
        elif issubclass(edge.output_type, Identity):
            # Identity is a special case, since it could be traversed from a Body.
            raise NotImplementedError("todo")
        else:
            raise TypeError()

        return new_node

    def full_name(self):
        """A full name for the frame, guaranteed to be unique."""
        return f"{self.space.name}/{self.name}"

    def vis_properties(self) -> Dict[str, Any]:
        """Visualization properties."""
        return dict(shape="box")


class Body(Node[S_co]):
    """A Body is an object in space, connected to a frame in the same space.

    In Fledge, a Body has in-degree == 1 and out-degree == 0. This means it is defined precisely
    by exactly one reference frame (although it may have cached references to others).

    Bodies are usually not created directly but rather by their defining edges via `traverse()`.

    """

    defining_edge: Reference  # E[F_t, B_t]
    defining_frame: Frame[S_co]  # F[S]

    def __init__(
        self,
        defining_edge: Reference,
        defining_frame: Union[str, Frame],
        space: Optional[Union[S_co, str]] = None,
    ) -> None:
        """A body is an object being referenced by a frame.

        Args:
            defining_edge (Ref): The reference edge that defines this body in a frame.
            defining_frame (Union[str, F]): The frame this body is defined in.
            space (Optional[S], optional): The space containing this body.
                Redundant unless the frame name is provided. Defaults to None.

        Raises:
            ValueError: If either the defining edge or frame are None.
        """
        if defining_edge is None or defining_frame is None:
            raise ValueError("bodies must be defined in a frame with an edge")

        super(Body, self).__init__(
            defining_edge=defining_edge, defining_frame=defining_frame, space=space
        )

    @final
    def connect(  # noqa: C901
        self,
        edge: Edge,
        frame: Union[None, str, Frame] = None,
        space: Union[None, str, Space] = None,
    ) -> None:
        """TODO."""
        if isinstance(edge, Reference):
            if space is not None and get_space(space) != self.space:
                raise RuntimeError("space mismatch")
            self.set_definition(edge, frame)
        else:
            raise TypeError

    def is_source(self) -> bool:
        """Bodies are never sources, because only frames are."""
        return False

    def is_orphan(self) -> bool:
        """Bodies are never orphans, because they are attached to a frame."""
        return False


class Edge(ABC, Generic[N1, N2]):
    """An Edge exists as a mathematical description of spatial objects (Nodes).

    An edge doesn't know about the particular instances of the nodes that it goes between, only the
    types of those nodes, as class variables. These are upper bounds on the type of nodes that the
    edge can go between. The nodes, in turn have upper bounds on the type of space they can be in.

    Edges usually have numrical representations. At least one of these should be implemented in the
    `__array__()` method.

    Sub-classes must define `input_type_bound` and `output_type` `join`, which is used by
    `__matmul__`. `join` defines how the edge interracts with other edges.
    `output_type` is used by a frame's `traverse()` method to traverse the edge.

    Sub-classes may also wish to implement `inverse()`, which finds the inverse of the edge. The
    `invertible()` method simply checks whether inverse() returns None, in which case the edge is
    not invertible.

    Finally, subclasses likely should have implementations of `__array__` and/or `__float__` as
    appropriate.

    Broadly, there are two types of edges:
    - Defining edges: which are the unique descriptions of a node in space. There is only one per
      node.
    - Projection edges: which go between spaces and result in new nodes to be created.

    There are four types of edges.
    * An Identity is a self-loop. It isn't very useful except as a building block for other edges.
    * A Reference is a defining Edge for a Body, where `R == S` is true.
       * References originate in Frames and are only stored in the Body's they reference.
       * A search only traverses a reference if it starts at a Body.
       * References are not invertible or reveresible, since Body's cannot have outgoing edges.
    * A Transform is a defining Edge for a Frame.
       * Transform edges go from a Frame to a different Frame in the same space.
       * References may be invertible.
    * A Projection is an Edge from a Frame in one space to a Frame in a different space.
       * An `onto()` search is limited to traversing one projection at a time.
       * Strictly speaking, projections are not invertible by definition, since they cannot be
         idempotent. However, for simplicity, we consider a projection to be invertible if there is
         a known projection in the opposite direction, even though it cannot return the original
         node exactly.

    Edges can be composed together to form a shortcut over the path they form. This is done with the
    `@` operator, as with matrix multiplication. Conceptually, edges can transform other edges but not
    non-edge nodes.

    If an edge is invertible, it is responsible for handling its own inverse. For example, if a
    point is actually moved, so that the edge to it is changed, the edge must change its own inverse
    as well to match.

    """

    input_type_bound: Type[Node]
    # input_type_bound: Type[Frame]
    # output_type: Union[Type[Frame], Type[Body]]
    output_type: Type[Node]

    def __matmul__(self, other: Edge[N2, N3]) -> Edge[N1, N3]:
        """The matmul operator returns a new edge equivalent to traversing self and other.

        Say I have a world frame W, frames A and B both defined in W, and a body x in frame B.

            A <----- W -----> B ----> x
                T_WA     T_WB     x_B

        where T_WA is A.incoming_edge, T_WB is B.incoming_edge, and x_B is x.incoming_edge.

        The numerical representation of x in frame A would be:

        .. code-block::

            T_WA.inverse() @ T_WB @ x_B

        A reference edge can only be placed at the end of this chain.

        Sub-classes should implement `join()` rather than overriding this function directly.

        Args:
            other (E): The other edge.

        Returns:
            Edge[F, N_new]: A new edge of type `self.output_type`.

        Raises:
            TypeError: If `self.output_type` is not a subclass of `other.input_type_bound`.
            NotImplementedError: If `other` is not an edge.

        """
        # TODO: gracefully handle cases where other is some other type (e.g. an array) that can be
        # interpreted as an edge in context.
        if not isinstance(other, Edge):
            raise NotImplementedError

        if not issubclass(self.output_type, other.input_type_bound):
            raise TypeError(
                f"cannot join {self} (output type {self.output_type.__name__}) "
                f"with {other} (input type bound {other.input_type_bound.__name__})"
            )

        return self.join(other)

    @abstractmethod
    def join(self, other: Edge[N2, N3]) -> Edge[N1, N3]:
        """Join the two edges together.

        This is the functional representation of the edge, meant to be overwridden by the user.

        Args:
            other (E): The other edge.

        Returns:
            E_new: A new edge of type `self.output_type`.

        """
        pass

    def __rmatmul__(self, other: Edge[N0, N1]) -> Edge[N0, N2]:
        """Edges might be joined with potential edges not yet made into edges."""
        if not isinstance(other, Edge):
            raise NotImplementedError

        return other @ self

    def inverse(self) -> Edge[N2, N1]:
        """Get the inverse of the edge, if it exists.

        Returns:
            Optional[E_new]: The inverse edge, if the edge is invertible.

        Raises:
            NotInvertibleError: If the edge is not invertible.
        """
        raise NotInvertibleError

    def invertible(self) -> bool:
        """Determine whether the edge is invertible.

        Sub-classes may wish to override this method if the invertibility is known without
        attempting to actually compute the inverse.

        Returns:
            bool: True if the class is invertible.

        """
        try:
            self.inverse()
            out = True
        except NotInvertibleError:
            out = False
        return out

    def copy(self):
        """Perform a deepcopy of self."""
        return deepcopy(self)


class Identity(Edge[N, N]):
    """The generic identity edge, which is a self-loop.

    Sub-classes may wish to implement __array__ to represent numerically meaningful identity
    functions.

    """

    def join(self, other: Edge[N1, N2]) -> Edge[N1, N2]:
        """The output contains the same values as the input, but it is not the same."""
        return other.copy()

    def inverse(self):
        """I^-1 = I."""
        return self

    def invertible(self):
        """I is always invertible."""
        return True


class Reference(Edge[F, B]):
    """A Reference is a Edge that terminates at a Body.

    References are not invertible, and they cannot be joined together with matmul.

    Note that the bodies these references describe *may* implement matmul, such as vectors being
    multiplied, but edges are descriptions, and only edges between frames can be joined.

    The base reference is a so-called "generic" reference, because it can be used to connect nodes
    but it doesn't contain any data.

    """

    input_type_bound = Frame
    output_type = Body

    def __init__(self) -> None:
        """Checks whether the output type is a body."""
        if not issubclass(self.output_type, Body):
            raise TypeError(
                f"references must map to a body. Got output_type: {self.output_type.__name__}"
            )

        super(Reference, self).__init__()

    @final
    def join(self, other):
        """References have no join."""
        raise ValueError("cannot join reference with any other edge")

    def inverse(self):
        """References are not invertible (in the spatial sense)."""
        return None

    def invertible(self):
        """Can't invert a reference."""
        return False


class Transform(Edge[F1, F2]):
    """A Transform is an edge to a frame in the same space.

    The base transform is invertible, defines only generic relationship, and stores no information.
    When joined with more sophisticated edges, it makes them generic.

    """

    input_type_bound = Frame
    output_type = Frame

    def __init__(self) -> None:
        """Checks whether the output type is a frame."""
        if not issubclass(self.output_type, Frame):
            raise TypeError(
                f"transforms must map between frames. got output_type: {self.output_type.__name__}"
            )

        super(Transform, self).__init__()

    def join(self, other):
        """The generic transform simply acts like the identity edge."""
        return other.copy()

    def inverse(self):
        """Inverse."""
        return Transform()

    def invertible(self):
        """The generic transform is invertible."""
        return True


class Projection(Named, Edge[F1, F2]):
    """A Projection is an edge that goes to a different space.

    Projections are not invertible, by definition. However, they may be reversible. If this is the
    case, the frame is responsible for adding the projection's reverse to the graph.

    The base Projection is generic.

    Projections are named because they are uniquely identified paths between spaces and have no
    guarantee of maintaining spatial relationships with one another.

    """

    input_type_bound = Frame
    ouput_type = Frame

    def __init__(self, name: Optional[str] = None):
        """Create a Projection with the given name.

        Args:
            name (Optional[str], optional): Optional name for the projection. Defaults to None.
        """
        Edge.__init__(self)
        Named.__init__(self, name=name)

    def join(self, other):
        """Join this projection with another edge.

        Projections joined with references are references in a different space.

        Projections joined with transforms or projections are also projections.

        """
        if isinstance(other, Reference):
            return Reference()
        elif isinstance(other, (Transform, Projection)):
            return Projection()
        else:
            return NotImplemented

    @final
    def inverse(self):
        """Projections cannot be inverted."""
        return None

    @final
    def invertible(self):
        """Projections cannot be inverted."""
        return False

    def reverse(self, name: Optional[str] = None) -> Projection:
        """Get the reverse of the projection.

        This is used to add the projection that goes in the opposite direction. This is not the same
        as the inverse, since extra information would be needed to get the same object, but it is
        similar.

        For example, a camera projection takes points in 3D and projections them onto 2D image
        indices. The reverse would be a projection that takes a 2D point on the image and returns
        the line connecting that point and the focal point.

        Args:
            name: The name for the reversed Projection.

        Returns:
            The projection that maps from the output space of `self` to the input space.

        Raises:
            NotReversibleError: If the projection is not reversible.

        """
        raise NotReversibleError

    def reversible(self) -> bool:
        """Determine whether the projection is reversible.

        Sub-classes may wish to implement a version that doesn't require actually creating the
        reverse.

        Returns:
            bool: Whether this projection is reversible.

        """
        try:
            self.reverse()
            out = True
        except NotReversibleError:
            out = False

        return out


def get_graph(*bodies: B) -> nx.MultiGraph:
    """Show the reference graph, with the provided bodies shown.

    TODO items:
    * Invertible/reversible edges should have their inverse/reverse drawn in dashed lines.
    * Projections, Transforms, and References should all be different colors.
    * Projections, frames, and spaces should have their names on the graph.
    * Spaces should be represented as group:
        https://pyvis.readthedocs.io/en/latest/tutorial.html#node-properties.

    Args:
        bodies (B): The bodies that are to be included in the graph.

    Returns:
        The reference graph including all spaces, frames, projections, and transforms.
        References are only included if the associated body is provided.

    """
    g = nx.MultiGraph()

    # First, add all the nodes in all the spaces
    for space in _space_registry.values():
        for frame in space:
            g.add_node(
                frame.full_name(),
                name=frame.name,
                space=space.name,
                **frame.vis_properties(),
            )

    # add all the edges
    for space in _space_registry.values():
        for frame in space:
            # add the defining edge
            if not frame.is_source():
                g.add_edge(frame.defining_frame.full_name(), frame.full_name())

            for p, f in frame.incoming_projections.items():
                g.add_edge(f.full_name(), frame.full_name(), key=p.name, label=p.name)

    # add all the bodies provided
    for i, body in enumerate(bodies):
        bid = f"bodies[{i}]"
        g.add_node(bid, space=body.space.name, **body.vis_properties())
        g.add_edge(bid, body.defining_frame.full_name())

    return g


def show(*bodies: B, path: str = "fledge_graph.html") -> None:
    """Get the reference graph and show it in an interactive window."""
    g = get_graph(*bodies)
    nt = Network("500px", "500px", directed=True)
    nt.set_edge_smooth("dynamic")
    nt.from_nx(g)
    nt.show(path)
