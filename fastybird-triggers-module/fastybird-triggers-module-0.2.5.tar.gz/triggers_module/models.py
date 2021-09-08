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
import uuid
import datetime
from enum import Enum
from typing import List, Tuple, Dict
from application_events.database import (
    DatabaseEntityCreatedEvent,
    DatabaseEntityUpdatedEvent,
    DatabaseEntityDeletedEvent,
)
from application_events.dispatcher import app_dispatcher
from modules_metadata.triggers_module import TriggerConditionOperator
from modules_metadata.types import ModuleOrigin
from pony.orm import core as orm, Database, PrimaryKey, Required, Optional, Set, Discriminator, Json
from pony.orm.dbproviders.mysql import MySQLProvider
from pony.orm.dbproviders.sqlite import SQLiteProvider

# Library libs
from triggers_module.converters import EnumConverter
from triggers_module.items import (
    TriggerItem,
    ConditionItem,
    DevicePropertyConditionItem,
    ChannelPropertyConditionItem,
    TimeConditionItem,
    DateConditionItem,
    PropertyActionItem,
    DevicePropertyActionItem,
    ChannelPropertyActionItem,
)

# Create triggers module database accessor
db: Database = Database()

# Add ENUM converter
MySQLProvider.converter_classes.append((Enum, EnumConverter))
SQLiteProvider.converter_classes.append((Enum, EnumConverter))


class EntityEventMixin:
    """
    Entity event mixin

    @package        FastyBird:TriggersModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """
    def after_insert(self) -> None:
        """After insert entity hook"""
        if isinstance(self, orm.Entity):
            app_dispatcher.dispatch(
                DatabaseEntityCreatedEvent.EVENT_NAME,
                DatabaseEntityCreatedEvent(
                    ModuleOrigin(ModuleOrigin.TRIGGERS_MODULE),
                    self,
                ),
            )

    # -----------------------------------------------------------------------------

    def after_update(self) -> None:
        """After update entity hook"""
        if isinstance(self, orm.Entity):
            app_dispatcher.dispatch(
                DatabaseEntityUpdatedEvent.EVENT_NAME,
                DatabaseEntityUpdatedEvent(
                    ModuleOrigin(ModuleOrigin.TRIGGERS_MODULE),
                    self,
                ),
            )

    # -----------------------------------------------------------------------------

    def after_delete(self) -> None:
        """After delete entity hook"""
        if isinstance(self, orm.Entity):
            app_dispatcher.dispatch(
                DatabaseEntityDeletedEvent.EVENT_NAME,
                DatabaseEntityDeletedEvent(
                    ModuleOrigin(ModuleOrigin.TRIGGERS_MODULE),
                    self,
                ),
            )


class TriggerEntity(EntityEventMixin, db.Entity):
    """
    Base trigger entity

    @package        FastyBird:TriggersModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """
    _table_: str = "fb_triggers"

    type = Discriminator(str, column="trigger_type")
    _discriminator_: str = "trigger"

    trigger_id: uuid.UUID = PrimaryKey(uuid.UUID, default=uuid.uuid4, column="trigger_id")
    name: str or None = Required(str, column="trigger_name", max_len=100, nullable=False)
    comment: str or None = Optional(str, column="trigger_comment", nullable=True, default=None)
    enabled: bool = Required(bool, column="trigger_enabled", nullable=False, default=True)
    params: Json or None = Optional(Json, column="params", nullable=True)
    created_at: datetime.datetime or None = Optional(datetime.datetime, column="created_at", nullable=True)
    updated_at: datetime.datetime or None = Optional(datetime.datetime, column="updated_at", nullable=True)

    actions: List["ActionEntity"] = Set("ActionEntity", reverse="trigger")
    notifications: List["NotificationEntity"] = Set("NotificationEntity", reverse="trigger")

    # -----------------------------------------------------------------------------

    def to_dict(
        self,
        only: Tuple = None,  # pylint: disable=unused-argument
        exclude: Tuple = None,  # pylint: disable=unused-argument
        with_collections: bool = False,  # pylint: disable=unused-argument
        with_lazy: bool = False,  # pylint: disable=unused-argument
        related_objects: bool = False,  # pylint: disable=unused-argument
    ) -> Dict[str, str or int or bool or None]:
        """Transform entity to dictionary"""
        return {
            "id": self.trigger_id.__str__(),
            "type": self.type,
            "name": self.name,
            "comment": self.comment,
            "enabled": self.enabled,
            "params": self.params,
        }

    # -----------------------------------------------------------------------------

    def before_insert(self) -> None:
        """Before insert entity hook"""
        self.created_at = datetime.datetime.now()

    # -----------------------------------------------------------------------------

    def before_update(self) -> None:
        """Before update entity hook"""
        self.updated_at = datetime.datetime.now()


