"""
Implementation of the base classes of all data models
"""
import typing
import re
import abc
import inspect

import rna
from rna.pattern.composite import Component
from rna.pattern.link import Linker
from rna.polymorphism import Storable
from w7x.switches import exposed

from w7x.merge import merge_dataclasses
import w7x.lib.dataclasses as dataclasses
from w7x.compatibility import dask
from w7x.compatibility import declared_attr
from dask.delayed import Delayed  # pylint:disable=wrong-import-order


@dataclasses.dataclass
class Entry:
    """
    Sql database entry using dataclass fields
    Note:
        see https://docs.sqlalchemy.org/en/14/orm/mapping_styles.html#orm-declarative-dataclasses
    """

    @declared_attr
    def __tablename__(cls):  # pylint:disable=no-self-argument
        return cls.__name__.lower()  # pylint:disable=no-member

    __sa_dataclass_metadata_key__ = "sa"
    # TODO-2: switch pk and id (NamedElement) and id -> mm_id etc
    # TODO-2: fix sqlalchemy-dask conflict
    # pk: int = dataclasses.field(
    #     init=False,
    #     repr=False,
    #     metadata={
    #         "sa": Column(Integer, primary_key=True),
    #         "merged": lambda x: None,
    #     },
    # )


# pylint:disable=abstract-method
class StateComponent(Component, Storable, Entry, Linker):
    """
    Attributes:
        PARENTS: indicating the model path of this component.

    """

    PARENT_TYPE: typing.Type = None  # Carefull, is set to "State" later!

    @Component.parent.setter
    def parent(self, parent):
        # pylint:disable=isinstance-second-argument-not-valid-type
        if parent is None:
            # remove
            pass
        elif self.PARENT_TYPE is not None and not parent.origin() is self.PARENT_TYPE:
            raise ValueError(
                f"Incorrect parent type. {self} is child of {self.PARENT_TYPE}"
                f" but was added to {type(parent)}"
            )
        self._parent = parent

    @classmethod
    def path_from_parent(cls, parent_type, _path=None) -> typing.Tuple[typing.Type]:
        """
        Recursively appends to _path the PARENT_TYPE

        Returns:
            path from the parent_type, empty if not found
        """
        if _path is None:
            _path = (cls,)

        if cls.PARENT_TYPE is None:
            return _path
        _path = (cls.PARENT_TYPE,) + _path
        return cls.PARENT_TYPE.path_from_parent(parent_type, _path=_path)

    @classmethod
    def merged(cls, *instances, **kwargs):
        """
        Merge the instances into a new object, considereing fields
        """
        obj = merge_dataclasses(*instances, cls=cls, **kwargs)
        return obj

    ATTRIBUTE_NAME: typing.ClassVar[str] = None

    @classmethod
    def attribute_name(cls) -> str:
        """
        snake case attribute name parsed from class name.

        Examples:
            Returns self.ATTRIBUTE_NAME
            >>> from w7x import StateComponent, StateLeaf, StateComposite
            >>> class AnAttribute(StateComponent):
            ...     ATTRIBUTE_NAME = 'alias'
            >>> AnAttribute.attribute_name()
            'alias'

            Fall back to snake case of class name. This is the usual case and works for all
            STATE_COMPONENT_BASES.
            >>> class MyAttribute(StateComponent):
            ...     pass
            >>> MyAttribute.attribute_name()
            'my_attribute'

            >>> class MyAttribute(StateComposite):
            ...     pass
            >>> MyAttribute.attribute_name()
            'my_attribute'

            >>> class MyAttribute(StateLeaf):
            ...     pass
            >>> MyAttribute.attribute_name()
            'my_attribute'

            Sub-derived classes still return the "origin" attribute_name
            >>> class MySpecialAttribute(MyAttribute):
            ...     pass
            >>> MySpecialAttribute.attribute_name()
            'my_attribute'

        """
        if cls.ATTRIBUTE_NAME is None:
            cls.ATTRIBUTE_NAME = re.sub(
                r"(?<!^)(?=[A-Z])", "_", cls.origin().__name__
            ).lower()
        return cls.ATTRIBUTE_NAME

    @classmethod
    def _attribute_parents(cls) -> typing.Tuple[type]:
        """
        Recursively loop through bases of cls until it is the Base class and return the list.
        """
        crrt_cls = cls
        chain = tuple([])
        while crrt_cls not in STATE_COMPONENT_BASES:
            # Infinity loop not possible because you derive from StateComponent or are the same
            for base in crrt_cls.__bases__:
                if issubclass(base, STATE_COMPONENT_BASES):
                    crrt_cls = base  # break condition for while
                    if crrt_cls not in STATE_COMPONENT_BASES:
                        chain += (crrt_cls,)
                    break
        return chain

    @classmethod
    def origin(cls):
        """
        Returns:
            StateComponent: first parent base class directly deriving from StateComponent

        Examples:
            >>> import w7x

            Subclass returns origin
            >>> w7x.config.Assemblies.Pfcs.origin()
            <class 'w7x.model.Assembly'>

            Origin gives itself
            >>> w7x.model.Assembly.origin()
            <class 'w7x.model.Assembly'>

            Instance returns type properly
            >>> w7x.model.Assembly().origin()
            <class 'w7x.model.Assembly'>

            Pure State returns None (although deriving from Composite)
            >>> assert w7x.State().origin() is w7x.State
        """
        base_attributes = cls._attribute_parents()
        if len(base_attributes) == 0:
            # not subclassed
            return cls
        return base_attributes[-1]

    def __getstate__(self):
        """
        Required for pickling
        """
        return self.__dict__

    def __setstate__(self, d):
        """
        Required for pickling
        """
        self.__dict__.update(d)


