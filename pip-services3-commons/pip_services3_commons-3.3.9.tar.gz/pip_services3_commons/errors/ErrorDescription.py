# -*- coding: utf-8 -*-
"""
    pip_services3_commons.errors.ErrorDescription
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Error description implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Any, Optional, Dict


class ErrorDescription:
    """
    Serializeable error description. It is use to pass information about errors
    between microservices implemented in different languages. On the receiving side
    :class:`ErrorDescription <pip_services3_commons.errors.ErrorDescription.ErrorDescription>` is used to recreate error object close to its original type
    without missing additional details.
    """

    def __init__(self):
        self.type: Optional[str] = None
        self.category: Optional[str] = None
        self.status: Optional[int] = None
        self.code: Optional[str] = None
        self.message: Optional[str] = None
        self.details: Any = None
        self.correlation_id: Optional[str] = None
        self.cause: Optional[str] = None
        self.stack_trace: Optional[str] = None

    def to_json(self) -> Dict[str, Any]:
        return {
            'type': self.type,
            'category': self.category,
            'status': self.status,
            'code': self.code,
            'message': self.message,
            'details': self.details,
            'correlation_id': self.correlation_id,
            'cause': self.cause,
            'stack_trace': self.stack_trace
        }

    @staticmethod
    def from_json(json: Dict[str, Any]) -> Any:
        if not isinstance(json, dict):
            return json

        error = ErrorDescription()
        error.type = json['type']
        error.category = json['category']
        error.status = json['status']
        error.code = json['code']
        error.message = json['message']
        error.details = json['details']
        error.correlation_id = json['correlation_id']
        error.cause = json['cause']
        error.stack_trace = json['stack_trace']
        return error
