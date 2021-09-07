# -*- coding: utf-8 -*-
"""
    pip_services3_commons.data.__init__
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Abstract, portable data types. For example – anytype, anyvalues, anyarrays, anymaps, stringmaps
    (on which many serializable objects are based on – configmap,
    filtermaps, connectionparams – all extend stringvaluemap). 
    Includes standard design patterns for working with data
    (data paging, filtering, GUIDs).
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

__all__ = [
    'IIdentifiable', 'IStringIdentifiable', 'IChangeable',
    'INamed', 'ITrackable', 'IVersioned', 'MultiString',
    'DataPage', 'FilterParams', 'SortField', 'SortParams',
    'PagingParams', 'IdGenerator', 'AnyValue',
    'AnyValueArray', 'AnyValueMap', 'StringValueMap', 'ProjectionParams'
]

from .IIdentifiable import IIdentifiable
from .IStringIdentifiable import IStringIdentifiable
from .IChangeable import IChangeable
from .INamed import INamed
from .ITrackable import ITrackable
from .IVersioned import IVersioned
from .MultiString import MultiString
from .DataPage import DataPage
from .FilterParams import FilterParams
from .SortField import SortField
from .SortParams import SortParams
from .PagingParams import PagingParams
from .IdGenerator import IdGenerator
from .AnyValue import AnyValue
from .AnyValueArray import AnyValueArray
from .AnyValueMap import AnyValueMap
from .StringValueMap import StringValueMap
from .ProjectionParams import ProjectionParams
