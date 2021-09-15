from abc import abstractclassmethod, abstractmethod
from herre.wards.query import get_schema_registry
from herre.wards.base import BaseWard
from typing import Generic, Optional, Type, TypeVar
from pydantic import BaseModel
from pydantic.main import ModelMetaclass

ModelType = TypeVar("ModelType", bound="Model", covariant=True)
ClassType = TypeVar("ClassType", covariant=True)


class BaseModelManager:

    def __init__(self, modelClass: ModelType = None) -> None:
        self.modelClass =  modelClass
        super().__init__()

    def __call__(self, modelClass: ModelType):
        self.modelClass = modelClass
        return self

    @property
    def ward(self) -> BaseWard:
        from herre.wards.registry import get_ward_registry
        return get_ward_registry().get_ward_instance(self.modelClass.Meta.ward)




class SyncModelManager(Generic[ModelType], BaseModelManager):
    """ A Manager to get Models from Packer
    syncrhonisouly

    Args:
        Generic ([type]): [description]

    Returns:
        [type]: [description]
    """


    

    @abstractmethod
    def get(self, id: str, **kwargs) -> ModelType:
        """Fetches an instance of Model on 

        Args:
            id (str): The unque UI

        Returns:
            ModelType: The Model
        """
        raise NotImplementedError("Please use a Subclass")


class AsyncModelManager(Generic[ModelType], BaseModelManager):


    @abstractmethod
    async def get(self, id: str = None, **kwargs) -> ModelType:
        """Fetches an instance of Model on 

        Args:
            id (str, optional): The unque UI

        Returns:
            ModelType: The Model
        """
        raise NotImplementedError("Please use a Subclass")

    
    @abstractmethod
    async def create(self, **kwargs) -> ModelType:
        """Create an instance of Model on the Website 

        Args:
            id (str, optional): The unque UI

        Returns:
            ModelType: The Model
        """
        raise NotImplementedError("Please use a Subclass")



    


class ModelMeta(ModelMetaclass):
    """
    The Model Meta class extends the Pydantic Metaclass and adds in 
    syncrhonous and asynchronous Managers. These Managers allow direct
    interaction with serverside Objects mimicking the Django ORM Scheme
    (https://docs.djangoproject.com/en/3.2/topics/db/queries/) it
    also registeres the Model as a potential serializer.

    Every Class using this metaclass has to subclass pydantic.BaseModel and
    implement a Meta class with the identifier attribute set to a cleartext
    identifier on the arkitekt platform.

    If this identifier does not exist, the serializer can potentially be auto
    registered with the platform according to the apps name

    Args:
        ModelMetaclass ([type]): [description]
    """


    def __new__(mcls, name, bases, attrs):
        slots = set(attrs.pop('__slots__', tuple())) # The slots from: https://github.com/samuelcolvin/pydantic/issues/655#issuecomment-610900376
        for base in bases:
            if hasattr(base, '__slots__'):
                slots.update(base.__slots__)

        if '__dict__' in slots:
            slots.remove('__dict__')
        attrs['__slots__'] = tuple(slots)

        mcls.overriden_manager = attrs.pop("objects") if "objects" in attrs else None
        mcls.overriden_async_manager = attrs.pop("asyncs") if "asyncs" in attrs else None
        return super(ModelMeta, mcls).__new__(mcls, name, bases, attrs)

    @property
    def objects(cls: Type[ModelType]) -> SyncModelManager[ModelType]:
        if not cls.__objects:
            cls.__objects = cls.get_objectsclass()(cls)
        return cls.__objects

    @property
    def asyncs(cls: Type[ModelType]) -> AsyncModelManager[ModelType]:
        if not cls.__asyncs:
            cls.__asyncs = cls.get_asyncclass()(cls)
        return cls.__asyncs


    def __init__(self, name, bases, attrs):
        super(ModelMeta, self).__init__(name, bases, attrs)
        if attrs["__qualname__"] != "Model":
            # This gets allso called for our Baseclass which is abstract
            meta = attrs["Meta"] if "Meta" in attrs else None
            assert meta is not None, f"Please provide a Meta class in your Arnheim Model {name}"

            try:
                if meta.abstract:
                    return
            except:
                pass

            self.__objects = self.overriden_manager(self) if self.overriden_manager else None
            self.__asyncs =  self.overriden_async_manager(self) if self.overriden_async_manager else None
            
            register = getattr(meta, "register", True)
            assert hasattr(meta, "ward"), f"Please specifiy which Ward this Model should use in Meta of  {attrs['__qualname__']}"

            if register:

                from arkitekt.packers.registry import get_packer_registry
                identifier = getattr(meta, "identifier", None)
                overwrite = getattr(meta, "overwrite", False)
                assert identifier is not None, f"Please provide identifier in your Meta class to register the Model {attrs['__qualname__']}, or specifiy register=False"
                get_packer_registry().register_structure(self, overwrite=overwrite)
                get_schema_registry().register_model_for_type_and_ward(name, meta.ward, self)









class Model(BaseModel, metaclass=ModelMeta):
    """Model

    Model is the abstract baseclass of all Serverside Models and provides a Django ORM
    like interface for retrieving data from the Server.

    Implements:
        id (str): Every Model has an id (UUID) that identifies the Server Instance

    Args:
        BaseModel ([type]): [description]
        metaclass ([type], optional): [description]. Defaults to ModelMeta.

    Raises:
        NotImplementedError: [description]
        NotImplementedError: [description]

    Returns:
        [type]: [description]
    """
    id: Optional[str]

    @abstractclassmethod
    def get_objectsclass(cls):
        raise NotImplementedError("Please provide an Implementatoin of SyncModelManager")

    @abstractclassmethod
    def get_asyncclass(cls):
        raise NotImplementedError("Please provide an Implementatoin of SyncModelManager")
