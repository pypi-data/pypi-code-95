#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/9/6
from easy_automation.utils.exception import AssertFailed
import allure


class EasyAssertMixin:

    def assert_equal(self, first, second, msg=None):
        try:
            assert first == second
        except AssertionError:
            self._screenshot()
            error_desc = f'Assert failed: {first} == {second}'
            raise AssertFailed(msg, error_desc) from None

    def assert_not_equal(self, first, second, msg=None):
        try:
            assert first != second
        except AssertionError:
            self._screenshot()
            error_desc = f'Assert failed: {first} != {second}'
            raise AssertFailed(msg, error_desc) from None

    def assert_in(self, target, gather, msg=None):
        try:
            assert target in gather
        except AssertionError:
            self._screenshot()
            error_desc = f'Assert failed: {target} in {gather}'
            raise AssertFailed(msg, error_desc) from None

    def assert_not_in(self, target, gather, msg=None):
        try:
            assert target not in gather
        except AssertionError:
            self._screenshot()
            error_desc = f'Assert failed: {target} not in {gather}'
            raise AssertFailed(msg, error_desc) from None

    def _screenshot(self):
        allure.attach(self.screenshot(), attachment_type=allure.attachment_type.PNG)

