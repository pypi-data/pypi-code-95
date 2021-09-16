import datetime
import uuid

from sqlalchemy import Column, ForeignKey, DDL, event
from sqlalchemy.orm import relationship, column_property
from sqlalchemy.dialects.postgresql import TIMESTAMP, TEXT, BYTEA, UUID

from .base import Base
from .users import Users


class HoneyTypes(Base):
    __tablename__ = "honey_types"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(TEXT())
    user_id = Column(UUID(as_uuid=True), ForeignKey(Users.id), nullable=False)

    created_at = Column(TIMESTAMP(), default=datetime.datetime.utcnow)
    updated_at = Column(
        TIMESTAMP(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )
    deleted_at = Column(TIMESTAMP(), nullable=True)

    user = relationship(Users, backref="honey_types")


class Apiaries(Base):
    __tablename__ = "apiaries"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(TEXT(), nullable=False)
    location = Column(TEXT(), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey(Users.id), nullable=False)
    honey_type_id = Column(
        UUID(as_uuid=True), ForeignKey(HoneyTypes.id), nullable=False
    )

    created_at = Column(TIMESTAMP(), default=datetime.datetime.utcnow)
    updated_at = Column(
        TIMESTAMP(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )
    deleted_at = Column(TIMESTAMP(), nullable=True)

    user = relationship(Users, backref="apiaries")
    honey_type = relationship(HoneyTypes)

    _nb_hives = None

    @property
    def nb_hives(self):
        if self._nb_hives is None:
            self._nb_hives = len(self.hives)  # pylint: disable=no-member
        return self._nb_hives


func = DDL(
    """
    CREATE FUNCTION check_user_apiaries() RETURNS trigger AS $check_user_apiaries$
        BEGIN
            IF NEW.user_id NOT IN (SELECT t.user_id FROM honey_types as t WHERE t.id = NEW.honey_type_id) THEN
                RAISE EXCEPTION 'Different user for honey_type';
            END IF;

            RETURN NEW;
        END; $check_user_apiaries$ LANGUAGE PLPGSQL
"""
)

trigger = DDL(
    """
    CREATE TRIGGER trigger_user_apiaries BEFORE INSERT OR UPDATE ON apiaries
        FOR EACH ROW EXECUTE PROCEDURE check_user_apiaries();
"""
)

event.listen(Apiaries.metadata, "after_create", func.execute_if(dialect="postgresql"))
event.listen(
    Apiaries.metadata, "after_create", trigger.execute_if(dialect="postgresql")
)
