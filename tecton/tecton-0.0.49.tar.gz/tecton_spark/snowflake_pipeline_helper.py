from typing import *

from tecton_proto.args.new_transformation_pb2 import NewTransformationArgs
from tecton_proto.args.new_transformation_pb2 import TransformationMode
from tecton_proto.args.pipeline_pb2 import DataSourceNode
from tecton_proto.args.pipeline_pb2 import Input as InputProto
from tecton_proto.args.pipeline_pb2 import Pipeline
from tecton_proto.args.pipeline_pb2 import PipelineNode
from tecton_proto.args.pipeline_pb2 import TransformationNode
from tecton_proto.data.new_transformation_pb2 import NewTransformation
from tecton_proto.data.virtual_data_source_pb2 import VirtualDataSource
from tecton_spark import function_serialization
from tecton_spark.id_helper import IdHelper
from tecton_spark.pipeline_helper import constant_node_to_value
from tecton_spark.pipeline_helper import CONSTANT_TYPE
from tecton_spark.pipeline_helper import get_keyword_inputs
from tecton_spark.pipeline_helper import get_transformation_name
from tecton_spark.pipeline_helper import positional_inputs
from tecton_spark.pipeline_helper import transformation_type_checker


def pipeline_to_sql_string(
    pipeline: Pipeline,
    virtual_data_sources: List[VirtualDataSource],
    transformations: List[NewTransformation],
) -> str:
    return _PipelineBuilder(
        pipeline,
        virtual_data_sources,
        transformations,
    ).get_sql_string()


