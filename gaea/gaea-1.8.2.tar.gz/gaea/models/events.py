import datetime
import uuid

from sqlalchemy import Column, ForeignKey, DDL, event
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import TIMESTAMP, TEXT, BYTEA, UUID

from .base import Base
from .users import Users
from .apiaries import Apiaries
from .hives import Hives


class EventTypes(Base):
    __tablename__ = "event_types"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(TEXT(), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey(Users.id), nullable=False)

    created_at = Column(TIMESTAMP(), default=datetime.datetime.utcnow)
    updated_at = Column(
        TIMESTAMP(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )
    deleted_at = Column(TIMESTAMP(), nullable=True)

    user = relationship(Users, backref="event_types")


class EventStatuses(Base):
    __tablename__ = "event_statuses"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(TEXT(), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey(Users.id), nullable=False)

    created_at = Column(TIMESTAMP(), default=datetime.datetime.utcnow)
    updated_at = Column(
        TIMESTAMP(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )
    deleted_at = Column(TIMESTAMP(), nullable=True)

    user = relationship(Users, backref="event_statuses")


class Events(Base):
    __tablename__ = "events"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(TEXT(), nullable=False)
    description = Column(TEXT(), nullable=True)
    due_date = Column(TIMESTAMP(), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey(Users.id), nullable=False)
    type_id = Column(UUID(as_uuid=True), ForeignKey(EventTypes.id), nullable=False)
    status_id = Column(UUID(as_uuid=True), ForeignKey(EventStatuses.id), nullable=False)
    hive_id = Column(UUID(as_uuid=True), ForeignKey(Hives.id), nullable=True)

    created_at = Column(TIMESTAMP(), default=datetime.datetime.utcnow)
    updated_at = Column(
        TIMESTAMP(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )
    deleted_at = Column(TIMESTAMP(), nullable=True)

    user = relationship(Users, backref="events")
    type = relationship(EventTypes)
    status = relationship(EventStatuses)
    hive = relationship(Hives, backref="events")


func = DDL(
    """
    CREATE FUNCTION check_user_events() RETURNS trigger AS $check_user_events$
        BEGIN
            IF NEW.user_id NOT IN (SELECT t.user_id FROM event_types as t WHERE t.id = NEW.type_id) THEN
                RAISE EXCEPTION 'Different user for event_types';
            END IF;

            IF NEW.user_id NOT IN (SELECT t.user_id FROM event_statuses as t WHERE t.id = NEW.status_id) THEN
                RAISE EXCEPTION 'Different user for event_statuses';
            END IF;

            IF NEW.hive_id IS NOT NULL AND NEW.user_id NOT IN (SELECT t.user_id FROM hives as t WHERE t.id = NEW.hive_id) THEN
                RAISE EXCEPTION 'Different user for hives';
            END IF;

            RETURN NEW;
        END; $check_user_events$ LANGUAGE PLPGSQL
"""
)

trigger = DDL(
    """
    CREATE TRIGGER trigger_user_events BEFORE INSERT OR UPDATE ON events
        FOR EACH ROW EXECUTE PROCEDURE check_user_events();
"""
)

event.listen(Events.metadata, "after_create", func.execute_if(dialect="postgresql"))
event.listen(Events.metadata, "after_create", trigger.execute_if(dialect="postgresql"))
