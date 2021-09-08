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
from triggers_module.models import actions_repository

# Tests libs
from tests.pytests.tests import DbTestCase


class TestActionsRepository(DbTestCase):
    def test_repository_iterator(self) -> None:
        self.assertEqual(13, len(actions_repository))

    # -----------------------------------------------------------------------------

    def test_get_item(self) -> None:
        action_item = actions_repository.get_by_id(
            uuid.UUID("4aa84028-d8b7-4128-95b2-295763634aa4", version=4)
        )

        self.assertIsInstance(action_item, PropertyActionItem)
        self.assertIsInstance(action_item, ChannelPropertyActionItem)
        self.assertEqual("4aa84028-d8b7-4128-95b2-295763634aa4", action_item.action_id.__str__())

    # -----------------------------------------------------------------------------

    def test_get_item_by_property(self) -> None:
        action_item = actions_repository.get_by_property_identifier(
            uuid.UUID("7bc1fc81-8ace-409d-b044-810140e2361a", version=4)
        )

        self.assertIsInstance(action_item, PropertyActionItem)
        self.assertIsInstance(action_item, ChannelPropertyActionItem)
        self.assertEqual("4aa84028-d8b7-4128-95b2-295763634aa4", action_item.action_id.__str__())
