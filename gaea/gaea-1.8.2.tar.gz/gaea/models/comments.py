import datetime
import uuid

from sqlalchemy import Column, ForeignKey, DDL, event
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import TIMESTAMP, TEXT, BYTEA, UUID

from .base import Base
from .users import Users
from .swarms import SwarmHealthStatuses, Swarms
from .apiaries import Apiaries
from .hives import Hives, HiveConditions
from .events import Events


class Comments(Base):
    __tablename__ = "comments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    comment = Column(TEXT(), nullable=False)
    date = Column(TIMESTAMP(), nullable=False)
    type = Column(TEXT(), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey(Users.id), nullable=False)
    swarm_id = Column(UUID(as_uuid=True), ForeignKey(Swarms.id), nullable=True)
    hive_id = Column(UUID(as_uuid=True), ForeignKey(Hives.id), nullable=True)
    event_id = Column(UUID(as_uuid=True), ForeignKey(Events.id), nullable=True)

    created_at = Column(TIMESTAMP(), default=datetime.datetime.utcnow)
    updated_at = Column(
        TIMESTAMP(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )
    deleted_at = Column(TIMESTAMP(), nullable=True)

    user = relationship(Users, backref="comments")
    swarm = relationship(Swarms, backref="comments")
    hive = relationship(Hives, backref="comments")
    event = relationship(Events, backref=backref("comment", uselist=False))


func = DDL(
    """
    CREATE FUNCTION check_user_comments() RETURNS trigger AS $check_user_comments$
        BEGIN
            IF new.event_id IS NOT NULL AND NEW.user_id NOT IN (SELECT t.user_id FROM events as t WHERE t.id = NEW.event_id) THEN
                RAISE EXCEPTION 'Different user for eventd';
            END IF;

            IF NEW.swarm_id IS NOT NULL AND NEW.user_id NOT IN (SELECT t.user_id FROM swarms as t WHERE t.id = NEW.swarm_id) THEN
                RAISE EXCEPTION 'Different user for swarms';
            END IF;

            IF NEW.hive_id IS NOT NULL AND NEW.user_id NOT IN (SELECT t.user_id FROM hives as t WHERE t.id = NEW.hive_id) THEN
                RAISE EXCEPTION 'Different user for hives';
            END IF;

            RETURN NEW;
        END; $check_user_comments$ LANGUAGE PLPGSQL
"""
)

trigger = DDL(
    """
    CREATE TRIGGER trigger_user_comments BEFORE INSERT OR UPDATE ON comments
        FOR EACH ROW EXECUTE PROCEDURE check_user_comments();
"""
)

event.listen(Comments.metadata, "after_create", func.execute_if(dialect="postgresql"))
event.listen(
    Comments.metadata, "after_create", trigger.execute_if(dialect="postgresql")
)
