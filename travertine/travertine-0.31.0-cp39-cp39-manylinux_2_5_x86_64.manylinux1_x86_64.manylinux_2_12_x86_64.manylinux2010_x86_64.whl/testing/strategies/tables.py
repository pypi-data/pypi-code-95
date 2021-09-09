#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from datetime import datetime
from typing import List, Optional

from hypothesis import strategies as st
from travertine.tables import (
    ATTR_FORMAT,
    NULL_FORMAT,
    AttrFormatConfiguration,
    TableFormat,
)
from travertine.types import ATTRIBUTE_OWNER, AttributeLocator, TypedAttribute

from .base import nonnumerical_attributes, numerical_attributes

random_demand_attributes = st.sampled_from(["demand_attr_%d" % i for i in range(25)])
random_request_attributes = st.sampled_from(["request_attr_%d" % i for i in range(25)])
random_commodity_attributes = st.sampled_from(
    ["commodity_attr_%d" % i for i in range(25)]
)

attribute_locators = (
    st.builds(
        AttributeLocator,
        st.just(ATTRIBUTE_OWNER.COMMODITY),
        st.builds(TypedAttribute, nonnumerical_attributes, st.just(str)),
    )
    | st.builds(
        AttributeLocator,
        st.just(ATTRIBUTE_OWNER.COMMODITY),
        st.builds(TypedAttribute, numerical_attributes, st.just(int)),
    )
    | st.just(AttributeLocator.of_demand("date", datetime))
    | st.just(AttributeLocator.of_request("quantity", float))
    | st.builds(
        AttributeLocator,
        st.just(ATTRIBUTE_OWNER.DEMAND),
        st.builds(TypedAttribute, random_demand_attributes, st.just(int)),
    )
    | st.builds(
        AttributeLocator,
        st.just(ATTRIBUTE_OWNER.REQUEST),
        st.builds(TypedAttribute, random_request_attributes, st.just(int)),
    )
    | st.builds(
        AttributeLocator,
        st.just(ATTRIBUTE_OWNER.COMMODITY),
        st.builds(TypedAttribute, random_commodity_attributes, st.just(int)),
    )
)
st.register_type_strategy(AttributeLocator, attribute_locators)


def _clean_up_format_configuration(
    fconf: AttrFormatConfiguration, also_ignore=None
) -> AttrFormatConfiguration:
    """Remove repeated attribute locators from the format configuration."""
    attrs: List[AttributeLocator] = []
    for attr in fconf.attrs:
        if attr not in attrs and (not also_ignore or attr not in also_ignore):
            attrs.append(attr)
    return AttrFormatConfiguration(tuple(attrs), fconf.how, fconf.visible)


format_confs = st.builds(
    AttrFormatConfiguration,
    attrs=st.sets(st.from_type(AttributeLocator), min_size=1, max_size=3).map(tuple),
    how=st.from_type(ATTR_FORMAT),
    visible=st.booleans(),
).map(_clean_up_format_configuration)


def _clean_up_table_format(tconf: TableFormat) -> TableFormat:
    """Remove repeated attribute locators from the table format and ensure a single BY_VALUE
    configuration."""
    tables_conf = AttrFormatConfiguration(
        tconf.tables_conf.attrs,
        ATTR_FORMAT.BY_VALUE,
        True,
    )
    seen_attrs = list(tconf.tables_conf.attrs)
    column_confs = []
    by_value: Optional[AttrFormatConfiguration] = None
    for cconf in tconf.columns_conf:
        cconf = _clean_up_format_configuration(cconf, also_ignore=seen_attrs)
        seen_attrs.extend(cconf.attrs)
        if cconf.how == ATTR_FORMAT.BY_VALUE:
            if by_value is None:
                by_value = cconf
            else:
                by_value.attrs = tuple(by_value.attrs) + tuple(cconf.attrs)
                cconf.attrs = ()
        if cconf.attrs:
            column_confs.append(cconf)
    return TableFormat(tables_conf, tuple(column_confs))


table_formats = st.builds(TableFormat, format_confs, st.lists(format_confs)).map(
    _clean_up_table_format
) | st.just(NULL_FORMAT)
