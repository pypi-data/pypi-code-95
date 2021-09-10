#!/usr/bin/python3

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

"""
Module models definitions
"""

# Library dependencies
import json
import uuid
from typing import List, Dict
import modules_metadata.exceptions as metadata_exceptions
from modules_metadata.loader import load_schema
from modules_metadata.routing import RoutingKey
from modules_metadata.validator import validate
from modules_metadata.triggers_module import TriggerConditionOperator
from modules_metadata.types import ModuleOrigin
from pony.orm import core as orm

# Library libs
from triggers_module.exceptions import HandleExchangeDataException
from triggers_module.models import (
    TriggerEntity,
    ActionEntity,
    DevicePropertyActionEntity,
    ChannelPropertyActionEntity,
    ConditionEntity,
    DevicePropertyConditionEntity,
    ChannelPropertyConditionEntity,
    TimeConditionEntity,
    DateConditionEntity,
)
from triggers_module.items import (
    TriggerItem,
    ConditionItem,
    DevicePropertyConditionItem,
    ChannelPropertyConditionItem,
    TimeConditionItem,
    DateConditionItem,
    ActionItem,
    PropertyActionItem,
    DevicePropertyActionItem,
    ChannelPropertyActionItem,
)


class TriggersRepository:
    """
    Triggers repository

    @package        FastyBird:TriggersModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """
    __items: Dict[str, TriggerItem] or None = None

    __iterator_index = 0

    # -----------------------------------------------------------------------------

    def get_by_id(self, trigger_id: uuid.UUID) -> TriggerItem or None:
        """Find trigger in cache by provided identifier"""
        if self.__items is None:
            self.initialize()

        if trigger_id.__str__() in self.__items:
            return self.__items[trigger_id.__str__()]

        return None

    # -----------------------------------------------------------------------------

    def clear(self) -> None:
        """Clear items cache"""
        self.__items = None

    # -----------------------------------------------------------------------------

    @orm.db_session
    def create_from_exchange(self, routing_key: RoutingKey, data: Dict) -> bool:
        """Process received trigger message from exchange when entity was created"""
        if routing_key != RoutingKey.TRIGGERS_ENTITY_CREATED:
            return False

        if self.__items is None:
            self.initialize()

            return True

        data: Dict = validate_exchange_data(ModuleOrigin(ModuleOrigin.TRIGGERS_MODULE), routing_key, data)

        entity: TriggerEntity or None = TriggerEntity.get(trigger_id=uuid.UUID(data.get("id"), version=4))

        if entity is not None:
            self.__items[entity.trigger_id.__str__()] = self.__create_item(entity)

            return True

        return False

    # -----------------------------------------------------------------------------

    @orm.db_session
    def update_from_exchange(self, routing_key: RoutingKey, data: Dict) -> bool:
        """Process received trigger message from exchange when entity was updated"""
        if routing_key != RoutingKey.TRIGGERS_ENTITY_UPDATED:
            return False

        if self.__items is None:
            self.initialize()

            return True

        validated_data: Dict = validate_exchange_data(ModuleOrigin(ModuleOrigin.TRIGGERS_MODULE), routing_key, data)

        if validated_data.get("id") not in self.__items:
            entity: TriggerEntity or None = TriggerEntity.get(trigger_id=uuid.UUID(validated_data.get("id"), version=4))

            if entity is not None:
                self.__items[entity.trigger_id.__str__()] = self.__create_item(entity)

                return True

            return False

        item = self.__update_item(
            self.get_by_id(uuid.UUID(validated_data.get("id"), version=4)),
            validated_data,
        )

        if item is not None:
            self.__items[validated_data.get("id")] = item

            return True

        return False

    # -----------------------------------------------------------------------------

    @orm.db_session
    def delete_from_exchange(self, routing_key: RoutingKey, data: Dict) -> bool:
        """Process received trigger message from exchange when entity was updated"""
        if routing_key != RoutingKey.TRIGGERS_ENTITY_DELETED:
            return False

        if data.get("id") in self.__items:
            del self.__items[data.get("id")]

            return True

        return False

    # -----------------------------------------------------------------------------

    @orm.db_session
    def initialize(self) -> None:
        """Initialize repository by fetching entities from database"""
        items: Dict[str, TriggerItem] = {}

        for trigger in TriggerEntity.select():
            if self.__items is None or trigger.trigger_id.__str__() not in self.__items:
                item = self.__create_item(trigger)

            else:
                item = self.__update_item(self.get_by_id(trigger.trigger_id), trigger.to_dict())

            if item is not None:
                items[trigger.trigger_id.__str__()] = item

        self.__items = items

    # -----------------------------------------------------------------------------

    @staticmethod
    def __create_item(entity: TriggerEntity) -> TriggerItem:
        return TriggerItem(
            trigger_id=entity.trigger_id,
            enabled=entity.enabled,
        )

    # -----------------------------------------------------------------------------

    @staticmethod
    def __update_item(item: TriggerItem, data: Dict) -> TriggerItem:
        return TriggerItem(
            trigger_id=item.trigger_id,
            enabled=bool(data.get("enabled", item.enabled)),
        )

    # -----------------------------------------------------------------------------

    def __iter__(self) -> "TriggersRepository":
        # Reset index for nex iteration
        self.__iterator_index = 0

        return self

    # -----------------------------------------------------------------------------

    def __len__(self):
        if self.__items is None:
            self.initialize()

        return len(self.__items.values())

    # -----------------------------------------------------------------------------

    def __next__(self) -> TriggerItem:
        if self.__items is None:
            self.initialize()

        if self.__iterator_index < len(self.__items.values()):
            items: List[TriggerItem] = list(self.__items.values())

            result: TriggerItem = items[self.__iterator_index]

            self.__iterator_index += 1

            return result

        # Reset index for nex iteration
        self.__iterator_index = 0

        # End of iteration
        raise StopIteration


