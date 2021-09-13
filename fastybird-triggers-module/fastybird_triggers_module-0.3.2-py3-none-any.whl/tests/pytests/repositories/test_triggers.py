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
from modules_metadata.triggers_module import TriggerType

# Library libs
from triggers_module.items import TriggerItem
from triggers_module.reposetories import triggers_repository

# Tests libs
from tests.pytests.tests import DbTestCase


class TestTriggersRepository(DbTestCase):
    def test_repository_iterator(self) -> None:
        triggers_repository.initialize()

        self.assertEqual(6, len(triggers_repository))

    # -----------------------------------------------------------------------------

    def test_get_item(self) -> None:
        triggers_repository.initialize()

        trigger_item = triggers_repository.get_by_id(
            uuid.UUID("c64ba1c4-0eda-4cab-87a0-4d634f7b67f4", version=4)
        )

        self.assertIsInstance(trigger_item, TriggerItem)
        self.assertEqual("c64ba1c4-0eda-4cab-87a0-4d634f7b67f4", trigger_item.trigger_id.__str__())

    # -----------------------------------------------------------------------------

    def test_create_from_exchange(self) -> None:
        triggers_repository.initialize()

        result: bool = triggers_repository.create_from_exchange(
            RoutingKey(RoutingKey.TRIGGERS_ENTITY_CREATED),
            {
                "id": "c64ba1c4-0eda-4cab-87a0-4d634f7b67f4",
                "type": TriggerType(TriggerType.AUTOMATIC).value,
                "enabled": True,
                "name": "Good Night's Sleep",
                "comment": None,
            },
        )

        self.assertTrue(result)

        trigger_item = triggers_repository.get_by_id(
            uuid.UUID("c64ba1c4-0eda-4cab-87a0-4d634f7b67f4", version=4)
        )

        self.assertIsInstance(trigger_item, TriggerItem)
        self.assertEqual("c64ba1c4-0eda-4cab-87a0-4d634f7b67f4", trigger_item.trigger_id.__str__())

    # -----------------------------------------------------------------------------

    def test_update_from_exchange(self) -> None:
        triggers_repository.initialize()

        trigger_item = triggers_repository.get_by_id(
            uuid.UUID("c64ba1c4-0eda-4cab-87a0-4d634f7b67f4", version=4)
        )

        self.assertIsInstance(trigger_item, TriggerItem)
        self.assertEqual("c64ba1c4-0eda-4cab-87a0-4d634f7b67f4", trigger_item.trigger_id.__str__())
        self.assertTrue(trigger_item.enabled)

        result: bool = triggers_repository.update_from_exchange(
            RoutingKey(RoutingKey.TRIGGERS_ENTITY_UPDATED),
            {
                "id": "c64ba1c4-0eda-4cab-87a0-4d634f7b67f4",
                "type": TriggerType(TriggerType.AUTOMATIC).value,
                "enabled": False,
                "name": "Good Night's Sleep",
                "comment": None,
            },
        )

        self.assertTrue(result)

        trigger_item = triggers_repository.get_by_id(
            uuid.UUID("c64ba1c4-0eda-4cab-87a0-4d634f7b67f4", version=4)
        )

        self.assertIsInstance(trigger_item, TriggerItem)
        self.assertEqual("c64ba1c4-0eda-4cab-87a0-4d634f7b67f4", trigger_item.trigger_id.__str__())
        self.assertFalse(trigger_item.enabled)

    # -----------------------------------------------------------------------------

    def test_delete_from_exchange(self) -> None:
        triggers_repository.initialize()

        trigger_item = triggers_repository.get_by_id(
            uuid.UUID("c64ba1c4-0eda-4cab-87a0-4d634f7b67f4", version=4)
        )

        self.assertIsInstance(trigger_item, TriggerItem)
        self.assertEqual("c64ba1c4-0eda-4cab-87a0-4d634f7b67f4", trigger_item.trigger_id.__str__())

        result: bool = triggers_repository.delete_from_exchange(
            RoutingKey(RoutingKey.TRIGGERS_ENTITY_DELETED),
            {
                "id": "c64ba1c4-0eda-4cab-87a0-4d634f7b67f4",
                "type": TriggerType(TriggerType.AUTOMATIC).value,
                "enabled": True,
                "name": "Good Night's Sleep",
                "comment": None,
            },
        )

        self.assertTrue(result)

        trigger_item = triggers_repository.get_by_id(
            uuid.UUID("c64ba1c4-0eda-4cab-87a0-4d634f7b67f4", version=4)
        )

        self.assertIsNone(trigger_item)