# pylint:disable=inherit-non-class
@dataclasses.dataclass
class StateComposite(StateComponent.Composite):
    """
    _children can be made an alias for a field with the DataclassPropertyAliaser
    """

    @StateComponent.parent.setter  # pylint:disable=no-member
    def parent(self, parent):
        if (
            not parent.origin() is self.PARENT_TYPE
            and not self.origin() is parent.origin()
        ):  # also allow composite pattern
            raise ValueError(
                f"Incorrect parent type. {self} is child of {self.PARENT_TYPE}"
                f" but was added to {type(parent)}"
            )
        self._parent = parent

    @classmethod
    def merged(cls, *instances, **kwargs):
        """
        Merge fields and children
        """
        obj = merge_dataclasses(*instances, cls=cls, **kwargs)
        return obj


# pylint:disable=inherit-non-class,too-few-public-methods
class StateLeaf(StateComponent.Leaf):
    """
    Leafs are at the cottom of containers. If in doubt, these should be used as the base of your
    model.
    """


class DefaultFlag(abc.ABC):
    """
    This flag is used to
    """

    @abc.abstractmethod
    def attribute_name(self):
        """
        Name of the attribute
        """

    @abc.abstractmethod
    def __call__(self):
        """
        Determine what to do on call time. Often flags trow specific errors here
        """


