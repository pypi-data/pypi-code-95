import datetime
import uuid

from sqlalchemy import Column, ForeignKey, DDL, event
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import TIMESTAMP, TEXT, BYTEA, UUID, INTEGER

from .base import Base
from .users import Users


class SwarmHealthStatuses(Base):
    __tablename__ = "swarm_health_statuses"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(TEXT())
    user_id = Column(UUID(as_uuid=True), ForeignKey(Users.id), nullable=False)

    created_at = Column(TIMESTAMP(), default=datetime.datetime.utcnow)
    updated_at = Column(
        TIMESTAMP(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )
    deleted_at = Column(TIMESTAMP(), nullable=True)

    user = relationship(Users, backref="swarm_healths")


class Swarms(Base):
    __tablename__ = "swarms"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    health_status_id = Column(
        UUID(as_uuid=True), ForeignKey(SwarmHealthStatuses.id), nullable=False
    )
    queen_year = Column(INTEGER(), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey(Users.id), nullable=False)

    created_at = Column(TIMESTAMP(), default=datetime.datetime.utcnow)
    updated_at = Column(
        TIMESTAMP(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )
    deleted_at = Column(TIMESTAMP(), nullable=True)

    user = relationship(Users, backref="swarms_healths")
    health = relationship(SwarmHealthStatuses)


func = DDL(
    """
    CREATE FUNCTION check_user_swarms() RETURNS trigger AS $check_user_swarms$
        BEGIN
            IF NEW.user_id NOT IN (SELECT t.user_id FROM swarm_health_statuses as t WHERE t.id = NEW.health_status_id) THEN
                RAISE EXCEPTION 'Different user for swarm_health_statuses';
            END IF;

            RETURN NEW;
        END; $check_user_swarms$ LANGUAGE PLPGSQL
"""
)

trigger = DDL(
    """
    CREATE TRIGGER trigger_user_swarms BEFORE INSERT OR UPDATE ON swarms
        FOR EACH ROW EXECUTE PROCEDURE check_user_swarms();
"""
)

event.listen(Swarms.metadata, "after_create", func.execute_if(dialect="postgresql"))
event.listen(Swarms.metadata, "after_create", trigger.execute_if(dialect="postgresql"))
