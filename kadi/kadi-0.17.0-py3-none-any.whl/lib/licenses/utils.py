# Copyright 2020 Karlsruhe Institute of Technology
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import requests
from flask import current_app

from .models import License
from kadi.lib.db import update_object


def update_licenses(licenses_url=None, catch_errors=True):
    """Update the licenses stored in the database.

    The expected license format is a dictionary, mapping the ID of each license to some
    additional information about the license, namely its title and (possibly empty) URL.

    :param licenses_url: (optional) The URL to get the licenses from. Defaults to
        ``LICENSES_URL`` as specified in the application's configuration.
    :param catch_errors: (optional) Flag indicating whether to catch any errors while
        retrieving or updating the licenses.
    """
    if licenses_url is None:
        licenses_url = current_app.config["LICENSES_URL"]

    try:
        licenses = requests.get(
            licenses_url, timeout=current_app.config["REQUESTS_TIMEOUT"]
        ).json()

        for name, license_dict in licenses.items():
            title = license_dict["title"]
            url = license_dict["url"] or None

            license = License.query.filter_by(name=name).first()

            if license is not None:
                update_object(license, title=title, url=url)
            else:
                license = License.create(name=name, title=title, url=url)

    except:
        if not catch_errors:
            raise
