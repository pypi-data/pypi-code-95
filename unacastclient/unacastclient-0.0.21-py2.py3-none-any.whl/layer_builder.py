
from syncer import sync

from unacastclient.unacast.maps.v1 import LayerSpec, Layer as v1_Layer, AddressComponentValueSpec
from .address_component import AddressComponent
from .layer import Layer


class LayerBuilder(object):

    def __init__(self, catalog: 'Catalog', given_id: str):
        self._catalog = catalog
        self.map_operator_service = catalog._client.map_operator_service

        self._given_id = given_id
        self._address_components = []
        self._display_name = None
        self._description = None
        self._feature_display_name = None
        self._feature_description = None
        self._version = None
        self._attribution = None


    def with_display_name(self, display_name: str):
      self._display_name = display_name
      return self

    def with_description(self, description: str):
      self._description = description
      return self

    def with_feature_display_name(self, display_name: str):
      self._feature_display_name = display_name
      return self
    
    def with_feature_description(self, description: str):
      self._feature_description = description
      return self

    def with_version(self, version: str):
      self._version = version
      return self
    
    def with_attribution(self, attribution: str):
      self._attribution = attribution
      return self

    def with_address_component(self, ac: AddressComponent, allow_empty_values: bool = False):
      self._address_components.append(AddressComponentValueSpec(component=ac.component, allow_empty_values=allow_empty_values))
      return self

    def create(self, skip_create_address_component: bool = False) -> Layer:
      res: v1_Layer = sync(
            self.map_operator_service.create_layer(
              given_id=self._given_id, 
              spec=LayerSpec(
                catalog_id=self._catalog._catalog.id,
                address_components=self._address_components,
                feature_display_name=self._feature_display_name,
                feature_description=self._feature_description,
                version=self._version,
                attribution=self._attribution
              ),
              display_name=self._display_name,
              description=self._description,
              skip_address_component=skip_create_address_component
            )
      )
      return Layer(self._catalog, res)
    
    