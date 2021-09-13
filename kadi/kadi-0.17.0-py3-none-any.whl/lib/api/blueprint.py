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
from flask import Blueprint

from kadi.config import BaseConfig


class APIBlueprint(Blueprint):
    """Custom Flask blueprint with support for API versioning."""

    def route(self, rule, **options):
        r"""Decorator to register a view function for a given URL rule.

        Adds a new option ``v`` to Flask's ``route`` decorator, allowing to set an API
        endpoint to one or multiple specific API versions.

        **Example:**

        .. code-block:: python3

            @route("/records", v=["1.0", "2.0"])
            def get_records():
                pass

        The specified API version has to be valid, i.e. it has to be listed in the
        ``API_VERSIONS`` value in the application's configuration. If no versions are
        given, the endpoint defaults to all versions given in ``API_VERSIONS``, i.e. if
        an endpoint did not change between versions it does not have to be modified or
        duplicated. In any case, the normal endpoint without any version will be created
        as well, pointing to the same function as the endpoint with the latest version.

        For example, the above code would lead to the following endpoints and URLs
        (assuming an URL prefix of ``"/api"``), where the last two endpoints would point
        to the same function:

        * api.get_records_v1_0 -> /api/v1.0/records
        * api.get_records_v2_0 -> /api/v2.0/records
        * api.get_records -> /api/records

        Alternatively, the version can be set to ``None`` explicitely, in which case
        this decorator will behave like the standard ``route`` decorator, i.e. no
        versioning will be used at all. This is especially useful for internal endpoints
        where versioning is unnecessary.

        The version is also used when generating the API documentation.

        :param rule: The URL rule as string.
        :param endpoint: (optional) The endpoint for the registered URL rule. Defaults
            to the name of the function with the version appended, if present.
        :param v: (optional) A list of strings specifying the API versions.
        :param \**options: Additional options to be forwarded to the underlying rule
            system of Flask.
        """

        def decorator(func):
            # Since we are working outside of an application context here, this is the
            # only way to access the application's configuration.
            api_versions = BaseConfig.API_VERSIONS

            endpoint = options.pop("endpoint", func.__name__)
            versions = options.pop("v", api_versions)

            if versions is None:
                apidoc_meta = None
                self.add_url_rule(rule, endpoint, func, **options)
            else:
                apidoc_meta = []

                for version in versions:
                    if version not in api_versions:
                        continue

                    apidoc_meta.append(version)

                    self.add_url_rule(
                        f"v{version}{rule}",
                        f"{endpoint}_v{version.replace('.', '_')}",
                        func,
                        **options,
                    )

                    if version == api_versions[-1]:
                        self.add_url_rule(rule, endpoint, func, **options)

            if hasattr(func, "_apidoc"):
                func._apidoc["versions"] = apidoc_meta
            else:
                func._apidoc = {"versions": apidoc_meta}

            return func

        return decorator


bp = APIBlueprint("api", __name__)


# pylint: disable=unused-import


import kadi.modules.accounts.api
import kadi.modules.collections.api
import kadi.modules.groups.api
import kadi.modules.main.api
import kadi.modules.notifications.api
import kadi.modules.records.api
import kadi.modules.settings.api
import kadi.modules.templates.api
