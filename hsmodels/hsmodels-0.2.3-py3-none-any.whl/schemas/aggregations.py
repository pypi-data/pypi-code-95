from datetime import datetime
from typing import List, Union

from pydantic import AnyUrl, Field, root_validator, validator

from hsmodels.schemas.base_models import BaseMetadata
from hsmodels.schemas.enums import AggregationType
from hsmodels.schemas.fields import (
    BandInformation,
    BoxCoverage,
    BoxSpatialReference,
    CellInformation,
    FieldInformation,
    GeometryInformation,
    MultidimensionalBoxSpatialReference,
    MultidimensionalPointSpatialReference,
    PeriodCoverage,
    PointCoverage,
    PointSpatialReference,
    Rights,
    TimeSeriesResult,
    Variable,
)
from hsmodels.schemas.rdf.validators import language_constraint
from hsmodels.schemas.root_validators import parse_abstract, parse_additional_metadata, parse_url, split_coverages
from hsmodels.schemas.validators import (
    parse_multidimensional_spatial_reference,
    parse_spatial_coverage,
    parse_spatial_reference,
    normalize_additional_metadata,
)


class BaseAggregationMetadata(BaseMetadata):

    url: AnyUrl = Field(
        title="Aggregation URL", description="An object containing the URL of the aggregation", allow_mutation=False
    )
    title: str = Field(
        title="Aggregation title", description="A string containing a descriptive title for the aggregation"
    )
    subjects: List[str] = Field(
        default=[],
        title="Subject keywords",
        description="A list of keyword strings expressing the topic of the aggregation",
    )
    language: str = Field(
        default="eng",
        title="Language",
        description="The 3-character string for the language in which the metadata and content are expressed",
    )
    additional_metadata: dict = Field(
        default={},
        title="Extended metadata",
        description="A list of extended metadata elements expressed as key-value pairs",
    )
    spatial_coverage: Union[PointCoverage, BoxCoverage] = Field(
        default=None,
        title="Spatial coverage",
        description="An object containing the geospatial coverage for the aggregation expressed as either a bounding box or point",
    )
    period_coverage: PeriodCoverage = Field(
        default=None,
        title="Temporal coverage",
        description="An object containing the temporal coverage for a aggregation expressed as a date range",
    )
    rights: Rights = Field(
        default=None,
        title="Rights statement",
        description="An object containing information about the rights held in and over the aggregation and the license under which a aggregation is shared",
    )

    _parse_additional_metadata = root_validator(pre=True, allow_reuse=True)(parse_additional_metadata)
    _parse_coverages = root_validator(pre=True, allow_reuse=True)(split_coverages)
    _parse_url = root_validator(pre=True, allow_reuse=True)(parse_url)

    _language_constraint = validator('language', allow_reuse=True)(language_constraint)
    _parse_spatial_coverage = validator("spatial_coverage", allow_reuse=True, pre=True)(parse_spatial_coverage)
    _normalize_additional_metadata = validator("additional_metadata", allow_reuse=True, pre=True)(normalize_additional_metadata)


class GeographicRasterMetadata(BaseAggregationMetadata):
    """
    A class used to represent the metadata associated with a geographic raster aggregation

    A geographic raster aggregation consists of the multiple content files that make up a
    geographic raster dataset to which aggregation-level metadata have been added. Rasters
    may have multiple files and multiple bands and are stored in HydroShare as GeoTIFF files.
    """

    class Config:
        title = 'Geographic Raster Aggregation Metadata'

        schema_config = {'read_only': ['type', 'url'],
                         'dictionary_field': ['additional_metadata']}

    type: AggregationType = Field(
        const=True,
        default=AggregationType.GeographicRasterAggregation,
        title="Aggregation type",
        description="A string expressing the aggregation type from the list of HydroShare aggregation types",
        allow_mutation=False,
    )

    band_information: BandInformation = Field(
        title="Band information",
        description="An object containing information about the bands contained in the raster dataset",
    )
    spatial_reference: Union[BoxSpatialReference, PointSpatialReference] = Field(
        default=None,
        title="Spatial reference",
        description="An object containing spatial reference information for the dataset",
    )
    cell_information: CellInformation = Field(
        title="Cell information", description="An object containing information about the raster grid cells"
    )

    _parse_spatial_reference = validator("spatial_reference", pre=True, allow_reuse=True)(parse_spatial_reference)


class GeographicFeatureMetadata(BaseAggregationMetadata):
    """
    A class used to represent the metadata associated with a geographic feature aggregation

    A geographic feature aggregation consists of the multiple content files that make up an
    ESRI shapefile containing a geographic feature dataset and to which aggregation-level
    metadata have been added.
    """

    class Config:
        title = 'Geographic Feature Aggregation Metadata'

        schema_config = {'read_only': ['type', 'url'],
                         'dictionary_field': ['additional_metadata']}

    type: AggregationType = Field(
        const=True,
        default=AggregationType.GeographicFeatureAggregation,
        title="Aggregation type",
        description="A string expressing the aggregation type from the list of HydroShare aggregation types",
        allow_mutation=False,
    )

    field_information: List[FieldInformation] = Field(
        title="Field information",
        description="A list of objects containing information about the fields in the dataset attribute table",
    )
    geometry_information: GeometryInformation = Field(
        title="Geometry information",
        description="An object containing information about the geometry of the features in the dataset",
    )
    spatial_reference: Union[BoxSpatialReference, PointSpatialReference] = Field(
        default=None,
        title="Spatial reference",
        description="An object containing spatial reference information for the dataset",
    )

    _parse_spatial_reference = validator("spatial_reference", pre=True, allow_reuse=True)(parse_spatial_reference)


