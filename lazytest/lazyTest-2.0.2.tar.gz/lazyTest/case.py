# -*- coding = UTF-8 -*-
# Author   :buxiubuzhi
# time     :2020/2/13  14:44
# ---------------------------------------
import pytest


class TestCase:

    @pytest.fixture(scope="function")
    def setUp(self, getdriver): ...
