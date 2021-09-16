import datetime
import uuid

from sqlalchemy import Column, ForeignKey, DDL, event
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import TIMESTAMP, TEXT, BYTEA, UUID

from .base import Base
from .users import Users, Owners
from .apiaries import Apiaries
from .swarms import Swarms


class HiveConditions(Base):
    __tablename__ = "hive_conditions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(TEXT(), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey(Users.id), nullable=False)

    created_at = Column(TIMESTAMP(), default=datetime.datetime.utcnow)
    updated_at = Column(
        TIMESTAMP(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )
    deleted_at = Column(TIMESTAMP(), nullable=True)

    user = relationship(Users, backref="hive_conditions")


class Hives(Base):
    __tablename__ = "hives"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(TEXT(), nullable=False)

    user_id = Column(UUID(as_uuid=True), ForeignKey(Users.id), nullable=False)
    condition_id = Column(
        UUID(as_uuid=True), ForeignKey(HiveConditions.id), nullable=False
    )
    owner_id = Column(UUID(as_uuid=True), ForeignKey(Owners.id), nullable=True)
    swarm_id = Column(UUID(as_uuid=True), ForeignKey(Swarms.id), nullable=True)
    apiary_id = Column(UUID(as_uuid=True), ForeignKey(Apiaries.id), nullable=True)

    created_at = Column(TIMESTAMP(), default=datetime.datetime.utcnow)
    updated_at = Column(
        TIMESTAMP(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )
    deleted_at = Column(TIMESTAMP(), nullable=True)

    user = relationship(Users, backref="hives")
    owner = relationship(Owners, backref="hives")
    swarm = relationship(Swarms, backref=backref("hive", uselist=False))
    apiary = relationship(Apiaries, backref="hives")
    condition = relationship(HiveConditions, backref="hives")


func = DDL(
    """
    CREATE FUNCTION check_user_hives() RETURNS trigger AS $check_user_hives$
        BEGIN
            IF NEW.user_id NOT IN (SELECT t.user_id FROM owners as t WHERE t.id = NEW.owner_id) THEN
                RAISE EXCEPTION 'Different user for owners';
            END IF;

            IF NEW.swarm_id IS NOT NULL AND NEW.user_id NOT IN (SELECT t.user_id FROM swarms as t WHERE t.id = NEW.swarm_id) THEN
                RAISE EXCEPTION 'Different user for swarms';
            END IF;

            IF NEW.apiary_id IS NOT NULL AND NEW.user_id NOT IN (SELECT t.user_id FROM apiaries as t WHERE t.id = NEW.apiary_id) THEN
                RAISE EXCEPTION 'Different user for apiaries';
            END IF;

            IF NEW.user_id NOT IN (SELECT t.user_id FROM hive_conditions as t WHERE t.id = NEW.condition_id) THEN
                RAISE EXCEPTION 'Different user for hive_conditions';
            END IF;

            RETURN NEW;
        END; $check_user_hives$ LANGUAGE PLPGSQL
"""
)

trigger = DDL(
    """
    CREATE TRIGGER trigger_user_hives BEFORE INSERT OR UPDATE ON hives
        FOR EACH ROW EXECUTE PROCEDURE check_user_hives();
"""
)

event.listen(Hives.metadata, "after_create", func.execute_if(dialect="postgresql"))
event.listen(Hives.metadata, "after_create", trigger.execute_if(dialect="postgresql"))