class ManualTriggerEntity(TriggerEntity):
    """
    Manual trigger entity

    @package        FastyBird:TriggersModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """
    _discriminator_: str = "manual"


class AutomaticTriggerEntity(TriggerEntity):
    """
    Automatic trigger entity

    @package        FastyBird:TriggersModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """
    _discriminator_: str = "automatic"

    conditions: List["ConditionEntity"] = Set("ConditionEntity", reverse="trigger")


class ActionEntity(EntityEventMixin, db.Entity):
    """
    Base action entity

    @package        FastyBird:TriggersModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """
    _table_: str = "fb_actions"

    type = Discriminator(str, column="action_type")

    action_id: uuid.UUID = PrimaryKey(uuid.UUID, default=uuid.uuid4, column="action_id")
    enabled: bool = Required(bool, column="action_enabled", nullable=False, default=True)
    created_at: datetime.datetime or None = Optional(datetime.datetime, column="created_at", nullable=True)
    updated_at: datetime.datetime or None = Optional(datetime.datetime, column="updated_at", nullable=True)

    trigger: TriggerEntity = Required("TriggerEntity", reverse="actions", column="trigger_id", nullable=False)

    # -----------------------------------------------------------------------------

    def to_dict(
        self,
        only: Tuple = None,  # pylint: disable=unused-argument
        exclude: Tuple = None,  # pylint: disable=unused-argument
        with_collections: bool = False,  # pylint: disable=unused-argument
        with_lazy: bool = False,  # pylint: disable=unused-argument
        related_objects: bool = False,  # pylint: disable=unused-argument
    ) -> Dict[str, str or int or bool or None]:
        """Transform entity to dictionary"""
        return {
            "id": self.action_id.__str__(),
            "type": self.type,
            "enabled": self.enabled,
            "trigger": self.trigger.trigger_id.__str__(),
        }

    # -----------------------------------------------------------------------------

    def before_insert(self) -> None:
        """Before insert entity hook"""
        self.created_at = datetime.datetime.now()

    # -----------------------------------------------------------------------------

    def before_update(self) -> None:
        """Before update entity hook"""
        self.updated_at = datetime.datetime.now()


class PropertyActionEntity(ActionEntity):
    """
    Property action entity

    @package        FastyBird:TriggersModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """
    device: uuid.UUID = Required(uuid.UUID, column="action_device", nullable=True)

    value: str = Required(str, column="action_value", max_len=100, nullable=True)

    # -----------------------------------------------------------------------------

    def to_dict(
        self,
        only: Tuple = None,
        exclude: Tuple = None,
        with_collections: bool = False,
        with_lazy: bool = False,
        related_objects: bool = False,
    ) -> Dict[str, str or int or bool or None]:
        """Transform entity to dictionary"""
        return {**{
            "device": self.device.__str__(),
            "value": self.value,
        }, **super().to_dict(only, exclude, with_collections, with_lazy, related_objects)}


