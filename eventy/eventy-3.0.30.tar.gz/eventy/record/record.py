# Copyright (c) Qotto, 2021

"""
Record abstract base class
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from semver import VersionInfo


from .record_errors import RecordAttributeTypeError, RecordAttributeValueError

__all__ = [
    'Record',
]

from eventy.trace_id import correlation_id_var
from eventy.trace_id.generator import gen_trace_id


class Record:
    """
    Common Record interface

    This class is a base for Event, Request, and Response. It should not be instantiated.
    """

    def __init__(
        self,
        protocol_version: str,
        schema: str,
        version: str,
        source: str,
        uuid: Optional[str] = None,
        correlation_id: Optional[str] = None,
        partition_key: Optional[str] = None,
        date: Optional[datetime] = None,
        context: Optional[Dict[str, Dict[str, Any]]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize Record attributes

        :param protocol_version: SemVer version of the Eventy protocol
        :param schema: URN of the record schema
        :param version: SemVer version of the record schema
        :param source: URN of the record emitter
        :param uuid: UUID v4 of the record. Default: auto-generated
        :param correlation_id: Trace / correlation ID for trace_id. Default: auto-generated
        :param partition_key: Partition or database key. Default: None
        :param date: Date of the event. Default: now
        :param context: Keys should be URN of a service using the context
        :param data: Domain data

        :raises RecordAttributeError:
        """
        self.protocol_version = protocol_version
        self.schema = schema
        self.version = version
        self.source = source
        if uuid is None:
            uuid = str(uuid4())
        self.uuid = uuid
        if correlation_id is None:
            correlation_id = correlation_id_var.get()
            if not correlation_id:
                correlation_id = gen_trace_id(schema)
        self.correlation_id = correlation_id
        # partition_key can be None
        self.partition_key = partition_key
        if date is None:
            date = datetime.now(tz=timezone.utc)
        self.date = date
        if context is None:
            context = {}
        self.context = context
        if data is None:
            data = {}
        self.data = data

    @property
    def type(self) -> str:
        """
        Type of the record: EVENT | REQUEST | RESPONSE
        """
        raise NotImplementedError

    @property
    def protocol_version(self) -> str:
        """
        Eventy protocol version (SemVer)
        """
        return self._protocol_version

    @protocol_version.setter
    def protocol_version(self, protocol_version: str) -> None:
        try:
            VersionInfo.parse(protocol_version)
        except ValueError:
            raise RecordAttributeValueError('protocol_version', protocol_version, 'Not in SemVer format')
        self._protocol_version = protocol_version

    @property
    def schema(self) -> str:
        """
        Record schema (URN)
        """
        return self._schema

    @schema.setter
    def schema(self, schema: str) -> None:
        self._schema = schema

    @property
    def version(self) -> str:
        """
        Record schema version (SemVer)
        """
        return self._version

    @version.setter
    def version(self, version: str) -> None:
        try:
            VersionInfo.parse(version)
        except ValueError:
            raise RecordAttributeValueError('version', version, 'Not in SemVer format')
        self._version = version

    @property
    def source(self) -> str:
        """
        Record source (URN)
        """
        return self._source

    @source.setter
    def source(self, source: str) -> None:
        self._source = source

    @property
    def uuid(self) -> str:
        """
        Record unique identifier (UUID v4)
        """
        return self._uuid

    @uuid.setter
    def uuid(self, uuid: str):
        if uuid is None:
            uuid = str(uuid4())
        try:
            UUID(uuid)
        except TypeError as e:
            raise RecordAttributeValueError('uuid', uuid, str(e)) from e
        except ValueError as e:
            raise RecordAttributeValueError('uuid', uuid, str(e)) from e
        self._uuid = uuid

    @property
    def correlation_id(self) -> str:
        """
        Record correlation_id to be propagated
        """
        return self._correlation_id

    @correlation_id.setter
    def correlation_id(self, correlation_id: str) -> None:
        if isinstance(correlation_id, str):
            self._correlation_id = correlation_id
        else:
            raise RecordAttributeTypeError('correlation_id', str, correlation_id)

    @property
    def partition_key(self) -> Optional[str]:
        """
        Key for partitioned states, e.g. Kafka topics partitions
        """
        return self._partition_key

    @partition_key.setter
    def partition_key(self, partition_key: Optional[str]):
        if partition_key is None or isinstance(partition_key, str):
            self._partition_key = partition_key
        else:
            raise RecordAttributeTypeError('partition_key', str, partition_key)

    @property
    def date(self) -> datetime:
        """
        Date of the event (unrelated to event production)
        """
        return self._date

    @date.setter
    def date(self, date: datetime) -> None:
        """
        Set the date, keeping a millisecond precision.

        :param date: record date, as a datetime, or iso str, or timestamp int
        """
        if isinstance(date, datetime):
            ts = int(date.timestamp() * 1000) / 1000
            date = datetime.fromtimestamp(ts, timezone.utc)
            self._date = date
        else:
            raise RecordAttributeTypeError('date', datetime, date)

    @property
    def context(self) -> Dict[str, Dict[str, Any]]:
        """
        Execution context to be propagated
        """
        return self._context

    @context.setter
    def context(self, context: Dict[str, Dict[str, Any]]) -> None:
        if not isinstance(context, Dict):
            raise RecordAttributeTypeError('context', Dict, context)
        for key, val in context.items():
            if not isinstance(key, str):
                raise RecordAttributeTypeError(f'context key', str, key)
            if not isinstance(val, Dict):
                raise RecordAttributeTypeError(f'value for key {key}', 'Dict', val)
        self._context = context

    @property
    def data(self) -> Dict[str, Any]:
        """
        Actual record payload
        """
        return self._data

    @data.setter
    def data(self, data) -> None:
        if not isinstance(data, Dict):
            raise RecordAttributeTypeError('data', Dict, data)
        for key in data:
            if not isinstance(key, str):
                raise RecordAttributeTypeError('data key', 'str', key)
        self._data = data

    def __repr__(self) -> str:
        return f"{self.type}:{self.schema} v{self.version} [CID:{self.correlation_id}] #{self.uuid} ${self.partition_key}"

    def _debug_str(self) -> str:
        return self.__repr__() + f"\n      CONTEXT={self.context}\n      DATA={self.data}"