class MultidimensionalMetadata(BaseAggregationMetadata):
    """
    A class used to represent the metadata associated with a multidimensional space-time aggregation

    An multidimensional aggregation consists of a Network Common Data Form (NetCDF) file that
    makes up a multidimensional space-time dataset to which aggregation-level metadata have
    been added.
    """

    class Config:
        title = 'Multidimensional Aggregation Metadata'

        schema_config = {'read_only': ['type', 'url'],
                         'dictionary_field': ['additional_metadata']}

    type: AggregationType = Field(
        const=True,
        default=AggregationType.MultidimensionalAggregation,
        title="Aggregation type",
        description="A string expressing the aggregation type from the list of HydroShare aggregation types",
        allow_mutation=False,
    )

    variables: List[Variable] = Field(
        title="Variables",
        description="A list containing information about the variables for which data are stored in the dataset",
    )
    spatial_reference: Union[MultidimensionalBoxSpatialReference, MultidimensionalPointSpatialReference] = Field(
        default=None,
        title="Spatial reference",
        description="An object containing spatial reference information for the dataset",
    )

    _parse_spatial_reference = validator("spatial_reference", pre=True, allow_reuse=True)(
        parse_multidimensional_spatial_reference
    )


class ReferencedTimeSeriesMetadata(BaseAggregationMetadata):
    """
    A class used to represent the metadata associated with a referenced time series aggregation

    A referenced time series aggregation consists of references to specific time series
    datasets hosted on an external web service to which aggregation-level metadata have
    been added.
    """

    class Config:
        title = 'Referenced Time Series Aggregation Metadata'

        schema_config = {'read_only': ['type', 'url'],
                         'dictionary_field': ['additional_metadata']}

    type: AggregationType = Field(
        const=True,
        default=AggregationType.ReferencedTimeSeriesAggregation,
        title="Aggregation type",
        description="A string expressing the aggregation type from the list of HydroShare aggregation types",
        allow_mutation=False,
    )


class FileSetMetadata(BaseAggregationMetadata):
    """
    A class used to represent the metadata associated with a file set aggregation

    A file set aggregation consists of an arbitrary collection of files that are logically
    grouped together as an aggregation and to which aggregation-level metadata have been
    added. There may be any number of files in the aggregation, and files may be of any type.
    """

    class Config:
        title = 'File Set Aggregation Metadata'

        schema_config = {'read_only': ['type', 'url'],
                         'dictionary_field': ['additional_metadata']}

    type: AggregationType = Field(
        const=True,
        default=AggregationType.FileSetAggregation,
        title="Aggregation type",
        description="A string expressing the aggregation type from the list of HydroShare aggregation types",
        allow_mutation=False,
    )


class SingleFileMetadata(BaseAggregationMetadata):
    """
    A class used to represent the metadata associated with a single file aggregation

    A single file aggregation consists of a single content file to which aggregation-level
    metadata have been added.
    """

    class Config:
        title = 'Single File Aggregation Metadata'

        schema_config = {'read_only': ['type', 'url'],
                         'dictionary_field': ['additional_metadata']}

    type: AggregationType = Field(
        const=True,
        default=AggregationType.SingleFileAggregation,
        title="Aggregation type",
        description="A string expressing the aggregation type from the list of HydroShare aggregation types",
        allow_mutation=False,
    )


class TimeSeriesMetadata(BaseAggregationMetadata):
    """
    A class used to represent the metadata associated with a time series aggregation

    A time series aggregation consists of one or more time series datasets to which
    aggregation-level metadata have been added. Time series datasets in HydroShare
    consist of sequences of individual data values that are ordered in time to record
    the changing trend of a certain phenomenon. They are stored in HydroShare using
    ODM2 SQLite database files.
    """

    class Config:
        title = 'Time Series Aggregation Metadata'

        schema_config = {'read_only': ['type', 'url'],
                         'dictionary_field': ['additional_metadata']}

    type: AggregationType = Field(
        const=True,
        default=AggregationType.TimeSeriesAggregation,
        title="Aggregation type",
        description="A string expressing the aggregation type from the list of HydroShare aggregation types",
        allow_mutation=False,
    )

    time_series_results: List[TimeSeriesResult] = Field(
        title="Time series results",
        description="A list of time series results contained within the time series aggregation",
    )

    abstract: str = Field(default=None, title="Abstract", description="A string containing a summary of a aggregation")

    _parse_abstract = root_validator(pre=True, allow_reuse=True)(parse_abstract)