class ActionsRepository:
    """
    Triggers actions repository

    @package        FastyBird:TriggersModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """
    __items: Dict[str, ActionItem] or None = None

    __iterator_index = 0

    # -----------------------------------------------------------------------------

    def get_by_id(self, action_id: uuid.UUID) -> ActionItem or None:
        """Find action in cache by provided identifier"""
        if self.__items is None:
            self.initialize()

        if action_id.__str__() in self.__items:
            return self.__items[action_id.__str__()]

        return None

    # -----------------------------------------------------------------------------

    def get_by_property_identifier(
            self,
            property_id: uuid.UUID,
    ) -> DevicePropertyConditionItem or ChannelPropertyConditionItem or None:
        """Find action in cache by provided property identifier"""
        if self.__items is None:
            self.initialize()

        for action in self.__items.values():
            if isinstance(action, DevicePropertyActionItem) and action.device_property.__eq__(property_id):
                return action

            if isinstance(action, ChannelPropertyActionItem) and action.channel_property.__eq__(property_id):
                return action

        return None

    # -----------------------------------------------------------------------------

    def get_all_by_property_identifier(
            self,
            property_id: uuid.UUID,
    ) -> List[DevicePropertyConditionItem or ChannelPropertyConditionItem]:
        """Find actions in cache by provided property identifier"""
        if self.__items is None:
            self.initialize()

        actions: List[DevicePropertyActionItem or ChannelPropertyActionItem] = []

        for action in self.__items.values():
            if isinstance(action, DevicePropertyActionItem) and action.device_property.__eq__(property_id):
                actions.append(action)

            if isinstance(action, ChannelPropertyActionItem) and action.channel_property.__eq__(property_id):
                actions.append(action)

        return actions

    # -----------------------------------------------------------------------------

    def get_all_for_trigger(self, trigger_id: uuid.UUID) -> List[ActionItem]:
        """Find all actions in cache for provided trigger identifier"""
        if self.__items is None:
            self.initialize()

        actions: List[ActionItem] = []

        for action in self.__items.values():
            if action.trigger_id.__eq__(trigger_id):
                actions.append(action)

        return actions

    # -----------------------------------------------------------------------------

    def clear(self) -> None:
        """Clear items cache"""
        self.__items = None

    # -----------------------------------------------------------------------------

    @orm.db_session
    def create_from_exchange(self, routing_key: RoutingKey, data: Dict) -> bool:
        """Process received action message from exchange when entity was created"""
        if routing_key != RoutingKey.TRIGGERS_ACTIONS_ENTITY_CREATED:
            return False

        if self.__items is None:
            self.initialize()

            return True

        data: Dict = validate_exchange_data(ModuleOrigin(ModuleOrigin.TRIGGERS_MODULE), routing_key, data)

        entity: ActionEntity or None = ActionEntity.get(action_id=uuid.UUID(data.get("id"), version=4))

        if entity is not None:
            self.__items[entity.action_id.__str__()] = self.__create_item(entity)

            return True

        return False

    # -----------------------------------------------------------------------------

    @orm.db_session
    def update_from_exchange(self, routing_key: RoutingKey, data: Dict) -> bool:
        """Process received action message from exchange when entity was updated"""
        if routing_key != RoutingKey.TRIGGERS_ACTIONS_ENTITY_UPDATED:
            return False

        if self.__items is None:
            self.initialize()

            return True

        validated_data: Dict = validate_exchange_data(ModuleOrigin(ModuleOrigin.TRIGGERS_MODULE), routing_key, data)

        if validated_data.get("id") not in self.__items:
            entity: ActionEntity or None = ActionEntity.get(action_id=uuid.UUID(validated_data.get("id"), version=4))

            if entity is not None:
                self.__items[entity.action_id.__str__()] = self.__create_item(entity)

                return True

            return False

        item = self.__update_item(
            self.get_by_id(uuid.UUID(validated_data.get("id"), version=4)),
            validated_data,
        )

        if item is not None:
            self.__items[validated_data.get("id")] = item

            return True

        return False

    # -----------------------------------------------------------------------------

    @orm.db_session
    def delete_from_exchange(self, routing_key: RoutingKey, data: Dict) -> bool:
        """Process received action message from exchange when entity was updated"""
        if routing_key != RoutingKey.TRIGGERS_ACTIONS_ENTITY_DELETED:
            return False

        if data.get("id") in self.__items:
            del self.__items[data.get("id")]

            return True

        return False

    # -----------------------------------------------------------------------------

    @orm.db_session
    def initialize(self) -> None:
        """Initialize repository by fetching entities from database"""
        items: Dict[str, ActionItem] = {}

        for action in ActionEntity.select():
            if self.__items is None or action.action_id.__str__() not in self.__items:
                item = self.__create_item(action)

            else:
                item = self.__update_item(self.get_by_id(action.action_id), action.to_dict())

            if item is not None:
                items[action.action_id.__str__()] = item

        self.__items = items

    # -----------------------------------------------------------------------------

    @staticmethod
    def __create_item(entity: ActionEntity) -> ActionItem or None:
        if isinstance(entity, DevicePropertyActionEntity):
            return DevicePropertyActionItem(
                action_id=entity.action_id,
                trigger_id=entity.trigger.trigger_id,
                enabled=entity.enabled,
                value=entity.value,
                device_property=entity.device_property,
                device=entity.device,
                is_triggered=False,
            )

        if isinstance(entity, ChannelPropertyActionEntity):
            return ChannelPropertyActionItem(
                action_id=entity.action_id,
                trigger_id=entity.trigger.trigger_id,
                enabled=entity.enabled,
                value=entity.value,
                channel_property=entity.channel_property,
                channel=entity.channel,
                device=entity.device,
                is_triggered=False,
            )

        return None

    # -----------------------------------------------------------------------------

    @staticmethod
    def __update_item(item: ActionItem, data: Dict) -> ActionItem or None:
        if isinstance(item, DevicePropertyActionItem):
            return DevicePropertyActionItem(
                action_id=item.action_id,
                trigger_id=item.trigger_id,
                enabled=data.get("enabled", item.enabled),
                value=data.get("value", item.value),
                device_property=item.device_property,
                device=item.device,
                is_triggered=item.is_triggered,
            )

        if isinstance(item, ChannelPropertyActionItem):
            return ChannelPropertyActionItem(
                action_id=item.action_id,
                trigger_id=item.trigger_id,
                enabled=data.get("enabled", item.enabled),
                value=data.get("value", item.value),
                channel_property=item.channel_property,
                channel=item.channel,
                device=item.device,
                is_triggered=item.is_triggered,
            )

        return None

    # -----------------------------------------------------------------------------

    def __iter__(self) -> "ActionsRepository":
        # Reset index for nex iteration
        self.__iterator_index = 0

        return self

    # -----------------------------------------------------------------------------

    def __len__(self):
        if self.__items is None:
            self.initialize()

        return len(self.__items.values())

    # -----------------------------------------------------------------------------

    def __next__(self) -> PropertyActionItem:
        if self.__items is None:
            self.initialize()

        if self.__iterator_index < len(self.__items.values()):
            items: List[PropertyActionItem] = list(self.__items.values())

            result: PropertyActionItem = items[self.__iterator_index]

            self.__iterator_index += 1

            return result

        # Reset index for nex iteration
        self.__iterator_index = 0

        # End of iteration
        raise StopIteration


