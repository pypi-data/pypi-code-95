#    Copyright 2021 Qruise project
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import sys
from typing import Optional, Union

from ._endpoint import Endpoint
from ._observer import OptimizationObserver


def _ipython_info():
    ip = None
    if 'ipykernel' in sys.modules:
        ip = 'notebook'
    elif 'IPython' in sys.modules:
        ip = 'terminal'
    return ip


def _openBrowser(url: str):
    if _ipython_info():
        from IPython.display import Javascript, display
        display(Javascript('window.open("{url}");'.format(url=url)))


class BrowserPresenter(OptimizationObserver):
    def __init__(
        self,
        webfrontend_url: str,
    ) -> None:
        self._webfrontend_url = webfrontend_url

    def on_start(self, run_id: str, *args, **kwargs):
        """Opens browser window showing current run's details, if running a notebook in a browser

        Parameters
        ----------
        run_id : [type]
            [description]
        """
        from urllib.parse import urljoin
        path = self._openBrowser(f"run/{run_id}")
        _openBrowser(urljoin(self._webfrontend_url, path))

    @staticmethod
    def from_endpoint(endpoint: Endpoint) -> Optional[OptimizationObserver]:
        """Creates Browser Presenter for a given endpoint for development and deployed environment
        expect host to be something grpc.* or localhost

        Parameters
        ----------
        endpoint : Endpoint
            remote services endpoint to start with

        Returns
        -------
        Optional[OptimizationObserver]
            instance or None
        """
        host = endpoint.host
        if host.startswith("grpc"):
            www_host = host.replace("grpc", "www")
            return BrowserPresenter(webfrontend_url=f"https://{www_host}:{endpoint.port}")
        elif host == "localhost" and endpoint.port == 9111:
            # development environment
            return BrowserPresenter(webfrontend_url="http://localhost:3000")
        else:
            return None
