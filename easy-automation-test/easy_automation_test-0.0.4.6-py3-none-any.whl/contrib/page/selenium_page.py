#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/8/16
from .page import Page
from ..selenium_mixin import SeleniumMixin
from ..easy_assert_mixin import EasyAssertMixin


class SeleniumPage(Page, SeleniumMixin, EasyAssertMixin):
    """
    Web project create project page should extend this
    abstract page class.
    """
    pass