class DevicePropertyActionEntity(PropertyActionEntity):
    """
    Device property action entity

    @package        FastyBird:TriggersModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """
    _discriminator_: str = "device_property"

    device_property: uuid.UUID = Required(uuid.UUID, column="action_device_property", nullable=True)

    # -----------------------------------------------------------------------------

    def to_dict(
        self,
        only: Tuple = None,
        exclude: Tuple = None,
        with_collections: bool = False,
        with_lazy: bool = False,
        related_objects: bool = False,
    ) -> Dict[str, str or int or bool or None]:
        """Transform entity to dictionary"""
        return {**{
            "property": self.device_property.__str__(),
        }, **super().to_dict(only, exclude, with_collections, with_lazy, related_objects)}


class ChannelPropertyActionEntity(PropertyActionEntity):
    """
    Channel property action entity

    @package        FastyBird:TriggersModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """
    _discriminator_: str = "channel_property"

    channel: uuid.UUID = Required(uuid.UUID, column="action_channel", nullable=True)
    channel_property: uuid.UUID = Required(uuid.UUID, column="action_channel_property", nullable=True)

    # -----------------------------------------------------------------------------

    def to_dict(
        self,
        only: Tuple = None,
        exclude: Tuple = None,
        with_collections: bool = False,
        with_lazy: bool = False,
        related_objects: bool = False,
    ) -> Dict[str, str or int or bool or None]:
        """Transform entity to dictionary"""
        return {**{
            "channel": self.channel.__str__(),
            "property": self.channel_property.__str__(),
        }, **super().to_dict(only, exclude, with_collections, with_lazy, related_objects)}


class NotificationEntity(EntityEventMixin, db.Entity):
    """
    Base notification entity

    @package        FastyBird:TriggersModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """
    _table_: str = "fb_notifications"

    type = Discriminator(str, column="notification_type")

    notification_id: uuid.UUID = PrimaryKey(uuid.UUID, default=uuid.uuid4, column="notification_id")
    enabled: bool = Required(bool, column="notification_enabled", nullable=False, default=True)
    created_at: datetime.datetime or None = Optional(datetime.datetime, column="created_at", nullable=True)
    updated_at: datetime.datetime or None = Optional(datetime.datetime, column="updated_at", nullable=True)

    trigger: TriggerEntity = Required("TriggerEntity", reverse="notifications", column="trigger_id", nullable=False)

    # -----------------------------------------------------------------------------

    def to_dict(
        self,
        only: Tuple = None,  # pylint: disable=unused-argument
        exclude: Tuple = None,  # pylint: disable=unused-argument
        with_collections: bool = False,  # pylint: disable=unused-argument
        with_lazy: bool = False,  # pylint: disable=unused-argument
        related_objects: bool = False,  # pylint: disable=unused-argument
    ) -> Dict[str, str or int or bool or None]:
        """Transform entity to dictionary"""
        return {
            "id": self.notification_id.__str__(),
            "type": self.type,
            "enabled": self.enabled,
            "trigger": self.trigger.trigger_id.__str__(),
        }

    # -----------------------------------------------------------------------------

    def before_insert(self) -> None:
        """Before insert entity hook"""
        self.created_at = datetime.datetime.now()

    # -----------------------------------------------------------------------------

    def before_update(self) -> None:
        """Before update entity hook"""
        self.updated_at = datetime.datetime.now()


class EmailNotificationEntity(NotificationEntity):
    """
    Email notification entity

    @package        FastyBird:TriggersModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """
    _discriminator_: str = "email"

    email: str = Required(str, column="notification_email", max_len=150, nullable=True)

    # -----------------------------------------------------------------------------

    def to_dict(
        self,
        only: Tuple = None,
        exclude: Tuple = None,
        with_collections: bool = False,
        with_lazy: bool = False,
        related_objects: bool = False,
    ) -> Dict[str, str or int or bool or None]:
        """Transform entity to dictionary"""
        return {**{
            "email": self.email,
        }, **super().to_dict(only, exclude, with_collections, with_lazy, related_objects)}


