# -*- coding: utf-8 -*-
#
# Copyright 2016 Ricequant, Inc
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
import os

RQDATAC_DEFAULT_ADDRESS = "rqdatad-pro.ricequant.com:16011"
PERMISSIONS_INFO_URL = "http://www.ricequant.com/api/rqlicense/get_permissions_readable_info"
EXTRA_INDEX_URL = "https://rquser:Ricequant8@pypi2.ricequant.com/simple/"
BASH_FILE = [".bash_profile", ".bashrc", ".bash_profile", ".zshrc"]
TAG_MAP = ["stock", "futures", "fund", "index", "option", "convertible", ]
DEFAULT_BUNDLE_PATH = os.path.join(os.path.expanduser('~'), ".rqalpha-plus")

VERSION_MAP = {}

version_map_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "version_map.json"))
if os.path.exists(version_map_path):
    with open(version_map_path, 'r', encoding="utf8") as f:
        VERSION_MAP = json.loads(f.read())
del version_map_path
