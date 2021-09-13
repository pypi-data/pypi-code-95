# Copyright 2021 Akita Software, Inc.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#    http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import copy
from datetime import datetime, timedelta, timezone
import time
import uuid

import akita_har.models as M
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.test import Client as DjangoClient

from . import __version__
from . import har

class Client(DjangoClient):
    """
    A wrapper around django.test.Client, which logs requests and responses to
    a HAR file.
    """

    def __init__(self, *args, har_file_path=None, **kwargs):
        super().__init__(*args, **kwargs)
        creator = M.Creator(
            name="Akita DjangoClient",
            version=__version__,
            comment="https://docs.akita.software/docs/integrate-with-django",
        )
        browser = M.Browser(
            name="",
            version="",
        )
        comment = "Created by the Akita DjangoClient."

        # Append 5 digits of a UUID to avoid clobbering the default file if
        # many HAR clients are created in rapid succession.
        tail = str(uuid.uuid4().int)[-5:]
        now = datetime.now().strftime('%y%m%d_%H%M')
        path = har_file_path if har_file_path is not None else f'akita_trace_{now}_{tail}.har'

        self.har_writer = HarWriter(path, 'w', creator=creator, browser=browser, comment=comment)

    def request(self, **request):
        start = datetime.now(timezone.utc)
        wsgi_request = WSGIRequest(self._base_environ(**request))
        response = super().request(**copy.deepcopy(request))
        self.har_writer.write_entry(har.django_to_har_entry(start, wsgi_request, response))

        return response

    def close(self):
        self.har_writer.close()

