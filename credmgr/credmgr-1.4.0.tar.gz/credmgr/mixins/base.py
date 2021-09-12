from datetime import datetime

from ..exceptions import InitializationError
from ..models.utils import resolveUser


class BaseModel(object):
    """Superclass for all models in credmgr."""

    _attrTypes = {"id": "int"}
    _path = None
    _nameAttr = "name"
    _nameMapping = None
    _canFetchByName = False
    _credmgrCallable = None
    _getByNamePath = "by_name"
    _apiNameMapping = None

    def __init__(self, credmgr, **kwargs):
        """Initialize a BaseModel instance.

        :param credmgr: An instance of :class:`.CredentialManager`.

        """
        self._credmgr = credmgr
        if kwargs:
            for attribute, value in kwargs.items():
                setattr(self, attribute, value)
        self._fetched = False

    def __getattr__(self, attribute):  # pragma: no cover
        """Return the value of ``attribute``."""
        if not attribute.startswith("_") and not self._fetched:
            self._fetch()
            return getattr(self, attribute)
        raise AttributeError(
            f"{self.__class__.__name__!r} object has no attribute {attribute!r}"
        )

    def _get(self, id):
        self.__dict__ = self._credmgr.get(f"{self._path}/{id}").__dict__

    def _getByName(self):
        data = {}
        for modelAttr, dataAttr in self._apiNameMapping.items():
            name = getattr(self, modelAttr, None)
            if not name:  # pragma: no cover
                raise InitializationError(
                    f"Missing required keyword arg, {modelAttr!r}, to fetch object by name"
                )
            data[dataAttr] = name
        self.__dict__ = self._credmgr.post(
            f"{self._path}/{self._getByNamePath}", data=data
        ).__dict__

    def _fetch(self, byName=False):
        if byName and self._canFetchByName:
            self._getByName()
        else:
            self._get(self.id)
        self._fetched = True

    @resolveUser()
    def listItems(self, batchSize=20, limit=None, owner=None):
        from credmgr.models.helpers import Paginator

        return Paginator(
            self._credmgr,
            self.__class__,
            batchSize=batchSize,
            limit=limit,
            itemsOwner=owner,
        )

    def toDict(self):
        result = {}

        for exportAttr in self._attrTypes.keys():
            if exportAttr in self._nameMapping:
                attr = self._nameMapping.get(exportAttr)
            else:
                attr = "".join(
                    exportAttr.split("_")[:1]
                    + [i.capitalize() for i in exportAttr.split("_")[1:]]
                )
            value = getattr(self, attr, None)
            if value:
                if isinstance(value, list):
                    result[exportAttr] = list(
                        map(lambda x: x.toDict() if hasattr(x, "toDict") else x, value)
                    )
                elif hasattr(value, "toDict"):
                    result[exportAttr] = value.toDict()
                elif isinstance(value, dict):
                    result[exportAttr] = dict(
                        map(
                            lambda item: (item[0], item[1].toDict())
                            if hasattr(item[1], "toDict")
                            else item,
                            value.items(),
                        )
                    )
                elif isinstance(value, datetime):
                    result[exportAttr] = value.astimezone().strftime(
                        self._credmgr.config.dateFormat
                    )
                else:
                    result[exportAttr] = value
        if issubclass(type(self), dict):  # pragma: no cover
            for key, value in self.items():
                result[key] = value
        return result

    def __repr__(self):  # pragma: no cover
        return f"<{self.__class__.__name__} id={self.id}, {self._nameAttr}={getattr(self, self._nameAttr)!r}>"

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, type(self)):
            return False

        return self.id == other.id and getattr(self, self._nameAttr) == getattr(
            other, other._nameAttr
        )
