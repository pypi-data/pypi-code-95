#!/usr/bin/env python3

import requests
from requests.models import Response
from typing import Any, Dict, Optional, Union

from ..exceptions import CFError, APIError


class Request:
    API_ROOT = "https://api.cloudflare.com/client/v4"

    def __init__(self, token: str, path: str = "") -> None:
        if not token:
            raise CFError("Invalid api token")
        path = self.__fix_path(path)
        self.base_url = f"{self.API_ROOT}{path}"
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def __del__(self) -> None:
        if "session" in self.__dict__ and self.session:
            self.session.close()
            self.session = None

    def get_result(self, response: Response) -> Union[Dict[str, Any], bool]:
        data = response.json()
        if data["result"] is None:
            return data["success"]
        return data["result"]

    def parse(self, response: Response) -> Union[Dict[str, Any], str, bool]:
        if not response.ok:
            data = response.json()
            keys = data.keys()
            if "errors" in keys and data["errors"]:
                raise APIError(data["errors"])
            if "error" in keys and data["error"]:
                raise APIError(data)
            raise CFError("Unkown error")
        if "json" not in response.headers["content-type"]:
            return response.text
        return self.get_result(response)

    def __fix_path(self, path: str) -> str:
        if path.startswith("https"):
            raise CFError("Invalid path")
        if not path.startswith("/"):
            path = "/" + path
        return path

    def url(self, path: Optional[str] = None) -> str:
        url = self.base_url
        if path is None or not path:
            return url
        return url + self.__fix_path(path)

    def get(
        self,
        url: Optional[str] = None,
        params: Optional[Any] = None,
        data: Optional[Any] = None,
        headers: Optional[Any] = None,
    ) -> Any:
        _res = self.session.get(
            self.url(url), params=params, data=data, headers=headers
        )
        return self.parse(_res)

    def post(
        self,
        url: Optional[str] = None,
        params: Optional[Any] = None,
        data: Optional[Any] = None,
        json: Optional[Any] = None,
        headers: Optional[Any] = None,
        files: Optional[Any] = None,
    ) -> Any:
        if json is not None:
            _res = self.session.post(
                self.url(url), params=params, json=json, headers=headers, files=files
            )
        else:
            if isinstance(data, (bytes, str)):
                _res = self.session.post(
                    self.url(url),
                    params=params,
                    data=data,
                    headers=headers,
                    files=files,
                )
            else:
                _res = self.session.post(
                    self.url(url),
                    params=params,
                    json=data,
                    headers=headers,
                    files=files,
                )
        return self.parse(_res)

    def put(
        self,
        url: Optional[str] = None,
        params: Optional[Any] = None,
        data: Optional[Any] = None,
        json: Optional[Any] = None,
        headers: Optional[Any] = None,
        files: Optional[Any] = None,
    ) -> Any:
        if json is not None:
            _res = self.session.put(
                self.url(url), params=params, json=json, headers=headers, files=files
            )
        else:
            if isinstance(data, (bytes, str)):
                _res = self.session.put(
                    self.url(url),
                    params=params,
                    data=data,
                    headers=headers,
                    files=files,
                )
            else:
                _res = self.session.put(
                    self.url(url),
                    params=params,
                    json=data,
                    headers=headers,
                    files=files,
                )
        return self.parse(_res)

    def delete(
        self,
        url: Optional[str] = None,
        params: Optional[Any] = None,
        data: Optional[Any] = None,
        json: Optional[Any] = None,
        headers: Optional[Any] = None,
    ) -> Any:
        if json is not None:
            _res = self.session.delete(
                self.url(url), params=params, json=json, headers=headers
            )
        else:
            if isinstance(data, (bytes, str)):
                _res = self.session.delete(
                    self.url(url), params=params, data=data, headers=headers
                )
            else:
                _res = self.session.delete(
                    self.url(url), params=params, json=data, headers=headers
                )
        return self.parse(_res)
