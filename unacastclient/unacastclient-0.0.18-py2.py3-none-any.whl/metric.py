import datetime
from collections import defaultdict
from typing import List

import betterproto
from pandas import DataFrame

from unacastclient.unacast.maps.v1 import ComponentKind
from unacastclient.unacast.metric.v1 import Metric as v1_Metric, MetricValue
from .dimension import Dimension
from .filter import Filter
from .layer import Layer


class Metric(object):

    def __init__(self, catalog, metric_value: v1_Metric, f: Filter = Filter()):
        self._catalog = catalog
        self._metric = metric_value
        self._filter = f
        self._layer = metric_value.layer
        self._related_layer = metric_value.related_layer

    @property
    def name(self):
        return self._metric.name

    @property
    def id(self):
        return self._metric.id

    @property
    def layer(self) -> Layer:
        return Layer(self._catalog, self._layer, f=self._filter)

    def dimension(self, dimension: str) -> Dimension:
        dimensions = [d for d in self.list_dimensions() if d.dimension_id == dimension]
        if len(dimensions) != 1:
            raise RuntimeError('Dimension {} not found'.format(dimension))
        dim = dimensions[0]

        return Dimension(self._catalog, dim)

    def list_dimensions(self, print_out: bool = True):
        dimensions = []
        for d in self._metric.spec.dimensions:
            if print_out:
                print(d.dimension_id)
            dimensions.append(d.dimension_id)
        return self._metric.spec.dimensions
    
    def list_dimension_values(self, dimension_id: str,  search_word: str = ''):
        print(self.dimension(dimension_id).search(search_word).values)

    def list_filters(self, print_out: bool = True):
        filters = []
        for a in self.layer.list_address_components():
            # all address component that is not FREE_FORM_UNSPECIFIED can be used as filter
            if a.kind != ComponentKind.FREE_FORM_UNSPECIFIED:
                if print_out:
                    print(a.component)
                filters.append(a.component)
        return filters

    
    def list_filter_values(self, address_component: str, search_word: str):
        print(self.layer.address_component(address_component).search(search_word).values)

    def __str__(self):
        return str(self.to_dict())

    def to_dict(self):
        return self._metric.to_dict(casing=betterproto.Casing.SNAKE)

    def with_filter(self, f: Filter) -> 'Metric':
        return Metric(self._catalog, self._metric, f)

    def report(self):
        return self._catalog._client.metric_report(self._catalog.id, self._metric.id)

    def values(self, include_geo: bool = False) -> DataFrame:
        metric_values: List[MetricValue] = self._catalog.client.search_metric_values(catalog_id=self._catalog.id,
                                                                                     metric_id=self.id,
                                                                                     f=self._filter)
        dataframe_dict = defaultdict(list)
        
        for mv in metric_values:
            dataframe_dict['feature_id'].append(mv.map_feature_v2.feature_id)
            start = mv.observation_period.start
            dataframe_dict['observation_start'].append(datetime.datetime(start.year, start.month, start.day))
            end = mv.observation_period.end
            dataframe_dict['observation_end'].append(datetime.datetime(end.year, end.month, end.day))


            for address_component in mv.map_feature_v2.address_components:
                dataframe_dict[address_component.component + "_id"].append(address_component.value)
                dataframe_dict[address_component.component + "_name"].append(address_component.display_name)
                dataframe_dict[address_component.component + "_short_name"].append(address_component.short_name)

            if mv.related_map_feature:
                for address_component in mv.related_map_feature.address_components:
                    dataframe_dict["related_" + address_component.component + "_id"].append(address_component.value)
                    dataframe_dict["related_" + address_component.component + "_name"].append(address_component.display_name)
                    dataframe_dict["related_" + address_component.component + "_short_name"].append(address_component.short_name)

            for dimension in mv.dimensions:
                dataframe_dict[dimension.dimension_id].append(dimension.display_name)

            dataframe_dict[mv.value.name].append(betterproto.which_one_of(mv.value, "value")[1])


            for supporting_value in mv.supporting_values:
                dataframe_dict[supporting_value.name].append(betterproto.which_one_of(supporting_value, "value")[1])


        df = DataFrame.from_dict(dataframe_dict)
        if include_geo:
            features = self.layer.with_filter(self._filter).features()
            df = df.merge(features[["feature_id", "geo"]], how='inner', on='feature_id')
            
        return df

    def print(self):
        print(f"""
        metric_id: {self._metric.id} \n 
        description: {self.to_dict()['dimensions'][0]['description']} \n 
        cadence: {self.to_dict()['spec']['cadence']} \n 
        filters: {self.list_filters(print_out=False)} \n
        dimensions: {self.list_dimensions()[0]} \n 
        """)