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
from modules_metadata.triggers_module import TriggerConditionType, TriggerConditionOperator

# Library libs
from triggers_module.items import PropertyConditionItem, ChannelPropertyConditionItem
from triggers_module.reposetories import conditions_repository

# Tests libs
from tests.pytests.tests import DbTestCase


class TestConditionsRepository(DbTestCase):
    def test_repository_iterator(self) -> None:
        conditions_repository.initialize()

        self.assertEqual(3, len(conditions_repository))

    # -----------------------------------------------------------------------------

    def test_get_item(self) -> None:
        conditions_repository.initialize()

        condition_item = conditions_repository.get_by_id(
            uuid.UUID("2726f19c-7759-440e-b6f5-8c3306692fa2", version=4)
        )

        self.assertIsInstance(condition_item, PropertyConditionItem)
        self.assertIsInstance(condition_item, ChannelPropertyConditionItem)
        self.assertEqual("2726f19c-7759-440e-b6f5-8c3306692fa2", condition_item.condition_id.__str__())

    # -----------------------------------------------------------------------------

    def test_get_item_by_property(self) -> None:
        conditions_repository.initialize()

        condition_item = conditions_repository.get_by_property_identifier(
            uuid.UUID("ff7b36d7-a0b0-4336-9efb-a608c93b0974", version=4)
        )

        self.assertIsInstance(condition_item, PropertyConditionItem)
        self.assertIsInstance(condition_item, ChannelPropertyConditionItem)
        self.assertEqual("2726f19c-7759-440e-b6f5-8c3306692fa2", condition_item.condition_id.__str__())

    # -----------------------------------------------------------------------------

    def test_create_from_exchange(self) -> None:
        conditions_repository.initialize()

        result: bool = conditions_repository.create_from_exchange(
            RoutingKey(RoutingKey.TRIGGERS_CONDITIONS_ENTITY_CREATED),
            {
                "id": "2726f19c-7759-440e-b6f5-8c3306692fa2",
                "type": TriggerConditionType(TriggerConditionType.CHANNEL_PROPERTY).value,
                "enabled": False,
                "device": "28989c89-e7d7-4664-9d18-a73647a844fb",
                "channel": "5421c268-8f5d-4972-a7b5-6b4295c3e4b1",
                "property": "ff7b36d7-a0b0-4336-9efb-a608c93b0974",
                "operand": "3",
                "operator": TriggerConditionOperator(TriggerConditionOperator.EQUAL).value,
                "trigger": "2cea2c1b-4790-4d82-8a9f-902c7155ab36",
            },
        )

        self.assertTrue(result)

        condition_item = conditions_repository.get_by_id(
            uuid.UUID("2726f19c-7759-440e-b6f5-8c3306692fa2", version=4)
        )

        self.assertIsInstance(condition_item, PropertyConditionItem)
        self.assertIsInstance(condition_item, ChannelPropertyConditionItem)
        self.assertEqual("2726f19c-7759-440e-b6f5-8c3306692fa2", condition_item.condition_id.__str__())
        self.assertIsInstance(condition_item.operator, TriggerConditionOperator)

    # -----------------------------------------------------------------------------

    def test_update_from_exchange(self) -> None:
        conditions_repository.initialize()

        condition_item = conditions_repository.get_by_id(
            uuid.UUID("2726f19c-7759-440e-b6f5-8c3306692fa2", version=4)
        )

        self.assertIsInstance(condition_item, PropertyConditionItem)
        self.assertIsInstance(condition_item, ChannelPropertyConditionItem)
        self.assertEqual("2726f19c-7759-440e-b6f5-8c3306692fa2", condition_item.condition_id.__str__())
        self.assertFalse(condition_item.enabled)

        result: bool = conditions_repository.update_from_exchange(
            RoutingKey(RoutingKey.TRIGGERS_CONDITIONS_ENTITY_UPDATED),
            {
                "id": "2726f19c-7759-440e-b6f5-8c3306692fa2",
                "type": TriggerConditionType(TriggerConditionType.CHANNEL_PROPERTY).value,
                "enabled": True,
                "device": "28989c89-e7d7-4664-9d18-a73647a844fb",
                "channel": "5421c268-8f5d-4972-a7b5-6b4295c3e4b1",
                "property": "ff7b36d7-a0b0-4336-9efb-a608c93b0974",
                "operand": "1",
                "operator": TriggerConditionOperator(TriggerConditionOperator.EQUAL).value,
                "trigger": "2cea2c1b-4790-4d82-8a9f-902c7155ab36",
            },
        )

        self.assertTrue(result)

        condition_item = conditions_repository.get_by_id(
            uuid.UUID("2726f19c-7759-440e-b6f5-8c3306692fa2", version=4)
        )

        self.assertIsInstance(condition_item, PropertyConditionItem)
        self.assertIsInstance(condition_item, ChannelPropertyConditionItem)
        self.assertEqual("2726f19c-7759-440e-b6f5-8c3306692fa2", condition_item.condition_id.__str__())
        self.assertTrue(condition_item.enabled)
        self.assertEqual("1", condition_item.operand)
        self.assertIsInstance(condition_item.operator, TriggerConditionOperator)

    # -----------------------------------------------------------------------------

    def test_delete_from_exchange(self) -> None:
        conditions_repository.initialize()

        condition_item = conditions_repository.get_by_id(
            uuid.UUID("2726f19c-7759-440e-b6f5-8c3306692fa2", version=4)
        )

        self.assertIsInstance(condition_item, PropertyConditionItem)
        self.assertIsInstance(condition_item, ChannelPropertyConditionItem)
        self.assertEqual("2726f19c-7759-440e-b6f5-8c3306692fa2", condition_item.condition_id.__str__())

        result: bool = conditions_repository.delete_from_exchange(
            RoutingKey(RoutingKey.TRIGGERS_CONDITIONS_ENTITY_DELETED),
            {
                "id": "2726f19c-7759-440e-b6f5-8c3306692fa2",
                "type": TriggerConditionType(TriggerConditionType.CHANNEL_PROPERTY).value,
                "enabled": False,
                "device": "28989c89-e7d7-4664-9d18-a73647a844fb",
                "channel": "5421c268-8f5d-4972-a7b5-6b4295c3e4b1",
                "property": "ff7b36d7-a0b0-4336-9efb-a608c93b0974",
                "operand": "3",
                "operator": TriggerConditionOperator(TriggerConditionOperator.EQUAL).value,
                "trigger": "2cea2c1b-4790-4d82-8a9f-902c7155ab36",
            },
        )

        self.assertTrue(result)

        condition_item = conditions_repository.get_by_id(
            uuid.UUID("2726f19c-7759-440e-b6f5-8c3306692fa2", version=4)
        )

        self.assertIsNone(condition_item)
