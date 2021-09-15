from enum import Enum, auto
from arkitekt.models.graphql import GraphQLObject


class PostmanProtocol(str, Enum):
    WEBSOCKET = "WEBSOCKET"
    KAFKA = "KAFKA"
    RABBITMQ = "RABBITMQ"



class PostmanSettings(GraphQLObject):
    type: PostmanProtocol
    kwargs: dict

class Transcript(GraphQLObject):
    postman: PostmanSettings
