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
from modules_metadata.routing import RoutingKey
from modules_metadata.triggers_module import TriggerActionType

# Library libs
from triggers_module.items import PropertyActionItem, ChannelPropertyActionItem
from triggers_module.reposetories import actions_repository

# Tests libs
from tests.pytests.tests import DbTestCase


class TestActionsRepository(DbTestCase):
    def test_repository_iterator(self) -> None:
        actions_repository.initialize()

        self.assertEqual(13, len(actions_repository))

    # -----------------------------------------------------------------------------

    def test_get_item(self) -> None:
        actions_repository.initialize()

        action_item = actions_repository.get_by_id(
            uuid.UUID("4aa84028-d8b7-4128-95b2-295763634aa4", version=4)
        )

        self.assertIsInstance(action_item, PropertyActionItem)
        self.assertIsInstance(action_item, ChannelPropertyActionItem)
        self.assertEqual("4aa84028-d8b7-4128-95b2-295763634aa4", action_item.action_id.__str__())

    # -----------------------------------------------------------------------------

    def test_get_item_by_property(self) -> None:
        actions_repository.initialize()

        action_item = actions_repository.get_by_property_identifier(
            uuid.UUID("7bc1fc81-8ace-409d-b044-810140e2361a", version=4)
        )

        self.assertIsInstance(action_item, PropertyActionItem)
        self.assertIsInstance(action_item, ChannelPropertyActionItem)
        self.assertEqual("4aa84028-d8b7-4128-95b2-295763634aa4", action_item.action_id.__str__())

    # -----------------------------------------------------------------------------

    def test_create_from_exchange(self) -> None:
        actions_repository.initialize()

        result: bool = actions_repository.create_from_exchange(
            RoutingKey(RoutingKey.TRIGGERS_ACTIONS_ENTITY_CREATED),
            {
                "id": "4aa84028-d8b7-4128-95b2-295763634aa4",
                "type": TriggerActionType(TriggerActionType.CHANNEL_PROPERTY).value,
                "enabled": True,
                "device": "a830828c-6768-4274-b909-20ce0e222347",
                "channel": "4f692f94-5be6-4384-94a7-60c424a5f723",
                "property": "7bc1fc81-8ace-409d-b044-810140e2361a",
                "value": "on",
                "trigger": "c64ba1c4-0eda-4cab-87a0-4d634f7b67f4",
            },
        )

        self.assertTrue(result)

        action_item = actions_repository.get_by_id(
            uuid.UUID("4aa84028-d8b7-4128-95b2-295763634aa4", version=4)
        )

        self.assertIsInstance(action_item, PropertyActionItem)
        self.assertIsInstance(action_item, ChannelPropertyActionItem)
        self.assertEqual("4aa84028-d8b7-4128-95b2-295763634aa4", action_item.action_id.__str__())

    # -----------------------------------------------------------------------------

    def test_update_from_exchange(self) -> None:
        actions_repository.initialize()

        action_item = actions_repository.get_by_id(
            uuid.UUID("4aa84028-d8b7-4128-95b2-295763634aa4", version=4)
        )

        self.assertIsInstance(action_item, PropertyActionItem)
        self.assertIsInstance(action_item, ChannelPropertyActionItem)
        self.assertEqual("4aa84028-d8b7-4128-95b2-295763634aa4", action_item.action_id.__str__())
        self.assertFalse(action_item.enabled)

        result: bool = actions_repository.update_from_exchange(
            RoutingKey(RoutingKey.TRIGGERS_ACTIONS_ENTITY_UPDATED),
            {
                "id": "4aa84028-d8b7-4128-95b2-295763634aa4",
                "type": TriggerActionType(TriggerActionType.CHANNEL_PROPERTY).value,
                "enabled": True,
                "device": "a830828c-6768-4274-b909-20ce0e222347",
                "channel": "4f692f94-5be6-4384-94a7-60c424a5f723",
                "property": "7bc1fc81-8ace-409d-b044-810140e2361a",
                "value": "off",
                "trigger": "c64ba1c4-0eda-4cab-87a0-4d634f7b67f4",
            },
        )

        self.assertTrue(result)

        action_item = actions_repository.get_by_id(
            uuid.UUID("4aa84028-d8b7-4128-95b2-295763634aa4", version=4)
        )

        self.assertIsInstance(action_item, PropertyActionItem)
        self.assertIsInstance(action_item, ChannelPropertyActionItem)
        self.assertEqual("4aa84028-d8b7-4128-95b2-295763634aa4", action_item.action_id.__str__())
        self.assertTrue(action_item.enabled)
        self.assertEqual("off", action_item.value)

    # -----------------------------------------------------------------------------

    def test_delete_from_exchange(self) -> None:
        actions_repository.initialize()

        action_item = actions_repository.get_by_id(
            uuid.UUID("4aa84028-d8b7-4128-95b2-295763634aa4", version=4)
        )

        self.assertIsInstance(action_item, PropertyActionItem)
        self.assertIsInstance(action_item, ChannelPropertyActionItem)
        self.assertEqual("4aa84028-d8b7-4128-95b2-295763634aa4", action_item.action_id.__str__())

        result: bool = actions_repository.delete_from_exchange(
            RoutingKey(RoutingKey.TRIGGERS_ACTIONS_ENTITY_DELETED),
            {
                "id": "4aa84028-d8b7-4128-95b2-295763634aa4",
                "type": TriggerActionType(TriggerActionType.CHANNEL_PROPERTY).value,
                "enabled": False,
                "device": "a830828c-6768-4274-b909-20ce0e222347",
                "channel": "4f692f94-5be6-4384-94a7-60c424a5f723",
                "property": "7bc1fc81-8ace-409d-b044-810140e2361a",
                "value": "on",
                "trigger": "c64ba1c4-0eda-4cab-87a0-4d634f7b67f4",
            },
        )

        self.assertTrue(result)

        action_item = actions_repository.get_by_id(
            uuid.UUID("4aa84028-d8b7-4128-95b2-295763634aa4", version=4)
        )

        self.assertIsNone(action_item)
