#     Copyright 2021. FastyBird s.r.o.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

# Test dependencies
import uuid

# Library libs
from triggers_module.items import PropertyActionItem, ChannelPropertyActionItem
from triggers_module.reposetories import actions_repository

# Tests libs
from tests.pytests.tests import DbTestCase


class TestActionItem(DbTestCase):
    def test_transform_to_dict(self) -> None:
        actions_repository.initialize()

        action_item = actions_repository.get_by_id(
            uuid.UUID("4aa84028-d8b7-4128-95b2-295763634aa4", version=4)
        )

        self.assertIsInstance(action_item, PropertyActionItem)
        self.assertIsInstance(action_item, ChannelPropertyActionItem)

        self.assertEqual({
            "id": "4aa84028-d8b7-4128-95b2-295763634aa4",
            "type": "channel-property",
            "enabled": False,
            "trigger": "c64ba1c4-0eda-4cab-87a0-4d634f7b67f4",
            "device": "a830828c-6768-4274-b909-20ce0e222347",
            "channel": "4f692f94-5be6-4384-94a7-60c424a5f723",
            "property": "7bc1fc81-8ace-409d-b044-810140e2361a",
            "value": "on"
        }, action_item.to_dict())

    # -----------------------------------------------------------------------------

    def test_validate(self) -> None:
        actions_repository.initialize()

        action_item = actions_repository.get_by_id(
            uuid.UUID("4aa84028-d8b7-4128-95b2-295763634aa4", version=4)
        )

        self.assertIsInstance(action_item, PropertyActionItem)
        self.assertIsInstance(action_item, ChannelPropertyActionItem)

        self.assertTrue(action_item.validate("on"))

        self.assertFalse(action_item.validate("off"))
