from typing import List, Type, TypeVar
from bson.errors import InvalidId
from pydantic import BaseModel
from bson.objectid import ObjectId


T = TypeVar("T")


class MongoId(ObjectId):
    """Pymongo ObjectId Wrapper that adds validation functions for Pydantic"""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not cls.is_valid(str(v)):
            raise InvalidId("Invalid ObjectId")

        return cls(str(v))

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class MongoModel(BaseModel):
    """Extended Pydantic BaseModel to map Pymongo `_id` to an `id` field."""

    @classmethod
    def from_mongo(cls: Type[T], data: dict) -> T:
        """Create a Pydantic model instance from a Pymongo dict."""
        if not data:
            return data
        id = data.pop("_id", None)
        return cls(**dict(data, id=id))

    @classmethod
    def from_mongo_list(cls: Type[T], mongo_list: List[dict]) -> List[T]:
        """Create a list of Pydantic instances from a list of Pymongo dicts."""
        items = []

        for item in mongo_list:
            items.append(cls.from_mongo(item))

        return items

    def mongo(self, **kwargs):
        """Create a dict of the current instance mapping `id` to `_id`."""
        parsed = self.dict(**kwargs)
        parsed["_id"] = parsed.pop("id")
        return parsed

    class Config:
        json_encoders = {ObjectId: lambda id: str(id)}
