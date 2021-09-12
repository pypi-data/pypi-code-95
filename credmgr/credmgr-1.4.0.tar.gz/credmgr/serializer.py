import datetime
import re

import credmgr.models

from .exceptions import SerializerException


class Serializer(object):
    """The serializer builds :class:`.BaseModel` objects."""

    primitiveTypes = (float, bool, bytes, str, int)
    nativeTypeMapping = {
        "int": int,
        "str": str,
        "bool": bool,
        "datetime": datetime.datetime,
        "object": object,
        "dict": dict,
        "list": list,
    }

    def __init__(self, credmgr):
        """Initialize an Objector instance.

        :param credmgr: An instance of :class:`.CredentialManager`.

        """
        self._credmgr = credmgr

    @staticmethod
    def _snakeToCamel(snakeCase):
        return "".join(
            snakeCase.split("_")[:1]
            + [i.capitalize() for i in snakeCase.split("_")[1:]]
        )

    @staticmethod
    def deserializeDatatime(string):
        """Deserializes string to datetime.

        The string should be in iso8601 datetime format.

        :param string: str.

        :returns: datetime.

        """
        try:
            from dateutil.parser import parse

            return parse(string)
        except ImportError:  # pragma: no cover
            return string
        except ValueError:  # pragma: no cover
            raise SerializerException(f"Failed to parse `{string}` as datetime object")

    @staticmethod
    def deserializeDate(string):  # pragma: no cover
        """Deserializes string to date.

        :param string: str.

        :returns: date.

        """
        try:
            from dateutil.parser import parse

            return parse(string).date()
        except ImportError:
            return string
        except ValueError:
            raise SerializerException(f"Failed to parse `{string}` as date object")

    @staticmethod
    def deserializeObject(value):
        """Return a original value.

        :returns: object.

        """
        return value  # pragma: no cover

    @staticmethod
    def deserializePrimitive(data, objectType):
        """Deserializes string to primitive type.

        :param data: str.
        :param objectType: class literal.

        :returns: int, long, float, str, bool.

        """
        try:
            return objectType(data)
        except UnicodeEncodeError:  # pragma: no cover
            return str(data)
        except TypeError:  # pragma: no cover
            return data

    def deserialize(self, response):
        """Deserializes response into an object.

        :param response: Response object to be deserialized.

        :returns: deserialized object.

        """
        data = response.json()
        if isinstance(data, list) and all(
            [i["resource_type"] == data[0]["resource_type"] for i in data]
        ):
            if data:
                resourceType = f'list[{data[0]["resource_type"]}]'
            else:  # pragma: no cover
                return data
        else:
            resourceType = data.get("resource_type", "dict")
        return self.__deserialize(data, resourceType)

    def __deserialize(self, data, objectType):
        """Deserializes dict, list, str into an object.

        :param data: dict, list or str.
        :param objectType: class literal, or string of class name.

        :returns: object.

        """
        if data is None:
            return None

        if type(objectType) == str:
            if objectType.startswith("list["):
                subClass = re.match(r"list\[(.*)\]", objectType).group(1)
                return [self.__deserialize(subData, subClass) for subData in data]

            if objectType.startswith("dict"):
                return {k: self.__deserialize(v, type(v)) for k, v in data.items()}

            # convert str to class
            if objectType in self.nativeTypeMapping:
                objectType = self.nativeTypeMapping[objectType]
            else:
                objectType = getattr(credmgr.models, objectType)

        if objectType in self.primitiveTypes:
            return self.deserializePrimitive(data, objectType)
        elif objectType == object:  # pragma: no cover
            return self.deserializeObject(data)
        elif objectType == datetime.date:  # pragma: no cover
            return self.deserializeDate(data)
        elif objectType == datetime.datetime:
            return self.deserializeDatatime(data)
        elif objectType == dict:
            return self.__deserialize(data, "dict")
        else:
            return self.__deserializeModel(data, objectType)

    def __hasattr__(self, object, name):  # pragma: no cover
        return name in object.__class__.__dict__

    def __deserializeModel(self, data, objectType):
        """Deserializes list or dict to model.

        :param data: dict, list.
        :param objectType: class literal.

        :returns: model object.

        """

        if not objectType._attrTypes:  # pragma: no cover
            return data

        kwargs = {}
        if objectType._attrTypes is not None:
            for attr, attrType in objectType._attrTypes.items():
                if data and attr in data and isinstance(data, (list, dict)):
                    value = data[attr]
                    if attr in objectType._nameMapping:
                        kwargs[objectType._nameMapping[attr]] = self.__deserialize(
                            value, attrType
                        )
                    else:
                        kwargs[self._snakeToCamel(attr)] = self.__deserialize(
                            value, attrType
                        )

        try:
            instance = objectType(self._credmgr, **kwargs)
        except TypeError:  # pragma: no cover
            for key, value in kwargs.items():
                setattr(objectType, key, value)
            instance = objectType
        if (
            isinstance(instance, dict)
            and objectType._attrTypes is not None
            and isinstance(data, dict)
        ):  # pragma: no cover
            for key, value in data.items():
                if key not in objectType._attrTypes:
                    instance[key] = value
        return instance