class ConditionsRepository:
    """
    Triggers conditions repository

    @package        FastyBird:TriggersModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """
    __items: Dict[str, ConditionItem] or None = None

    __iterator_index = 0

    # -----------------------------------------------------------------------------

    def get_by_id(self, condition_id: uuid.UUID) -> ConditionItem or None:
        """Find condition in cache by provided identifier"""
        if self.__items is None:
            self.initialize()

        if condition_id.__str__() in self.__items:
            return self.__items[condition_id.__str__()]

        return None

    # -----------------------------------------------------------------------------

    def get_by_property_identifier(
            self,
            property_id: uuid.UUID,
    ) -> DevicePropertyConditionItem or ChannelPropertyConditionItem or None:
        """Find condition in cache by provided property identifier"""
        if self.__items is None:
            self.initialize()

        for condition in self.__items.values():
            if isinstance(condition, DevicePropertyConditionItem) and condition.device_property.__eq__(property_id):
                return condition

            if isinstance(condition, ChannelPropertyConditionItem) and condition.channel_property.__eq__(property_id):
                return condition

        return None

    # -----------------------------------------------------------------------------

    def get_all_by_property_identifier(
            self,
            property_id: uuid.UUID,
    ) -> List[DevicePropertyConditionItem or ChannelPropertyConditionItem]:
        """Find conditions in cache by provided property identifier"""
        if self.__items is None:
            self.initialize()

        conditions: List[DevicePropertyConditionItem or ChannelPropertyConditionItem] = []

        for condition in self.__items.values():
            if isinstance(condition, DevicePropertyConditionItem) and condition.device_property.__eq__(property_id):
                conditions.append(condition)

            if isinstance(condition, ChannelPropertyConditionItem) and condition.channel_property.__eq__(property_id):
                conditions.append(condition)

        return conditions

    # -----------------------------------------------------------------------------

    def get_all_for_trigger(
            self,
            trigger_id: uuid.UUID,
    ) -> List[ConditionItem]:
        """Find all conditions in cache for provided trigger identifier"""
        if self.__items is None:
            self.initialize()

        conditions: List[ConditionItem] = []

        for condition in self.__items.values():
            if condition.trigger_id.__eq__(trigger_id):
                conditions.append(condition)

        return conditions

    # -----------------------------------------------------------------------------

    def clear(self) -> None:
        """Clear items cache"""
        self.__items = None

    # -----------------------------------------------------------------------------

    @orm.db_session
    def create_from_exchange(self, routing_key: RoutingKey, data: Dict) -> bool:
        """Process received condition message from exchange when entity was created"""
        if routing_key != RoutingKey.TRIGGERS_CONDITIONS_ENTITY_CREATED:
            return False

        if self.__items is None:
            self.initialize()

            return True

        data: Dict = validate_exchange_data(ModuleOrigin(ModuleOrigin.TRIGGERS_MODULE), routing_key, data)

        entity: ConditionEntity or None = ConditionEntity.get(condition_id=uuid.UUID(data.get("id"), version=4))

        if entity is not None:
            self.__items[entity.condition_id.__str__()] = self.__create_item(entity)

            return True

        return False

    # -----------------------------------------------------------------------------

    @orm.db_session
    def update_from_exchange(self, routing_key: RoutingKey, data: Dict) -> bool:
        """Process received condition message from exchange when entity was updated"""
        if routing_key != RoutingKey.TRIGGERS_CONDITIONS_ENTITY_UPDATED:
            return False

        if self.__items is None:
            self.initialize()

            return True

        validated_data: Dict = validate_exchange_data(ModuleOrigin(ModuleOrigin.TRIGGERS_MODULE), routing_key, data)

        if validated_data.get("id") not in self.__items:
            entity: ConditionEntity or None = ConditionEntity.get(
                condition_id=uuid.UUID(validated_data.get("id"), version=4)
            )

            if entity is not None:
                self.__items[entity.condition_id.__str__()] = self.__create_item(entity)

                return True

            return False

        item = self.__update_item(
            self.get_by_id(uuid.UUID(validated_data.get("id"), version=4)),
            validated_data,
        )

        if item is not None:
            self.__items[validated_data.get("id")] = item

            return True

        return False

    # -----------------------------------------------------------------------------

    @orm.db_session
    def delete_from_exchange(self, routing_key: RoutingKey, data: Dict) -> bool:
        """Process received condition message from exchange when entity was updated"""
        if routing_key != RoutingKey.TRIGGERS_CONDITIONS_ENTITY_DELETED:
            return False

        if data.get("id") in self.__items:
            del self.__items[data.get("id")]

            return True

        return False

    # -----------------------------------------------------------------------------

    @orm.db_session
    def initialize(self) -> None:
        """Initialize conditions repository by fetching entities from database"""
        items: Dict[str, ConditionItem] = {}

        for condition in ConditionEntity.select():
            if self.__items is None or condition.condition_id.__str__() not in self.__items:
                item = self.__create_item(condition)

            else:
                item = self.__update_item(self.get_by_id(condition.condition_id), condition.to_dict())

            if item is not None:
                items[condition.condition_id.__str__()] = item

        self.__items = items

    # -----------------------------------------------------------------------------

    @staticmethod
    def __create_item(entity: ConditionEntity) -> ConditionItem or None:
        if isinstance(entity, DevicePropertyConditionEntity):
            return DevicePropertyConditionItem(
                condition_id=entity.condition_id,
                trigger_id=entity.trigger.trigger_id,
                enabled=entity.enabled,
                operator=entity.operator,
                operand=entity.operand,
                device_property=entity.device_property,
                device=entity.device,
                is_fulfilled=False,
            )

        if isinstance(entity, ChannelPropertyConditionEntity):
            return ChannelPropertyConditionItem(
                condition_id=entity.condition_id,
                trigger_id=entity.trigger.trigger_id,
                enabled=entity.enabled,
                operator=entity.operator,
                operand=entity.operand,
                channel_property=entity.channel_property,
                channel=entity.channel,
                device=entity.device,
                is_fulfilled=False,
            )

        if isinstance(entity, TimeConditionEntity):
            return TimeConditionItem(
                condition_id=entity.condition_id,
                trigger_id=entity.trigger.trigger_id,
                enabled=entity.enabled,
                time=entity.time,
                days=entity.days,
            )

        if isinstance(entity, DateConditionEntity):
            return DateConditionItem(
                condition_id=entity.condition_id,
                trigger_id=entity.trigger.trigger_id,
                enabled=entity.enabled,
                date=entity.date,
            )

        return None

    # -----------------------------------------------------------------------------

    @staticmethod
    def __update_item(item: ConditionItem, data: Dict) -> ConditionItem or None:
        if isinstance(item, DevicePropertyConditionItem):
            return DevicePropertyConditionItem(
                condition_id=item.condition_id,
                trigger_id=item.trigger_id,
                enabled=data.get("enabled", item.enabled),
                operator=TriggerConditionOperator(data.get("operator", item.operator.value)),
                operand=data.get("operand", item.operand),
                device_property=item.device_property,
                device=item.device,
                is_fulfilled=item.is_fulfilled,
            )

        if isinstance(item, ChannelPropertyConditionItem):
            return ChannelPropertyConditionItem(
                condition_id=item.condition_id,
                trigger_id=item.trigger_id,
                enabled=data.get("enabled", item.enabled),
                operator=TriggerConditionOperator(data.get("operator", item.operator.value)),
                operand=data.get("operand", item.operand),
                channel_property=item.channel_property,
                channel=item.channel,
                device=item.device,
                is_fulfilled=item.is_fulfilled,
            )

        if isinstance(item, TimeConditionItem):
            return TimeConditionItem(
                condition_id=item.condition_id,
                trigger_id=item.trigger_id,
                enabled=data.get("enabled", item.enabled),
                time=data.get("time", item.time),
                days=data.get("days", item.days),
            )

        if isinstance(item, DateConditionItem):
            return DateConditionItem(
                condition_id=item.condition_id,
                trigger_id=item.trigger_id,
                enabled=data.get("enabled", item.enabled),
                date=data.get("time", item.date),
            )

        return None

    # -----------------------------------------------------------------------------

    def __iter__(self) -> "ConditionsRepository":
        # Reset index for nex iteration
        self.__iterator_index = 0

        return self

    # -----------------------------------------------------------------------------

    def __len__(self):
        if self.__items is None:
            self.initialize()

        return len(self.__items.values())

    # -----------------------------------------------------------------------------

    def __next__(self) -> ConditionItem:
        if self.__items is None:
            self.initialize()

        if self.__iterator_index < len(self.__items.values()):
            items: List[ConditionItem] = list(self.__items.values())

            result: ConditionItem = items[self.__iterator_index]

            self.__iterator_index += 1

            return result

        # Reset index for nex iteration
        self.__iterator_index = 0

        # End of iteration
        raise StopIteration


def validate_exchange_data(origin: ModuleOrigin, routing_key: RoutingKey, data: Dict) -> Dict:
    """
    Validate received RPC message against defined schema
    """
    try:
        schema: str = load_schema(origin, routing_key)

    except metadata_exceptions.FileNotFoundException as ex:
        raise HandleExchangeDataException("Provided data could not be validated") from ex

    except metadata_exceptions.InvalidArgumentException as ex:
        raise HandleExchangeDataException("Provided data could not be validated") from ex

    try:
        return validate(json.dumps(data), schema)

    except metadata_exceptions.MalformedInputException as ex:
        raise HandleExchangeDataException("Provided data are not in valid json format") from ex

    except metadata_exceptions.LogicException as ex:
        raise HandleExchangeDataException("Provided data could not be validated") from ex

    except metadata_exceptions.InvalidDataException as ex:
        raise HandleExchangeDataException("Provided data are not valid") from ex


triggers_repository = TriggersRepository()
actions_repository = ActionsRepository()
conditions_repository = ConditionsRepository()
