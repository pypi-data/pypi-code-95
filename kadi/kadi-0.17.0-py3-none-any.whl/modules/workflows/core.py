# Copyright 2021 Karlsruhe Institute of Technology
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
import json

from defusedxml.ElementTree import parse

import kadi.lib.constants as const
from kadi.modules.records.files import open_file


def get_custom_mimetype(file, base_mimetype):
    """Get a custom MIME type of a workflow or tool file based on its content.

    :param file: The file to get the MIME type of.
    :param base_mimetype: The base MIME type of the file on which to base the custom
        MIME type.
    :return: The custom MIME type or ``None`` if no custom MIME type was found.
    """
    if file.size > 10 * const.ONE_MB:
        return None

    with open_file(file) as f:
        if f is None:
            return None

        if base_mimetype == "application/json":
            try:
                data = json.load(f)
            except:
                return None

            if (
                isinstance(data, dict)
                and len(data.keys()) <= 3
                and isinstance(data.get("nodes"), list)
                and isinstance(data.get("connections"), list)
            ):
                return "application/x-flow+json"

        if base_mimetype == "application/xml":
            try:
                tree = parse(f)
                root = tree.getroot()

                # Tools can currently either be normal "programs" or "environments",
                # which only differ in their root tag.
                if root.tag in ["program", "env"] and "name" in root.attrib:
                    for child in root:
                        if child.tag != "param" or any(
                            attr not in child.attrib for attr in ["name", "type"]
                        ):
                            return None

                return "application/x-tool+xml"
            except:
                return None

    return None


def parse_tool_file(file):
    """Parse a tool file.

    :param file: The file whose contents should be parsed.
    :return: The parsed tool file as dictionary or ``None`` if it could not be parsed.
    """
    if file.magic_mimetype != "application/x-tool+xml":
        return None

    with open_file(file) as f:
        if f is None:
            return None

        try:
            tree = parse(f)
            root = tree.getroot()

            tool = {
                "name": root.attrib["name"],
                "version": root.attrib.get("version"),
                "type": root.tag,
                "param": [],
            }

            for param in root:
                tool["param"].append(
                    {
                        "name": param.attrib["name"],
                        "type": param.attrib["type"],
                        "char": param.attrib.get("char"),
                        "required": param.attrib.get("required") == "true",
                    }
                )
        except:
            return None

        return tool
