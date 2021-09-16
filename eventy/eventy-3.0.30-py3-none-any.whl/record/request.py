# Copyright (c) Qotto, 2021

"""
Request record
"""

from datetime import datetime
from typing import Dict, Any, Optional

from eventy.record import Record

__all__ = [
    'Request',
]


class Request(Record):

    def __init__(
        self,
        protocol_version: str,
        schema: str,
        version: str,
        source: str,
        destination: str,
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
        :param destination: URN of the request destination
        :param uuid: UUID v4 of the record. Default: auto-generated
        :param correlation_id: Trace / correlation ID for trace_id. Default: auto-generated
        :param partition_key: Partition or database key. Default: None
        :param date: Date of the event. Default: now
        :param context: Keys should be URN of a service using the context
        :param data: Domain data

        :raises RecordAttributeError:
        """
        super().__init__(
            protocol_version,
            schema,
            version,
            source,
            uuid,
            correlation_id,
            partition_key,
            date,
            context,
            data,
        )
        self.destination = destination

    @property
    def destination(self) -> str:
        return self._destination

    @destination.setter
    def destination(self, destination: str):
        self._destination = destination

    @property
    def type(self) -> str:
        return 'REQUEST'
