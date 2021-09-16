# -*- coding: utf-8 -*-
# @Time    : 2021/9/8 15:21
# @Author  : chinablue
# @Email   : dongjun@reconova.cn
# @File    : test_prepare_request.py

import pytest

from djtesting.request.models import PrepareRequest


class TestPrepareRequest():

    def setup_class(self):
        self.pre_request = PrepareRequest()

    @pytest.mark.parametrize(
        "url, req_data, query_data, expected", [
            (
                    "http://dj.reconova.com",
                    None,
                    None,
                    "http://dj.reconova.com"
            ),
            (
                    "http://dj.reconova.com/{id}",
                    {"id": 20},
                    None,
                    "http://dj.reconova.com/20"
            ),
            (
                    "http://dj.reconova.com",
                    None,
                    {"name": "chinablue", "age": 18},
                    "http://dj.reconova.com?name=chinablue&age=18"
            ),
            (
                    "http://dj.reconova.com?userid=1",
                    None,
                    {"name": "chinablue", "age": 18},
                    "http://dj.reconova.com?userid=1&name=chinablue&age=18"
            ),
        ]
    )
    def test_prepare_url(self, url, req_data, query_data, expected):
        self.pre_request.prepare_url(url=url, req_data=req_data, query_data=query_data)
        assert self.pre_request.url == expected

    @pytest.mark.parametrize(
        "url, req_data, exception", [
            (
                    "ws://dj.reconova.com",
                    None,
                    Exception,
            ),
            (
                    "http://dj.reconova.com/{id}",
                    {"userid": 1},
                    Exception,
            ),
            (
                    "http://dj.reconova.com/{id}",
                    None,
                    Exception,
            ),

        ]
    )
    def test_invalid_url(self, url, req_data, exception):
        with pytest.raises(exception):
            self.pre_request.prepare_url(url=url, req_data=req_data)


if __name__ == "__main__":
    pytest.main()
