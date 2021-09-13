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
from triggers_module.items import PropertyConditionItem, ChannelPropertyConditionItem
from triggers_module.reposetories import conditions_repository

# Tests libs
from tests.pytests.tests import DbTestCase


class TestConditionItem(DbTestCase):
    def test_transform_to_dict(self) -> None:
        conditions_repository.initialize()

        condition_item = conditions_repository.get_by_id(
            uuid.UUID("2726f19c-7759-440e-b6f5-8c3306692fa2", version=4)
        )

        self.assertIsInstance(condition_item, PropertyConditionItem)
        self.assertIsInstance(condition_item, ChannelPropertyConditionItem)

        self.assertEqual({
            "id": "2726f19c-7759-440e-b6f5-8c3306692fa2",
            "type": "channel-property",
            "enabled": False,
            "trigger": "2cea2c1b-4790-4d82-8a9f-902c7155ab36",
            "device": "28989c89-e7d7-4664-9d18-a73647a844fb",
            "channel": "5421c268-8f5d-4972-a7b5-6b4295c3e4b1",
            "property": "ff7b36d7-a0b0-4336-9efb-a608c93b0974",
            "operand": "3",
            "operator": "eq",
        }, condition_item.to_dict())

    # -----------------------------------------------------------------------------

    def test_validate(self) -> None:
        conditions_repository.initialize()

        condition_item = conditions_repository.get_by_id(
            uuid.UUID("2726f19c-7759-440e-b6f5-8c3306692fa2", version=4)
        )

        self.assertIsInstance(condition_item, PropertyConditionItem)
        self.assertIsInstance(condition_item, ChannelPropertyConditionItem)

        self.assertTrue(condition_item.validate("3"))

        self.assertFalse(condition_item.validate("1"))
