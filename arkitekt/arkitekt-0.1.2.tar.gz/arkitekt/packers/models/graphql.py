from arkitekt.packers.models.base import StructureModel
from arkitekt.models.graphql import GraphQLModel


class GraphQLStructure(GraphQLModel, StructureModel):
    __typename: str

    @classmethod
    async def expand(cls, identifier):
        return await cls.asyncs.get(id=identifier)

    async def shrink(self):
        assert self.id is not None, "In order to send a Model through a Port you need to query 'id' in your GQL Query"
        return self.id


    class Meta:
        abstract = True