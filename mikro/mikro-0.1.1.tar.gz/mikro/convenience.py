try:
    from arkitekt.packers.models import GraphQLStructure
    GraphQLModel = GraphQLStructure
except ImportError as e:
    from herre.access.model import GraphQLModel
    GraphQLModel =  GraphQLModel