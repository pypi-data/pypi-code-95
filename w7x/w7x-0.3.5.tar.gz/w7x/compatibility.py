"""
Compoatibility bugfixes
"""
###################################################################################################
# Hack to circumvent bug with dask.delayed and not initialized fields:
# TODO-2: remove this hack once dask has issue #7654 https://github.com/dask/dask/issues/7654
# resolved
import dataclasses

fields = dataclasses.fields


def dataclass_fields(expr):
    """
    Hack to bugfix dask datclass handling in case of init=False and not other setter
    """
    ret = []
    for field in fields(expr):
        if field.init or hasattr(expr, field.name):
            ret.append(field)
    return tuple(ret)


dataclasses.fields = dataclass_fields
import dask.compatibility  # noqa, pylint:disable=wrong-import-position

dask.compatibility.dataclass_fields = dataclass_fields
dataclasses.fields = fields
# hack end|
import dask  # noqa, pylint:disable=wrong-import-position

###################################################################################################
# sqlalchemy optional but declared_attr is required in state
no_sqlalchemy = False
try:
    import sqlalchemy
    from sqlalchemy.orm import declared_attr
except ImportError:
    no_sqlalchemy = True


if no_sqlalchemy:

    class _Dummy:
        """
        Do nothing dummy!
        """

        def __init__(self, *args, **kwargs):
            pass

    class sqlalchemy:  # noqa
        # copied from sqlalchemy

        class Column(_Dummy):
            pass

        class Integer(_Dummy):
            pass

        class String(_Dummy):
            pass

        class UniqueConstraint(_Dummy):
            pass

    class declared_attr(property):  # noqa
        """Mark a class-level method as representing the definition of
        a mapped property or special declarative member name.
        .. note:: @declared_attr is available as
          ``sqlalchemy.util.classproperty`` for SQLAlchemy versions
          0.6.2, 0.6.3, 0.6.4.
        @declared_attr turns the attribute into a scalar-like
        property that can be invoked from the uninstantiated class.
        Declarative treats attributes specifically marked with
        @declared_attr as returning a construct that is specific
        to mapping or declarative table configuration.  The name
        of the attribute is that of what the non-dynamic version
        of the attribute would be.
        @declared_attr is more often than not applicable to mixins,
        to define relationships that are to be applied to different
        implementors of the class::
            class ProvidesUser(object):
                "A mixin that adds a 'user' relationship to classes."
                @declared_attr
                def user(self):
                    return relationship("User")
        It also can be applied to mapped classes, such as to provide
        a "polymorphic" scheme for inheritance::
            class Employee(Base):
                id = Column(Integer, primary_key=True)
                type = Column(String(50), nullable=False)
                @declared_attr
                def __tablename__(cls):
                    return cls.__name__.lower()
                @declared_attr
                def __mapper_args__(cls):
                    if cls.__name__ == 'Employee':
                        return {
                                "polymorphic_on":cls.type,
                                "polymorphic_identity":"Employee"
                        }
                    else:
                        return {"polymorphic_identity":cls.__name__}
        """

        def __init__(self, fget, *arg, **kw):
            super(declared_attr, self).__init__(fget, *arg, **kw)
            self.__doc__ = fget.__doc__

        def __get__(desc, self, cls):
            return desc.fget(cls)
