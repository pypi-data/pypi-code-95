# -*- coding: utf-8 -*-
"""
    pip_services3_commons.validate.FilterParamsSchema
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    FilterParams schema implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from .MapSchema import MapSchema
from ..convert.TypeCode import TypeCode


class FilterParamsSchema(MapSchema):
    """
    Schema to validate :class:`FilterParams <pip_services3_commons.data.FilterParams.FilterParams>`.
    """

    def __init__(self):
        """
        Creates a new instance of validation schema.
        """
        super(FilterParamsSchema, self).__init__(TypeCode.String, None)
