from dataclasses import dataclass, field
from logging import getLogger
from typing import Any, Dict, List, Optional, Union

from annotell.openlabel.models.data_types import Boolean, Num, Text, Vec
from annotell.openlabel.models.datatypelist import DataTypeList
from annotell.openlabel.models.openlabel_base import OpenLabelBase

logger = getLogger(__name__)


@dataclass
class Attributes(OpenLabelBase):
    boolean: DataTypeList[Boolean] = field(default_factory=DataTypeList)
    num: DataTypeList[Num] = field(default_factory=DataTypeList)
    text: DataTypeList[Text] = field(default_factory=DataTypeList)
    vec: DataTypeList[Vec] = field(default_factory=DataTypeList)

    def has_attribute_with_name(self, attribute: str, name=""):
        return name in getattr(self, attribute, [])


@dataclass
class DataTypeWithAttributes:
    name: str = None
    val: Any = None
    attributes: Optional[Attributes] = field(default_factory=Attributes)
    stream: str = None


@dataclass
class Coordinate:
    x: float
    y: float


@dataclass
class Bbox(DataTypeWithAttributes):
    val: Union[List[int], List[float]] = field(default_factory=list)

    def __post_init__(self):
        assert len(self.val) == 4, f"val must have length 4, not {len(self.val)}"


@dataclass
class Rbbox(DataTypeWithAttributes):
    val: Union[List[int], List[float]] = field(default_factory=list)


@dataclass
class Binary(DataTypeWithAttributes):
    val: str = ""


@dataclass
class Cuboid(DataTypeWithAttributes):
    val: Union[List[int], List[float]] = field(default_factory=list)

    def __post_init__(self):
        assert len(self.val) == 10, f"val must have length 10, not {len(self.val)}"


@dataclass
class Image(DataTypeWithAttributes):
    val: str = ""


@dataclass
class Mat(DataTypeWithAttributes):
    val: Union[List[List[int]], List[List[float]]] = field(default_factory=list)

    def __add__(self, other):
        return Mat(name=self.name + other.name, val=[list(map(sum, zip(*t))) for t in zip(self.val, other.val)])


@dataclass
class Point2d(DataTypeWithAttributes):
    val: List[float] = field(default_factory=list)

    def __post_init__(self):
        assert len(self.val) == 2, f"val must have length 2, not {len(self.val)}"


@dataclass
class Point3d(DataTypeWithAttributes):
    val: List[float] = field(default_factory=list)

    def __post_init__(self):
        assert len(self.val) == 3, f"val must have length 3, not {len(self.val)}"


@dataclass
class Poly2d(DataTypeWithAttributes):
    val: List[Point2d] = field(default_factory=list)


@dataclass
class Poly3d(DataTypeWithAttributes):
    val: List[Point3d] = field(default_factory=list)


@dataclass
class AreaReference(DataTypeWithAttributes):
    val: str = ""


@dataclass
class LineReference(DataTypeWithAttributes):
    val: str = ""


@dataclass
class Mesh(DataTypeWithAttributes):
    val: Any = None  # TODO: should not be any (a 3D mesh of points, vertex and areas)


@dataclass
class ObjectData(OpenLabelBase):
    boolean: DataTypeList[Boolean] = field(default_factory=DataTypeList)
    num: DataTypeList[Num] = field(default_factory=DataTypeList)
    text: DataTypeList[Text] = field(default_factory=DataTypeList)
    vec: DataTypeList[Vec] = field(default_factory=DataTypeList)
    bbox: List[Bbox] = field(default_factory=list)
    rbbox: List[Rbbox] = field(default_factory=list)
    binary: List[Binary] = field(default_factory=list)
    cuboid: List[Cuboid] = field(default_factory=list)
    image: List[Image] = field(default_factory=list)
    mat: List[Mat] = field(default_factory=list)
    point2d: List[Point2d] = field(default_factory=list)
    point3d: List[Point3d] = field(default_factory=list)
    poly2d: List[Poly2d] = field(default_factory=list)
    poly3d: List[Poly3d] = field(default_factory=list)
    area_reference: List[AreaReference] = field(default_factory=list)
    line_reference: List[LineReference] = field(default_factory=list)
    mesh: List[Mesh] = field(default_factory=list)


@dataclass
class FrameInterval(OpenLabelBase):
    frame_start: int = None
    frame_end: int = None

    def merge_with(self, other):
        return FrameInterval(frame_start=min(self.frame_start, other.frame_start), frame_end=max(self.frame_end, other.frame_end))


@dataclass
class BaseElement(OpenLabelBase):
    name: str = None
    type: str = None


@dataclass
class Object(BaseElement):
    object_data: Optional[ObjectData] = None
    ontology_uid: Optional[str] = None
    frame_intervals: Optional[List[FrameInterval]] = field(default_factory=list)


@dataclass
class Action(BaseElement):
    frame_intervals: Optional[List[FrameInterval]] = field(default_factory=list)


@dataclass
class Event(BaseElement):
    frame_intervals: Optional[List[FrameInterval]] = field(default_factory=list)


@dataclass
class Context(BaseElement):
    pass


@dataclass
class RdfObject(OpenLabelBase):
    uid: str = ""
    type: str = ""


@dataclass
class RdfSubject(OpenLabelBase):
    uid: str = ""
    type: str = ""


@dataclass
class Relation(BaseElement):
    rdf_subjects: List[RdfSubject] = field(default_factory=list)
    rdf_objects: List[RdfObject] = field(default_factory=list)

    def object_in_odf_objects(self, object_id: str) -> bool:
        return any([object_id == rdf_object.uid for rdf_object in self.rdf_objects])


@dataclass
class CoordinateSystem(OpenLabelBase):
    coordinates: List[float] = field(default_factory=list)


@dataclass
class Elements(OpenLabelBase):
    actions: Optional[Dict[str, Action]] = field(default_factory=dict)
    contexts: Optional[Dict[str, Context]] = field(default_factory=dict)
    events: Optional[Dict[str, Event]] = field(default_factory=dict)
    objects: Optional[Dict[str, Object]] = field(default_factory=dict)
    relations: Optional[Dict[str, Relation]] = field(default_factory=dict)

    def get_relations_for_object(self, object_id: str) -> List[Relation]:
        return [relation for relation in self.relations.values() if relation.object_in_odf_objects(object_id)]


class Metadata(dict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


@dataclass
class Ontologies(dict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


@dataclass
class Sync(OpenLabelBase):
    frame_stream: str = None
    timestamp: str = None


@dataclass
class StreamProperties(Attributes):
    sync: Optional[Sync] = None


@dataclass
class Stream(OpenLabelBase):
    name: str = None
    type: str = None
    attributes: Optional[Attributes] = field(default_factory=Attributes)


@dataclass
class FrameProperties(Attributes):
    streams: Optional[Dict[str, Stream]] = field(default_factory=dict)


@dataclass
class Frame(Elements):
    frame_properties: Optional[FrameProperties] = field(default_factory=FrameProperties)


@dataclass
class OpenLabelAnnotation(OpenLabelBase):
    coordinate_systems: Optional[Dict[str, CoordinateSystem]] = field(default_factory=dict)
    elements: Optional[Elements] = field(default_factory=Elements)
    frames: Optional[Dict[str, Frame]] = field(default_factory=dict)
    metadata: Optional[Metadata] = field(default_factory=Metadata)
    ontologies: Optional[Ontologies] = field(default_factory=Ontologies)

    def to_dict(self):
        stripped_dict = super().to_dict()
        return {"openlabel": stripped_dict}
