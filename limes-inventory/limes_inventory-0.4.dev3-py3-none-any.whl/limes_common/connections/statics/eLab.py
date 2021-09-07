import numpy as np

from limes_common import config
from limes_common.connections import T
from limes_common.connections.http import HttpConnection
from limes_common.models import Model, elab as Models, provider as ProviderModels

class Storages:
    def __init__(self, storages: list[Models.Storage] = None) -> None:
        if storages is None:
            try:
                loaded = np.load(file=config.ELAB_CACHE, allow_pickle=True)
                storages = [Models.Storage.Parse(s) for s in loaded]
            except FileNotFoundError:
                storages = []
        else:
            np.save(file=config.ELAB_CACHE, arr=[s.ToDict() for s in storages])

        S = Models.Storage
        self._byName: dict[str, list[S]] = {}
        self._byParentId: dict[int, list[S]] = {}
        self._byStorageId: dict[int, S] = {}
        self._byLayerId: dict[int, S] = {}

        def addToList(k, v, d:dict):
            similarLayers = d.get(k, [])
            similarLayers.append(v)
            d[k] = similarLayers

        for item in storages:
            item.link = ' %smembers/inventory/browser/?initStorageLayer=%s ' % (config.ELAB_URL, item.storageLayerID)
            addToList(item.name.lower(), item, self._byName)
            addToList(item.parentStorageLayerID, item, self._byParentId)
            self._byStorageId[item.storageID] = item
            self._byLayerId[item.storageLayerID] = item

class ELabConnection(HttpConnection):
    def __init__(self) -> None:
        super().__init__(config.ELAB_API)
        self._token: str = ''
        self._storages = Storages()

    def _makeHeader(self):
        return {'authorization': self._token}

    def SetToken(self, token:str) -> None:
        self._token = token

    def LoggedIn(self) -> bool:
        return self._token != ''

    def GetSchema(self) -> ProviderModels.Schema:
        s = ProviderModels.Schema()
        s.Code = 503
        s.Error = 'please visit https://elab.msl.ubc.ca/docs/api/ for eLab api documentation'
        return s

    def Search(self, query: str) -> ProviderModels.Search.Response:
        samples = self.SearchSamples(query)
        storages = self.SearchStorages(query)
        res = ProviderModels.Search.Response()
        t_samples = str(Models.Sample)
        t_storages = str(Models.Storage)
        def makeHit(x, t):
            hit = ProviderModels.Search.Hit()
            hit.DataType = t
            if x is None: return hit
            hit.Data = [i.ToDict() for i in x]
            return hit
        res.Hits = {
            'samples': makeHit(samples.data, t_samples),
            'storages': makeHit(storages, t_storages)
        }
        res.Code = 200
        return res

    def Login(self, username: str, password: str):
        transaction = Models.Login
        req = transaction.Request()
        req.username = username
        req.password = password
        res = self._makeParseRequest(
            req,
            transaction.Response.Parse,
            transaction.Response()
        )
        if res.Code == 200:
            self.SetToken(res.token)
        return res 

    def SearchSamples(self, query: str):
        query = query.lower()
        transaction = Models.SampleSearch
        req = transaction.Request(query)
        return self._makeParseRequest(
            req,
            transaction.Response.Parse,
            transaction.Response()
        )

    def GetSample(self, sampleID: int):
        transaction = Models.GetSample
        req = transaction.Request(sampleID)
        return self._makeParseRequest(
            req,
            transaction.Response.Parse,
            transaction.Response()
        )

    def ReloadStorages(self):
        transaction = Models.AllStorages
        req = transaction.Request()
        res = self._makeParseRequest(
            req,
            transaction.Response.Parse,
            transaction.Response()
        )
        self._storages = Storages(res.data)
        return res

    def SearchStorages(self, query: str):
        query = query.lower()
        results: list[Models.Storage] = []
        d = self._storages._byName
        for n in d.keys():
            if query in n:
                results += d[n]
        return results
    
    def GetStorage(self, layerID: int):
        # default = Models.Storage()
        default = None
        return self._storages._byLayerId.get(layerID, default)

    def GetFullStoragePath(self, layerID: int) -> list[Models.Storage]:
        layer = self.GetStorage(layerID)
        path = []
        while layer is not None:
            path.append(layer)
            layer = self.GetStorage(layer.parentStorageLayerID)
        return path

    # def _truncateToId(self, id: str) -> str:
    #     return id[-9:] if len(id) > 9 else id

    # def SearchSamplesById(self, strIds: list[str]) -> elab.Sample.ListResponse:
    #     ids = list(self._truncateToId(id) for id in strIds)
    #     query = '' if len(strIds)==0 else '?sampleID=' + reduce(lambda s, id: '%s,%s' % (s, id), ids, '')[1:]
    #     return elab.Sample.ListResponse(self.session.get(
    #         '%s/%s%s' % (self._makeUrl(ELabEndpoint.SAMPLES.Path), 'get', query),
    #         headers=self._getAuthHeader()
    #     ))

    # def SearchSamplesByName(self, name: str) -> elab.Sample.ListResponse:
    #     query = '' if len(name)==0 else '?name=' + reduce(lambda s, id: '%s,%s' % (s, id), [name], '')[1:]
    #     return elab.Sample.ListResponse(self.session.get(
    #         '%s%s' % (self._makeUrl(ELabEndpoint.SAMPLES.Path), query),
    #         headers=self._getAuthHeader()
    #     ))

    # def SearchSamples(self, token: str) -> elab.Sample.ListResponse:
    #     return elab.Sample.ListResponse(self.session.get(
    #         '%s%s%s' % (self._makeUrl(ELabEndpoint.SAMPLES.Path), '?search=', token),
    #         headers=self._getAuthHeader()
    #     ))

    # def GetSample(self, id: str) -> elab.Sample.Response:
    #     id = self._truncateToId(id)
    #     return elab.Sample.Response(self.session.get(
    #         '%s/%s' % (self._makeUrl(ELabEndpoint.SAMPLES.Path), id),
    #         headers=self._getAuthHeader()
    #     ))

    # def GetSampleMeta(self, id: str) -> elab.SampleMeta.Response:
    #     id = self._truncateToId(id)
    #     return elab.SampleMeta.Response(self.session.get(
    #         '%s/%s/meta' % (self._makeUrl(ELabEndpoint.SAMPLES.Path), id),
    #         headers=self._getAuthHeader()
    #     ))

    # def UpdateSampleMeta(self, sampleId: str, metaKey: str, newValue: str) -> elab.SampleMeta.UpdateResponse:
    #     id = self._truncateToId(sampleId)
    #     meta = self.GetSampleMeta(id)
    #     fieldId=0
    #     field = elab.MetaField()
    #     for k, f in meta.Fields.items():
    #         if k == metaKey:
    #             fieldId = f.sampleMetaID
    #             field = f
    #             if field.sampleDataType in ['TEXTAREA']:
    #                 field.value = newValue
    #             else:
    #                 print('cannot update a non text meta field')
    #     return elab.SampleMeta.UpdateResponse(self.session.patch(
    #         '%s/%s/meta/%s' % (self._makeUrl(ELabEndpoint.SAMPLES.Path), id, fieldId),
    #         headers=self._getAuthHeader(),
    #         data=field.ToDict(),
    #     ))