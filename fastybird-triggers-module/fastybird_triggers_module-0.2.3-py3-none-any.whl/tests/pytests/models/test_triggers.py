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
from triggers_module.items import TriggerItem
from triggers_module.models import triggers_repository

# Tests libs
from tests.pytests.tests import DbTestCase


class TestTriggersRepository(DbTestCase):
    def test_repository_iterator(self) -> None:
        self.assertEqual(6, len(triggers_repository))

    # -----------------------------------------------------------------------------

    def test_get_item(self) -> None:
        trigger_item = triggers_repository.get_trigger_by_id(
            uuid.UUID("c64ba1c4-0eda-4cab-87a0-4d634f7b67f4", version=4)
        )

        self.assertIsInstance(trigger_item, TriggerItem)
        self.assertEqual("c64ba1c4-0eda-4cab-87a0-4d634f7b67f4", trigger_item.trigger_id.__str__())