class SmsNotificationEntity(NotificationEntity):
    """
    SMS notification entity

    @package        FastyBird:TriggersModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """
    _discriminator_: str = "sms"

    phone: str = Required(str, column="notification_phone", max_len=150, nullable=True)

    # -----------------------------------------------------------------------------

    def to_dict(
        self,
        only: Tuple = None,
        exclude: Tuple = None,
        with_collections: bool = False,
        with_lazy: bool = False,
        related_objects: bool = False,
    ) -> Dict[str, str or int or bool or None]:
        """Transform entity to dictionary"""
        return {**{
            "phone": self.phone,
        }, **super().to_dict(only, exclude, with_collections, with_lazy, related_objects)}


class ConditionEntity(EntityEventMixin, db.Entity):
    """
    Base condition entity

    @package        FastyBird:TriggersModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """
    _table_: str = "fb_conditions"

    type = Discriminator(str, column="condition_type")

    condition_id: uuid.UUID = PrimaryKey(uuid.UUID, default=uuid.uuid4, column="condition_id")
    enabled: bool = Required(bool, column="condition_enabled", nullable=False, default=True)
    created_at: datetime.datetime or None = Optional(datetime.datetime, column="created_at", nullable=True)
    updated_at: datetime.datetime or None = Optional(datetime.datetime, column="updated_at", nullable=True)

    trigger: AutomaticTriggerEntity = Required(
        "AutomaticTriggerEntity",
        reverse="conditions",
        column="trigger_id",
        nullable=False,
    )

    # -----------------------------------------------------------------------------

    def to_dict(
        self,
        only: Tuple = None,  # pylint: disable=unused-argument
        exclude: Tuple = None,  # pylint: disable=unused-argument
        with_collections: bool = False,  # pylint: disable=unused-argument
        with_lazy: bool = False,  # pylint: disable=unused-argument
        related_objects: bool = False,  # pylint: disable=unused-argument
    ) -> Dict[str, str or int or bool or None]:
        """Transform entity to dictionary"""
        return {
            "id": self.condition_id.__str__(),
            "type": self.type,
            "enabled": self.enabled,
            "trigger": self.trigger.trigger_id.__str__(),
        }

    # -----------------------------------------------------------------------------

    def before_insert(self) -> None:
        """Before insert entity hook"""
        self.created_at = datetime.datetime.now()

    # -----------------------------------------------------------------------------

    def before_update(self) -> None:
        """Before update entity hook"""
        self.updated_at = datetime.datetime.now()


class PropertyConditionEntity(ConditionEntity):
    """
    Property condition entity

    @package        FastyBird:TriggersModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """
    operator: TriggerConditionOperator = Required(TriggerConditionOperator, column="condition_operator",
                                                  nullable=True)
    operand: str = Required(str, column="condition_operand", max_len=100, nullable=True)

    device: uuid.UUID = Required(uuid.UUID, column="condition_device", nullable=True)

    # -----------------------------------------------------------------------------

    def to_dict(
        self,
        only: Tuple = None,
        exclude: Tuple = None,
        with_collections: bool = False,
        with_lazy: bool = False,
        related_objects: bool = False,
    ) -> Dict[str, str or int or bool or None]:
        """Transform entity to dictionary"""
        return {**{
            "operator": self.operator,
            "operand": self.operand,
            "device": self.device.__str__(),
        }, **super().to_dict(only, exclude, with_collections, with_lazy, related_objects)}