# pylint:disable=inherit-non-class
@dataclasses.dataclass
class State(
    StateComponent.Composite, dask.base.DaskMethodsMixin, rna.polymorphism.Storable
):
    """
    A state is a collection of state attributes. This works similar to a dictionary except that
    state attributes can be set without a key. The key is autogenerated from
    StateComponent.attribute_name().

    Args:
        *args: added as children

    Attributes:
        _attributes (dict): holding the attributes by attribute.attribute_name key

    Examples:
        >>> import w7x
        >>> state = w7x.core.State(
        ...     w7x.model.CoilSet(),
        ...     w7x.model.Assembly(),
        ... )
        >>> assert list(state.keys()) == ['coil_set', 'assembly']
    """

    PARENT_TYPE = None

    attributes: StateComponent = dataclasses.children_alias(default_factory=lambda: [])

    @classmethod
    def origin(cls):
        return State

    def __init__(self, *children, attributes=None):
        super().__init__()
        if attributes is not None:
            if children:
                raise ValueError(
                    "Conflict in arguments. Either pass children or attributes."
                )
            children = attributes
        for child in children:
            self.add(child)

    def keys(self) -> list:
        """
        Returns:
            list of attribute names that are accessible also on getattr level
        """
        return [child.attribute_name() for child in self._children]

    def __getattr__(self, name):
        """
        Forward to state attributes
        """
        # if name == 'pk':
        #     return None  # hack, see entry
        if "_children" in self.__dict__:
            children = self._children
        else:
            # prevent recursion at unpickling time
            children = []
        for child in children:
            if child.attribute_name() == name:
                return child
        raise AttributeError(
            "'{self.__class__.__name__}' object has no attribute '{name}'".format(
                **locals()
            )
        )

    def __setattr__(self, name, value):
        if isinstance(value, StateComponent):
            if name != value.attribute_name():
                raise ValueError(f"Trying to set attribute {value} with name {name}")
            for child in self._children:
                if child.attribute_name() == value.attribute_name():
                    self.remove(child)
                    self.add(value)
                    break
            else:
                self.add(value)
        else:
            super().__setattr__(name, value)

    @classmethod
    def merged(cls, *components: StateComponent) -> "State":
        """
        Merge a state and multiple StateComponents without copying the state if passed.
        Same logic as constructor just with state mutation

        Args:
            *args: state to mutate/copy and or attributes to update the state with
            copy: switches the behaviour from mutating the passed state to returning a copy

        Examples:
            >>> import w7x

            Build a new state from StateComponent
            >>> state = w7x.State.merged(
            ...     w7x.config.CoilGroups.DeformedPlanar()
            ... )
            >>> assert state.has(w7x.model.CoilSet)

            Add to an existing state but do not mutate the state, instead return a shallow copy
            >>> state_original = state
            >>> equilibrium = w7x.model.Equilibrium()
            >>> state =  w7x.State.merged(state, equilibrium)
            >>> assert state.has(w7x.model.CoilSet)
            >>> assert state.has(w7x.model.Equilibrium)
            >>> assert state is not state_original

            Updating an existing state attribute has the following priorities:
            1) If the fields of the two attributes are mutually exclusive (only "None" entries are
            differing), we have no conflict:
            >>> state = w7x.State.merged(
            ...     state,
            ...     w7x.model.Equilibrium(plasma_volume=30.),
            ...     w7x.model.Equilibrium(kinetic_energy=42.),
            ... )
            >>> assert state.equilibrium.plasma_volume == 30.
            >>> assert state.equilibrium.kinetic_energy == 42.
        """
        if any([isinstance(c, Delayed) for c in components]):
            with exposed(True):
                return dask.delayed(cls.merged)(*components)

        # deconstruct all passed states and put children into attributes in the order given
        attributes = []
        for component in components:
            if isinstance(component, State):
                # pylint:disable=protected-access
                attributes.extend(component._children)
            else:
                attributes.append(component)

        # build a new state and fill with the deconstructed children. Merge similar objects
        state = cls()
        while attributes:
            # pop first
            comp = attributes.pop(0)
            name = comp.attribute_name()

            # find other objects of that kind
            indices = []
            same_attributes = []
            for i, attr in enumerate(attributes):
                if attr.attribute_name() == name:
                    same_attributes.append(attr)
                    indices.append(i)

            # merge them
            merge = type(comp).merged(comp, *same_attributes)
            state.add(merge)

            # pop them from the list
            for i in reversed(indices):
                del attributes[i]

        return state

    def has(self, state_attribute_cls: "StateComponent", subclass: bool = True) -> bool:
        """
        Examples:
            >>> import w7x
            >>> coil_set = w7x.config.CoilSets.Deformed()
            >>> assemblies = w7x.config.Assemblies.Pfcs()
            >>> state = w7x.core.State(coil_set, assemblies)
            >>> assert state.has(w7x.model.CoilSet)
            >>> assert state.has(w7x.model.Assembly)

        Returns:
            wheter the state has an attribute of the required type

        Args:
            state_attribute_cls: Does the state have an attribute according to this?
            *fields: attributes of the StateComponent that should be set and not None
            subclass: if False, you have to pass the root attribute for a check
        """
        if subclass:
            state_attribute_cls = state_attribute_cls.origin()
        else:
            assert state_attribute_cls.origin() is state_attribute_cls
        return state_attribute_cls.attribute_name() in self.keys()

    def require(
        self, state_attribute_cls: typing.Type["StateComponent"]
    ) -> "StateComponent":
        """
        Demand a state attribute in the state.
        Throws exception if state_attribute not present
        """
        if not self.has(state_attribute_cls):
            raise ValueError(
                f"State requires attribute {state_attribute_cls}"
                "with name {state_attribute_cls.attribute_name()}"
            )
        return getattr(self, state_attribute_cls.attribute_name())

    def provide(
        self, state_attribute_cls: typing.Type["StateComponent"], **kwargs
    ) -> "StateComponent":
        """
        Check if state attribute is part of the state. If so, return it, else, instantiate one.

        Args:
            state_attribute_cls: class of state attribute
            **kwargs: used to set values to the StateComponent or initilaize it
        """
        if not self.has(state_attribute_cls):
            att = state_attribute_cls(**kwargs)
            self.set(att)
        elif kwargs:
            att = self.require(state_attribute_cls)
            for key, val in kwargs.items():
                setattr(att, key, val)
        return att

    def set(self, attr: typing.Union[typing.Type["StateComponent"], "StateComponent"]):
        """
        Set a state attribute
        """
        if isinstance(attr, StateComponent):
            value = attr
        else:
            assert issubclass(attr, StateComponent), "Invalid attr"
            value = attr()
        self.add(value)

    def set_default(
        self,
        attr: typing.Union[typing.Type["StateComponent"], "StateComponent", str],
        value=None,
    ) -> bool:
        """
        Pass an instantiating method to spare the cost for instantiation

        Returns:
            True if value has been updated, False if nothing has been done
        """
        default_method = None
        if isinstance(attr, StateComponent):
            attr_name = attr.attribute_name()
            value = attr
        elif isinstance(attr, str):
            attr_name = attr
        elif isinstance(attr, DefaultFlag):
            attr_name = attr.attribute_name()
            default_method = attr.__call__
        elif inspect.isclass(attr) and issubclass(attr, StateComponent):
            attr_name = attr.attribute_name()
            default_method = attr  # use the StateComponent default constructor
        else:
            raise TypeError(f"Instance of StateComponent expected. Got {attr}.")

        if not hasattr(self, attr_name) or getattr(self, attr_name) is None:
            if default_method is not None:
                value = default_method()
            setattr(self, attr_name, value)
            return True
        return False

    def __repr__(self):
        return f"{self.__class__.__name__} object with keys {self.keys()}"


StateComponent.PARENT_TYPE = State
STATE_COMPONENT_BASES = (StateComponent, StateLeaf, StateComposite)


if __name__ == "__main__":
    pass