# This class is for Snowflake pipelines
class _PipelineBuilder:
    # The value of internal nodes in the tree
    _VALUE_TYPE = Union[str, CONSTANT_TYPE]

    def __init__(
        self,
        pipeline: Pipeline,
        virtual_data_sources: List[VirtualDataSource],
        # we only use mode and name from these
        transformations: Union[List[NewTransformation], List[NewTransformationArgs]],
    ):
        self._pipeline = pipeline
        self._id_to_vds = {IdHelper.to_string(vds.virtual_data_source_id): vds for vds in virtual_data_sources}
        self._id_to_transformation = {IdHelper.to_string(t.transformation_id): t for t in transformations}

    def get_sql_string(self) -> str:
        sql_str = self._node_to_value(self._pipeline.root)
        assert isinstance(sql_str, str)
        return sql_str

    def _node_to_value(self, pipeline_node: PipelineNode) -> _VALUE_TYPE:
        if pipeline_node.HasField("transformation_node"):
            return self._transformation_node_to_sql_str(pipeline_node.transformation_node)
        elif pipeline_node.HasField("data_source_node"):
            return self._data_source_node_to_sql_str(pipeline_node.data_source_node)
        elif pipeline_node.HasField("constant_node"):
            return constant_node_to_value(pipeline_node.constant_node)
        elif pipeline_node.HasField("materialization_context_node"):
            # TODO(TEC-5905): Need to figure out how to support this later
            raise ValueError("MaterializationContext is not supported in Snowflake SQL pipelines")
        elif pipeline_node.HasField("request_data_source_node"):
            raise ValueError("RequestDataSource is not supported in Snowflake SQL pipelines")
        elif pipeline_node.HasField("feature_view_node"):
            raise ValueError("Dependent FeatureViews are not supported in Snowflake SQL pipelines")
        else:
            raise KeyError(f"Unknown PipelineNode type: {pipeline_node}")

    def _data_source_node_to_sql_str(self, data_source_node: DataSourceNode) -> str:
        """Creates a sql string from a VDS and time parameters."""
        vds = self._id_to_vds[IdHelper.to_string(data_source_node.virtual_data_source_id)]
        # TODO(TEC-5906): Applies time window on the data source
        return self._get_vds_sql_str(vds)

    def _get_vds_sql_str(self, vds: VirtualDataSource) -> str:
        # TODO(TEC-5907): Supports other types of data source
        if vds.HasField("batch_data_source"):
            batch_data_source = vds.batch_data_source
            # TODO(TEC-5907): Supports other types of batch data source
            if batch_data_source.HasField("snowflake"):
                snowflake_args = batch_data_source.snowflake.snowflakeArgs
                if snowflake_args.HasField("table"):
                    # Makes sure we have all the info for the table
                    assert snowflake_args.HasField("database")
                    assert snowflake_args.HasField("schema")
                    sql_str = f"{snowflake_args.database}.{snowflake_args.schema}.{snowflake_args.table}"
                else:
                    raise ValueError(f"Snowflake SQL pipeline does not support query as a batch data source")
            else:
                raise ValueError(f"Snowflake SQL pipeline does not support batch data source: {vds.batch_data_source}")
        else:
            raise ValueError("Snowflake SQL pipeline only supports batch data source")
        return sql_str

    def _transformation_node_to_sql_str(self, transformation_node: TransformationNode) -> str:
        """Recursively translates inputs to values and then passes them to the transformation."""
        args: List[_VALUE_TYPE] = []
        kwargs = {}
        for transformation_input in transformation_node.inputs:
            node_value = self._node_to_value(transformation_input.node)
            if transformation_input.HasField("arg_index"):
                assert len(args) == transformation_input.arg_index
                args.append(node_value)
            elif transformation_input.HasField("arg_name"):
                kwargs[transformation_input.arg_name] = node_value
            else:
                raise KeyError(f"Unknown argument type for Input node: {transformation_input}")

        return self._apply_transformation_function(transformation_node, args, kwargs)

    def _apply_transformation_function(self, transformation_node, args, kwargs) -> str:
        """For the given transformation node, returns the corresponding sql string."""
        transformation = self._id_to_transformation[IdHelper.to_string(transformation_node.transformation_id)]
        user_function = function_serialization.from_proto(transformation.user_function)
        transformation_name = get_transformation_name(transformation)

        if transformation.transformation_mode == TransformationMode.TRANSFORMATION_MODE_SNOWFLAKE_SQL:
            return self._wrap_sql_function(transformation_node, user_function)(*args, **kwargs)
        else:
            raise KeyError(
                f"Invalid transformation mode: {transformation.transformation_mode} for a Snowflake SQL pipeline"
            )

    def _wrap_sql_function(
        self, transformation_node: TransformationNode, user_function: Callable[..., str]
    ) -> Callable[..., str]:
        def wrapped(*args, **kwargs):
            wrapped_args = []
            for arg, node_input in zip(args, positional_inputs(transformation_node)):
                wrapped_args.append(self._wrap_node_inputvalue(node_input, arg))
            keyword_inputs = get_keyword_inputs(transformation_node)
            wrapped_kwargs = {}
            for k, v in kwargs.items():
                node_input = keyword_inputs[k]
                wrapped_kwargs[k] = self._wrap_node_inputvalue(node_input, v)
            sql_string = user_function(*wrapped_args, **wrapped_kwargs)
            transformation_name = get_transformation_name(
                self._id_to_transformation[IdHelper.to_string(transformation_node.transformation_id)]
            )
            transformation_type_checker(transformation_name, sql_string, "snowflake_sql", self._possible_modes())
            return sql_string

        return wrapped

    def _wrap_node_inputvalue(self, node_input, value: _VALUE_TYPE) -> Optional[Union[InputProto, CONSTANT_TYPE]]:
        if node_input.node.HasField("constant_node"):
            assert (
                isinstance(value, str)
                or isinstance(value, int)
                or isinstance(value, float)
                or isinstance(value, bool)
                or value is None
            )
            return value
        else:
            # This should be a sql string already, we need to return this with a bracket wrapping it
            # The current implementation will add a round bracket () to all subquery
            assert isinstance(value, str)
            return f"({value})"

    def _possible_modes(self):
        return ["snowflake_sql", "pipeline"]
