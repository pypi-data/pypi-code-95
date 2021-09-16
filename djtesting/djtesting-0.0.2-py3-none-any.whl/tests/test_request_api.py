# -*- coding: utf-8 -*-
# @Time    : 2021/9/8 15:54
# @Author  : chinablue
# @Email   : dongjun@reconova.cn
# @File    : test_request_api.py

import pytest

from djtesting.request.api import call_api, get, post, put, delete


class TestRequestApi():

    def test_call_api_get(self):
        url = "https://httpbin.org/get"
        res = call_api(method="get", url=url)

        assert res.status_code == 200
        assert res.json().get("url") == url

    def test_call_api_get_with_querydata(self):
        url = "https://httpbin.org/get"
        res = call_api(method="get", url=url, query_data={"a": 1, "b": 2})

        assert res.status_code == 200
        assert res.json().get("url") == "https://httpbin.org/get?a=1&b=2"

    def test_call_api_get_with_contenttype_urlencode(self):
        url = "https://httpbin.org/get"
        res = call_api(method="get", url=url, type="urlencode", data={"name": "chinablue"})

        assert res.status_code == 200
        assert "application/x-www-form-urlencoded" in str(res.json().get("headers"))

    def test_call_api_get_with_contenttype_json(self):
        url = "https://httpbin.org/get"
        res = call_api(method="get", url=url, type="json", data={"name": "chinablue"})

        assert res.status_code == 200
        assert "application/json" in str(res.json().get("headers"))

    def test_call_api_post(self):
        url = "https://httpbin.org/post"
        res = call_api(method="post", url=url)

        assert res.status_code == 200
        assert res.json().get("url") == url

    def test_call_api_post_with_contenttype_urlencode(self):
        url = "https://httpbin.org/post"
        res = call_api(method="post", url=url, type="urlencode", data={"name": "chinablue"})

        assert res.status_code == 200
        assert "application/x-www-form-urlencoded" in str(res.json().get("headers"))
        assert "chinablue" == res.json().get("form").get("name")

    def test_call_api_post_with_contenttype_json(self):
        url = "https://httpbin.org/post"
        res = call_api(method="post", url=url, type="json", data={"name": "chinablue"})

        assert res.status_code == 200
        assert "application/json" in str(res.json().get("headers"))
        assert "chinablue" in res.json().get("data")

    def test_call_api_put_with_contenttype_json(self):
        url = "https://httpbin.org/put"
        res = call_api(method="put", url=url, type="json", data={"name": "chinablue"})

        assert res.status_code == 200
        assert "application/json" in str(res.json().get("headers"))
        assert "chinablue" in res.json().get("data")

    def test_call_api_delete_with_contenttype_json(self):
        url = "https://httpbin.org/delete"
        res = call_api(method="delete", url=url, type="json", data={"name": "chinablue"})

        assert res.status_code == 200
        assert "application/json" in str(res.json().get("headers"))
        assert "chinablue" in res.json().get("data")

    # 添加自定义header
    def test_call_api_post_custom_headers(self):
        url = "https://httpbin.org/post"
        res = call_api(method="post", url=url, headers={"myheader": "djtest"})

        assert res.status_code == 200
        assert "djtest" in str(res.json().get("headers"))

    # url中存在动态参数
    def test_call_api_delete_with_dynamic_param_in_url(self):
        url = "https://httpbin.org/anything/{userId}/{groupId}"
        res = call_api(method="delete", type="json", url=url, data={"userId": 1, "groupId": 20})

        assert res.status_code == 200
        assert res.json().get("url") == "https://httpbin.org/anything/1/20"

    def test_get(self):
        url = "https://httpbin.org/get"
        query_data = {"a": 1, "b": 2}

        res = get(url, query_data)

        assert res.status_code == 200
        assert res.json().get("url") == "https://httpbin.org/get?a=1&b=2"

    def test_post(self):
        url = "https://httpbin.org/post"
        data = {"name": "chinablue"}

        res = post(url=url, data=data)

        assert res.status_code == 200
        assert "application/x-www-form-urlencoded" in str(res.json().get("headers"))
        assert "chinablue" == res.json().get("form").get("name")

    def test_put(self):
        url = "https://httpbin.org/put"
        data = {"name": "chinablue"}

        res = put(url=url, data=data)

        assert res.status_code == 200
        assert "application/json" in str(res.json().get("headers"))
        assert "chinablue" in res.json().get("data")

    def test_delete(self):
        url = "https://httpbin.org/delete"
        data = {"name": "chinablue"}

        res = delete(url=url, data=data)

        assert res.status_code == 200
        assert "application/json" in str(res.json().get("headers"))
        assert "chinablue" in res.json().get("data")

    # 修改接口的端口
    def test_get_modified_port(self):
        url = "http://httpbin.org:9000/get"
        res = get(url, port="80")

        assert res.status_code == 200

    # 设置接口的超时时间(默认超时时间10s)
    def test_get_set_timeout(self):
        import requests
        with pytest.raises(AssertionError):
            url = "http://httpbin.org/get"
            get(url, timeout=0.1)

    # 过滤出请求参数中value为None的key
    def test_post_data_autoremove_key_of_the_value_is_none(self):
        url = "https://httpbin.org/post"
        data = {"name": "chinablue", "age": None}
        res = post(url, data=data, type="json")

        assert res.status_code == 200
        assert '"age": null' not in str(res.text)

    # 请求参数中value为空字符串的key不会被过滤
    def test_post_data_reserved_key_of_the_value_is_none(self):
        url = "https://httpbin.org/post"
        data = {"name": "chinablue", "age": ""}
        res = post(url, data=data, type="json")

        assert res.status_code == 200
        assert '"age": ""' in str(res.text)

    @pytest.mark.skip(f"目前没有对请求方法进行验证")
    def test_call_api_invalid_reqmethod(self):
        with pytest.raises(Exception):
            url = "https://httpbin.org/get"
            call_api(method="gget", url=url)

    def test_call_api_invalid_reqtype(self):
        with pytest.raises(Exception):
            url = "https://httpbin.org/get"
            call_api(method="get", url=url, type="json123")


if __name__ == '__main__':
    pytest.main(["./test_request_api.py::TestRequestApi::test_call_api_invalid_reqmethod", "-s"])
