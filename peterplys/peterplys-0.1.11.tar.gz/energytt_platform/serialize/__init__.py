from .serializer import Serializer, Serializable
from .serpyco import SerpycoSimpleSerializer, SerpycoJsonSerializer


simple_serializer = SerpycoSimpleSerializer()

json_serializer = SerpycoJsonSerializer()
