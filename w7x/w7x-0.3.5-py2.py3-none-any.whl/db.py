"""
Yet immature exploration of automatic storage in a e.g. sqlite db.
"""
import typing
import logging
from sqlalchemy import create_engine
from sqlalchemy import inspect
from sqlalchemy import Column
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
import w7x
from w7x.model import Component


LOGGER = logging.getLogger(__name__)


def get(session, model, **kwargs):
    """Return first instance found."""
    try:
        return session.query(model).filter_by(**kwargs).first()
    except NoResultFound:
        return


def create(session, model, **kwargs):
    """create instance"""
    try:
        instance = model(**kwargs)
        session.add(instance)
        session.flush()
    except Exception as msg:
        LOGGER.error("model:%s, args:%s => msg:%s", model, kwargs, msg)
        session.rollback()
        raise (msg)
    return instance


def provide(session, model, **kwargs):
    """
    Get or create an instance
    Usage:
    class Employee(Base):
        __tablename__ = 'employee'
        id = Column(Integer, primary_key=True)
        name = Column(String, unique=True)

    provide(Employee, name='bob')
    """
    instance = get(model, **kwargs)
    if instance is None:
        instance = create(session, model, **kwargs)
    return instance


def unique_columns(model) -> typing.List[Column]:
    """
    Find the columns with the unique flag.
    """
    uniques = []
    for column in inspect(model).columns:  # Or better Model.__table__.columns  ?
        if column.unique:  # or column.primary_key:
            uniques.append(column)
    return uniques


def unique_together_columns(model) -> typing.List[typing.List[Column]]:
    """
    Find the uninque constraints on multiple columns.

    Returns:
        columns that are unique constrained
    """
    constraints = Component.__table__.constraints
    return [cons.columns for cons in constraints if isinstance(cons, UniqueConstraint)]


if __name__ == "__main__":
    engine = create_engine("sqlite:///foo.db")
    w7x.model.mapper_registry.metadata.create_all(bind=engine)

    component = Component(id=51, custom_id=257)
    for columns in unique_together_columns(Component):
        print([(c.name, getattr(component, c.name)) for c in columns])
    print([getattr(component, c.name) for c in unique_columns(Component)])

    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    # from IPython import embed; embed()
    session.add(component)

    print(session.query(Component).filter_by(id=51).first())

    session.commit()