class DevicePropertyConditionEntity(PropertyConditionEntity):
    """
    Device property condition entity

    @package        FastyBird:TriggersModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """
    _discriminator_: str = "device_property"

    device_property: uuid.UUID = Required(uuid.UUID, column="condition_device_property", nullable=True)

    # -----------------------------------------------------------------------------

    def to_dict(
        self,
        only: Tuple = None,
        exclude: Tuple = None,
        with_collections: bool = False,
        with_lazy: bool = False,
        related_objects: bool = False,
    ) -> Dict[str, str or int or bool or None]:
        """Transform entity to dictionary"""
        return {**{
            "property": self.device_property.__str__(),
        }, **super().to_dict(only, exclude, with_collections, with_lazy, related_objects)}


class ChannelPropertyConditionEntity(PropertyConditionEntity):
    """
    Channel property condition entity

    @package        FastyBird:TriggersModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """
    _discriminator_: str = "channel_property"

    channel: uuid.UUID = Required(uuid.UUID, column="condition_channel", nullable=True)
    channel_property: uuid.UUID = Required(uuid.UUID, column="condition_channel_property", nullable=True)

    # -----------------------------------------------------------------------------

    def to_dict(
        self,
        only: Tuple = None,
        exclude: Tuple = None,
        with_collections: bool = False,
        with_lazy: bool = False,
        related_objects: bool = False,
    ) -> Dict[str, str or int or bool or None]:
        """Transform entity to dictionary"""
        return {**{
            "channel": self.channel.__str__(),
            "property": self.channel_property.__str__(),
        }, **super().to_dict(only, exclude, with_collections, with_lazy, related_objects)}


class TimeConditionEntity(ConditionEntity):
    """
    Time property condition entity

    @package        FastyBird:TriggersModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """
    _discriminator_: str = "time"

    time: datetime.timedelta = Required(datetime.timedelta, column="condition_time", nullable=True)
    days: str = Required(str, column="condition_days", max_len=100, nullable=True)

    # -----------------------------------------------------------------------------

    def to_dict(
        self,
        only: Tuple = None,
        exclude: Tuple = None,
        with_collections: bool = False,
        with_lazy: bool = False,
        related_objects: bool = False,
    ) -> Dict[str, str or int or bool or None]:
        """Transform entity to dictionary"""
        return {**{
            "time": self.time,
            "days": self.days,
        }, **super().to_dict(only, exclude, with_collections, with_lazy, related_objects)}


