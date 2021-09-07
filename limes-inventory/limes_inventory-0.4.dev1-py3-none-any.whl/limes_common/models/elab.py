from typing import Union
from limes_common import config
from limes_common.models import Model, provider as Models
from limes_common.models.provider import GenericResponse, Transaction
from limes_common.models.http import GET, POST, PUT

class Endpoints(Models.Endpoints):
    AUTH = 'auth/user'
    SAMPLES = 'samples'
    STORAGE_LAYERS = 'storageLayers'

class ELabRequest(Models.ProviderRequest):
    pass

class ELabResponse(Models.ProviderResponse):
    pass

class User(Model):
    userID: int
    username: str
    email: str
    firstName: str
    lastName: str
    instituteID: int
    primaryGroupID: int
    primarySubGroupID: int
    domain: str
    
class Login(Transaction):
    class Request(ELabRequest):
        username: str
        password: str

        def __init__(self) -> None:
            super().__init__(Endpoints.AUTH, POST)

    class Response(ELabResponse):
        token: str
        user: User

class Authenticate(Transaction):
    class Request(ELabRequest):
        def __init__(self) -> None:
            super().__init__(Endpoints.AUTH, GET)

    class Response(ELabResponse):
        pass

class SampleType(Model):
    sampleTypeID: int
    userID: int
    groupID: int
    name: str

class Sample(Model):
    owner: str
    archived: bool
    sampleID: int
    created: str
    userID: int
    creatorID: int
    storageLayerID: int
    position: int
    seriesID: int
    groupID: int
    sampleTypeID: int
    sampleType: SampleType
    checkedOut: bool
    parentSampleID: int
    name: str
    description: str
    note: str
    link: str

    @classmethod
    def Parse(cls, raw: Union[bytes, str, dict], base: Model=None):
        s = super().Parse(raw, base=base)
        s.link = ' %smembers/inventory/browser/?return=true&sampleID=%s#viewSample ' % (config.ELAB_URL, s.sampleID)
        return s

class SearchHits(ELabResponse):
    recordCount: int
    currentPage: int
    maxRecords: int
    totalRecords: int
    data: list

class SampleSearch(Transaction):
    class Request(ELabRequest):
        def __init__(self, query: str='') -> None:
            super().__init__(Endpoints.SAMPLES, GET, queryParams={'search': query})

    class Response(SearchHits):
        data: list[Sample]

class SampleNameSearch(Transaction):
    class Request(ELabRequest):
        def __init__(self, query: str='') -> None:
            super().__init__(Endpoints.SAMPLES, GET, queryParams={'name': query})

    class Response(SearchHits):
        data: list[Sample]

class GetSample(Transaction):
    class Request(ELabRequest):
        def __init__(self, sampleID: int=0) -> None:
            super().__init__('%s/%s' % (Endpoints.SAMPLES, sampleID), GET)

    class Response(Sample, ELabResponse):
        pass

class Storage(Model):
    storageID: int
    storageLayerID: int
    parentStorageLayerID: int
    storageLayerDefinitionID: int
    position: int
    maxSize: int
    dimension: dict
    barcode: str
    isGrid: bool
    userID: int
    created: str
    name: str
    link: str

class AllStorages(Transaction):
    class Request(ELabRequest):
        def __init__(self) -> None:
            super().__init__(Endpoints.STORAGE_LAYERS, GET)

    class Response(SearchHits):
        data: list[Storage]

# class SampleModel:
#     def __init__(self, data: dict = {}) -> None:
#         self.Name = _tryParse(str, data, 'name', 'None')
#         self.Owner =_tryParse(str, data, 'owner', '')
#         self.TimeCreated =_tryParse(str, data, 'created', '')
#         self.Id =_tryParse(int, data, 'sampleID', 0)
#         self.Barcode =_tryParse(str, data, 'barcode', '')
#         self.Description =_tryParse(str, data, 'description', '')
#         self.ParentId =_tryParse(int, data, 'parent', 0)

# class Sample:
#     class ListResponse(PublicModel):
#         def __init__(self, res: Response) -> None:
#             super().__init__(res)
#             # self.Samples = list(map(lambda raw: SampleModel(raw), self.data))
#             self.Samples = list(map(lambda raw: SampleModel(raw), self.data.get('data', [])))

#     class Response(PublicModel):
#         def __init__(self, res: Response) -> None:
#             super().__init__(res)
#             self.Sample = SampleModel(self.data)


# class MetaField:
#     def __init__(self, data: dict = {}) -> None:
#         T = TypeVar('T')
#         def parse (constr, key):
#             defaults = {
#                 bool: False,
#                 str: '',
#                 int: 0,
#             }
#             return _tryParse(constr, data, key, defaults[constr])
#         self.raw = data
#         self.archived: bool = parse(bool, 'archived')
#         self.sampleMetaID: int = parse(int, 'sampleMetaID')
#         self.sampleDataType: str = parse(str, 'sampleDataType') # todo, make enum
#         self.key: str = parse(str, 'key')
#         self.value: str = parse(str, 'value')
#         self.sampleTypeMetaID: int = parse(int, 'sampleTypeMetaID')
#         self.truncated: bool = parse(bool, 'truncated')

#     def ToDict(self) -> dict:
#         out = self.__dict__.copy()
#         keys = list(out.keys())
#         for k in keys:
#             if k.startswith('_') or k in ['raw']:
#                 del out[k]
#         return out

# class SampleMeta:
#     class Response(PublicModel):
#         def __init__(self, res: Response) -> None:
#             super().__init__(res)
#             self.Fields: dict[str, MetaField] = {}
#             for raw in self.data['data']:
#                 self.Fields[raw['key']] = MetaField(raw)

#     class UpdateResponse(PublicModel):
#         def __init__(self, res: Response) -> None:
#             super().__init__(res)
#             self.Success = self.Code == 204
