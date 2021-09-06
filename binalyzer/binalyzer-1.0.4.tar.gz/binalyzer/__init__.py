# -*- coding: utf-8 -*-
"""
    binalyzer
    ~~~~~~~~~

    A library supporting the analysis of binary data.

    :copyright: 2020 Denis Vasilík
    :license: MIT, see LICENSE for details.
"""

name = "binalyzer"

__tag__ = "v1.0.4"
__build__ = 206
__version__ = "{}".format(__tag__)
__commit__ = "7d46dde"


from binalyzer_core import (
    Binalyzer,
    BinalyzerExtension,
    Template,
    PropertyBase,
    ValueProperty,
    ReferenceProperty,
    AutoSizeValueProperty,
    StretchSizeProperty,
    RelativeOffsetValueProperty,
    RelativeOffsetReferenceProperty,
    BindingContext,
    BackedBindingContext,
    TemplateProviderBase,
    TemplateProvider,
    PlainTemplateProvider,
    DataProviderBase,
    DataProvider,
    BufferedIODataProvider,
    ZeroedDataProvider,
    siblings,
    rightsiblings,
    leftsiblings,
    ValueProviderBase,
    ValueProvider,
    RelativeOffsetValueProvider,
    RelativeOffsetReferenceValueProvider,
    AutoSizeValueProvider,
    StretchSizeValueProvider,
    value_cache,
)
from binalyzer_template_provider import XMLTemplateProviderExtension, XMLTemplateParser
from binalyzer_cli import TemplateAutoCompletion, ExpandedFile, BasedIntParamType
from binalyzer_wasm import WebAssemblyExtension

from .extension import UtilityExtension
from .cli import cli


def _register_extensions(binalyzer):
    XMLTemplateProviderExtension(binalyzer)
    WebAssemblyExtension(binalyzer)
    UtilityExtension(binalyzer)


Binalyzer._register_extensions = _register_extensions