class DateConditionEntity(ConditionEntity):
    """
    Date property condition entity

    @package        FastyBird:TriggersModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """
    _discriminator_: str = "date"

    date: datetime.datetime = Required(datetime.datetime, column="condition_date", nullable=True)

    # -----------------------------------------------------------------------------

    def to_dict(
        self,
        only: Tuple = None,
        exclude: Tuple = None,
        with_collections: bool = False,
        with_lazy: bool = False,
        related_objects: bool = False,
    ) -> Dict[str, str or int or bool or None]:
        """Transform entity to dictionary"""
        return {**{
            "date": self.date,
        }, **super().to_dict(only, exclude, with_collections, with_lazy, related_objects)}


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
    def initialize(self) -> None:
        """Initialize repository by fetching entities from database"""
        items: Dict[str, TriggerItem] = {}

        for trigger in TriggerEntity.select():
            record = TriggerItem(trigger.trigger_id, trigger.enabled)

            items[trigger.trigger_id.__str__()] = record

        self.__items = items

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
    __items: Dict[str, DevicePropertyActionItem or ChannelPropertyActionItem] or None = None

    __iterator_index = 0

    # -----------------------------------------------------------------------------

    def get_by_id(self, action_id: uuid.UUID) -> DevicePropertyActionItem or ChannelPropertyActionItem or None:
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

    def get_all_for_trigger(self, trigger_id: uuid.UUID) -> List[DevicePropertyActionItem or ChannelPropertyActionItem]:
        """Find all actions in cache for provided trigger identifier"""
        if self.__items is None:
            self.initialize()

        actions: List[DevicePropertyActionItem or ChannelPropertyActionItem] = []

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
    def initialize(self) -> None:
        """Initialize repository by fetching entities from database"""
        items: Dict[str, PropertyActionItem] = {}

        for action in ActionEntity.select():
            is_triggered: bool = False

            if isinstance(action, ChannelPropertyActionEntity):
                if (
                    self.__items is not None
                    and action.action_id.__str__() in self.__items
                    and isinstance(self.__items[action.action_id.__str__()], ChannelPropertyActionItem)
                ):
                    is_triggered = self.__items[action.action_id.__str__()].is_triggered

                items[action.action_id.__str__()] = ChannelPropertyActionItem(
                    action_id=action.action_id,
                    trigger_id=action.trigger.trigger_id,
                    enabled=action.enabled,
                    value=action.value,
                    channel_property=action.channel_property,
                    channel=action.channel,
                    device=action.device,
                    is_triggered=is_triggered,
                )

            elif isinstance(action, DevicePropertyActionEntity):
                if (
                    self.__items is not None
                    and action.action_id.__str__() in self.__items
                    and isinstance(self.__items[action.action_id.__str__()], DevicePropertyActionItem)
                ):
                    is_triggered = self.__items[action.action_id.__str__()].is_triggered

                items[action.action_id.__str__()] = DevicePropertyActionItem(
                    action_id=action.action_id,
                    trigger_id=action.trigger.trigger_id,
                    enabled=action.enabled,
                    value=action.value,
                    device_property=action.device_property,
                    device=action.device,
                    is_triggered=is_triggered,
                )

        self.__items = items

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
    def initialize(self) -> None:
        """Initialize repository by fetching entities from database"""
        items: Dict[str, ConditionItem] = {}

        for condition in ConditionEntity.select():
            is_fulfilled: bool = False

            if isinstance(condition, ChannelPropertyConditionEntity):
                if (
                    self.__items is not None
                    and condition.condition_id.__str__() in self.__items
                    and isinstance(self.__items[condition.condition_id.__str__()], ChannelPropertyConditionItem)
                ):
                    is_fulfilled = self.__items[condition.condition_id.__str__()].is_fulfilled

                items[condition.condition_id.__str__()] = ChannelPropertyConditionItem(
                    condition_id=condition.condition_id,
                    trigger_id=condition.trigger.trigger_id,
                    enabled=condition.enabled,
                    operator=condition.operator,
                    operand=condition.operand,
                    channel_property=condition.channel_property,
                    channel=condition.channel,
                    device=condition.device,
                    is_fulfilled=is_fulfilled,
                )

            elif isinstance(condition, DevicePropertyConditionEntity):
                if (
                    self.__items is not None
                    and condition.condition_id.__str__() in self.__items
                    and isinstance(self.__items[condition.condition_id.__str__()], DevicePropertyConditionItem)
                ):
                    is_fulfilled = self.__items[condition.condition_id.__str__()].is_fulfilled

                items[condition.condition_id.__str__()] = DevicePropertyConditionItem(
                    condition_id=condition.condition_id,
                    trigger_id=condition.trigger.trigger_id,
                    enabled=condition.enabled,
                    operator=condition.operator,
                    operand=condition.operand,
                    device_property=condition.device_property,
                    device=condition.device,
                    is_fulfilled=is_fulfilled,
                )

            elif isinstance(condition, TimeConditionEntity):
                items[condition.condition_id.__str__()] = TimeConditionItem(
                    condition_id=condition.condition_id,
                    trigger_id=condition.trigger.trigger_id,
                    enabled=condition.enabled,
                    time=condition.time,
                    days=condition.days,
                )

            elif isinstance(condition, DateConditionEntity):
                items[condition.condition_id.__str__()] = DateConditionItem(
                    condition_id=condition.condition_id,
                    trigger_id=condition.trigger.trigger_id,
                    enabled=condition.enabled,
                    date=condition.date,
                )

        self.__items = items

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


triggers_repository = TriggersRepository()
actions_repository = ActionsRepository()
conditions_repository = ConditionsRepository()
