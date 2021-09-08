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
from triggers_module.models import conditions_repository

# Tests libs
from tests.pytests.tests import DbTestCase


class TestConditionsRepository(DbTestCase):
    def test_repository_iterator(self) -> None:
        self.assertEqual(3, len(conditions_repository))

    # -----------------------------------------------------------------------------

    def test_get_item(self) -> None:
        condition_item = conditions_repository.get_by_id(
            uuid.UUID("2726f19c-7759-440e-b6f5-8c3306692fa2", version=4)
        )

        self.assertIsInstance(condition_item, PropertyConditionItem)
        self.assertIsInstance(condition_item, ChannelPropertyConditionItem)
        self.assertEqual("2726f19c-7759-440e-b6f5-8c3306692fa2", condition_item.condition_id.__str__())

    # -----------------------------------------------------------------------------

    def test_get_item_by_property(self) -> None:
        condition_item = conditions_repository.get_by_property_identifier(
            uuid.UUID("ff7b36d7-a0b0-4336-9efb-a608c93b0974", version=4)
        )

        self.assertIsInstance(condition_item, PropertyConditionItem)
        self.assertIsInstance(condition_item, ChannelPropertyConditionItem)
        self.assertEqual("2726f19c-7759-440e-b6f5-8c3306692fa2", condition_item.condition_id.__str__())
