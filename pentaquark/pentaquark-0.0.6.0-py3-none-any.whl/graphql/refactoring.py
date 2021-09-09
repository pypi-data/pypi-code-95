import logging
from itertools import chain
from typing import Union

from ariadne import MutationType, QueryType, make_executable_schema

from pentaquark.constants import START_NODE_ALIAS
from pentaquark.exceptions import PentaQuarkConfigurationError
from pentaquark.graphql import flatten_field_nodes
from pentaquark.models import Node

logger = logging.getLogger(__name__)

GQL_TYPE = "type"
GQL_INPUT_TYPE = "input"


class GraphQLType:
    name: str = ""
    fields: dict = None
    is_input_type: bool = False

    def __init__(self, name=None, fields=None, is_input_type=None):
        if name:
            self.name = name
        if fields:
            self.fields = fields
        if is_input_type is not None:
            self.is_input_type = is_input_type

    def get_name(self):
        return self.name or self.__class__.__name__

    def get_fields(self):
        return self.fields

    def to_def(self):
        return f"""{GQL_INPUT_TYPE if self.is_input_type else GQL_TYPE} {self.get_name()} {{ {
             ' '.join(f'{k}: {v}' for k, v in self.get_fields().items())
            } }}"""


class GraphQLInputType(GraphQLType):
    is_input_type = True


class MutationResultType(GraphQLType):
    fields = {
        "success": "Boolean!"
    }


class ModelType(GraphQLType):
    model: Node = None
    include_fields: list = None
    exclude_fields: list = None
    extra_fields: dict[str, str] = None  # name + type

    def __init__(self, model=None, include_fields=None, exclude_fields=None, extra_fields=None, is_input_type=None):
        super().__init__(is_input_type=is_input_type)
        if model:
            self.model = model
        if include_fields is not None:
            self.include_fields = include_fields
        if extra_fields is not None:
            self.exclude_fields = exclude_fields
        if extra_fields is not None:
            self.extra_fields = extra_fields

    def get_include_fields(self):
        return self.include_fields

    def get_exclude_fields(self):
        return self.exclude_fields

    def _get_model_properties(self, include_fields=None, exclude_fields=None):
        include_fields = include_fields or []
        exclude_fields = exclude_fields or []
        props = []
        for pn, p in chain(self.model._properties.items(), self.model._relationships.items()):
            if pn in exclude_fields:
                continue
            if pn in include_fields or not include_fields:
                props.append(p)
        return props

    def _get_model_fields(self, include_fields=None, exclude_fields=None):
        props = self._get_model_properties(include_fields, exclude_fields)
        return {
            p.name: p.get_dyn_graphql_type()
            for p in props
        }

    def get_fields(self):
        return {
            **self._get_model_fields(self.get_include_fields(), self.get_exclude_fields()),
            **(self.extra_fields or {})
        }


class ModelInputType(ModelType, GraphQLInputType):
    pass


class ModelIdInputType(ModelInputType):
    def get_include_fields(self):
        return [self.model.get_id_property_name()]


class ModelMutationOutputType(ModelType):
    output_sub_type: str = None

    def get_fields(self):
        res = {
            "success": "Boolean!"
        }
        if self.output_sub_type:
            res["obj"] = self.output_sub_type
        return res


class QueryOrMutation:
    name: str = ""
    input_type: dict[str, Union[GraphQLType, str]] = None
    output_type: Union[GraphQLType, str] = ""
    return_many: bool = False

    def __init__(self, name=None, input_type=None, output_type=None, return_many=None):
        super().__init__()
        if name:
            self.name = name
        if input_type is not None:
            self.input_type = input_type
        if output_type is not None:
            self.output_type = output_type
        if return_many is not None:
            self.return_many = return_many

    def get_name(self):
        return self.name

    def get_input_type(self):
        return self.input_type

    def get_output_type(self):
        return self.output_type

    def _get_input_type_as_def(self):
        i = self.get_input_type()
        res = []
        for k, v in i.items():
            if isinstance(v, str):
                res.append(f"{k}: {v}")
                continue
            if issubclass(v, GraphQLType):
                v = v().get_name()
                res.append(f"{k}: {v}")
        return ", ".join(res)

    def _get_output_type_as_def(self):
        o = self.get_output_type()
        if isinstance(o, str):
            return o
        if issubclass(o, GraphQLType):
            return o().get_name()
        raise PentaQuarkConfigurationError("Output type must be a string or a subclass of GraphQLType")

    def to_def(self):
        res = self.get_name()
        input_def = self._get_input_type_as_def()
        if input_def:
            res += f"({input_def})"
        res += f": {self._get_output_type_as_def()}"
        return res
        # return f"{self.get_name()}({self._get_input_type_as_def()}): {self.get_output_type()}"

    def resolve(self, *args, **kwargs):
        return None


class Query(QueryOrMutation):
    pass


class ModelQueryOrMutation(QueryOrMutation):
    model: Node = None

    def __init__(self, model=None, name=None, input_type=None, output_type=None, return_many=False):
        super().__init__(name, input_type, output_type, return_many)
        if model is not None:
            self.model = model

    def get_name(self):
        """

        :return:
        """
        if self.name:
            return self.name
        if self.model:
            return self.model.get_label()
        raise PentaQuarkConfigurationError(
            f"{self.__class__.__name__} must define a name, a model or implement get_name(self)"
        )

    def _model_id_input_type(self):
        return

    def _model_input_type(self):
        if not self.return_many:
            return self._model_id_input_type()

    def get_input_type(self):
        """

        :return:
        """
        if self.input_type:
            return self.input_type
        if self.model:
            return self._model_input_type()
        # we can have no input type for operations with no argument

    def get_output_type(self):
        """

        :return:
        """
        if self.output_type:
            return self.output_type
        if self.model:
            return self.model.to_output_type()
        raise PentaQuarkConfigurationError(
            f"{self.__class__.__name__} must define a name, a model or implement get_output_type(self)"
        )

    def get_node_class(self):
        return self.model


class ModelQuery(ModelQueryOrMutation):
    def resolve(self, obj, info, **kwargs):
        return self.resolve_query(obj, info, **kwargs)

    def resolve_query(self, _, info, **kwargs):
        # print(info.context)   # coming from context_value in graphql_sync
        node_class = self.get_node_class()
        # pagination
        order_by = kwargs.pop("orderBy", None)
        limit = kwargs.pop("limit", None)
        skip = kwargs.pop("skip", None)

        if "filters" in kwargs:
            res = node_class.q.match(**kwargs["filters"])
        else:
            res = node_class.q.match(**kwargs["input"])

        if order_by:
            res = res.order_by(order_by)
        if limit:
            res = res.limit(limit)
        if skip:
            res = res.skip(skip)

        # format return values by parsing graphQL query string
        ret_values = flatten_field_nodes(
            info.field_nodes,
            start=START_NODE_ALIAS,
            field_name=info.field_name,
        )
        # TODO: add graphql_properties requirements here
        # perform db query
        objects = res.returns(*ret_values).all()
        # format result, include graphql_properties if any
        final_result = []
        for o in objects:
            final_result.append(o.to_graphql_return(ret_values, context={}))
        if self.return_many:  # returns a list
            return final_result
        if len(final_result) > 1:
            raise ValueError("More than one value")
        try:
            final_result = final_result[0]
        except IndexError:
            final_result = None
        return final_result


class ModelListQuery(ModelQuery):
    return_many = True


class ModelDetailQuery(ModelQuery):
    return_many = False


class Mutation(QueryOrMutation):
    output_type = MutationResultType


class ModelMutation(ModelQueryOrMutation, Mutation):
    model = None

    def get_match_kwargs(self, **kwargs):
        return {
            self.get_node_class().get_id_property_name(): kwargs["id"]
        }

    def get_node_class(self):
        return self.model


class ModelCreateMutation(ModelMutation):
    def get_name(self):
        return f"Create{self.model.get_label()}"

    # def get_output_type(self):
    #     return {
    #         "success": "Boolean!",
    #         "obj": self.output_type,
    #     }

    def resolve(self, _, info, **kwargs):
        # logger.debug("MUTATION RESOLVER CREATE %s, data=%s", node_class, input_data)
        node_class = self.get_node_class()
        input_data = kwargs["input"]
        obj = node_class.q.create(**input_data)
        return {
            "success": True,
            "obj": obj,
        }


class ModelUpdateMutation(ModelMutation):

    def find_instance(self, _, info, **kwargs):
        node_class = self.get_node_class()
        instance = node_class.q.match(
            **self.get_match_kwargs(**kwargs)
        ).one()
        return instance

    def resolve(self, _, info, **kwargs):
        # logger.debug("MUTATION RESOLVER UPDATE %s, id=%s, data=%s", node_class, pk, input_data)
        instance = self.find_instance(_, info, **kwargs)
        input_data = kwargs.get("input_data")
        for k, v in input_data.items():
            setattr(instance, k, v)
        instance.save()
        return instance


class ModelCreateOrUpdateMutation(ModelMutation):
    pass


class ModelDeleteMutation(ModelMutation):

    def find_instance(self, _, info, **kwargs):
        node_class = self.get_node_class()
        # logger.debug("GRAPHQL: ModelDeleteMutation: try deleting %s, %s", node_class, pk)
        instance = node_class.q.match(
            **self.get_match_kwargs(**kwargs)
        ).one()
        return instance

    def resolve(self, _, info, **kwargs):
        instance = self.find_instance(_, info, **kwargs)
        logger.warning(f"GRAPHQL: ModelDeleteMutation: DELETING {instance}")
        return instance.detach_delete()


class ModelConnectMutation(ModelMutation):
    pass


class ModelMutationSet:
    """
    A collection of mutations for a given model
    """
    model = None
    mutations = {
        "create": {
            "name": "createMovie",
            "input_type": "",
            "output_type": "",
        },
        "update": {},
        "delete": None,
    }

    def make_model_mutations(self):
        mt = MutationType()
        type_defs = ""
        for mutation_type, mutation_data in self.mutations.items():
            if mutation_type == "create":
                m = ModelCreateMutation(
                    model=self.model,
                    input_type=mutation_data.get("input_type"),
                    output_type=mutation_data.get("output_type"),

                )
                type_defs += m.to_def()
                mt.set_field(m.get_name(), m.resolve)
            break
        return mt


class ModelTypeSet:
    """
    A collection of models default types
    """
    pass


def create_schema(types, queries, mutations):
    all_types = []
    type_defs = "scalar UUID \n"
    for t in types:
        type_defs += t().to_def() + "\n"
        # all_types.append(t)
    query_type_def = ""
    if queries:
        qt = QueryType()
        query_type_def = "type Query {"
        for q in queries:
            qi = q()
            qt.set_field(qi.get_name(), qi.resolve)
            query_type_def += qi.to_def() + "\n"
        query_type_def += "} "
        all_types.append(qt)
    else:
        query_type_def = "type Query { dummy: String }"
    mutation_type_def = ""
    if mutations:
        mt = MutationType()
        mutation_type_def = "type Mutation {"
        for m in mutations:
            mi = m()
            mt.set_field(mi.get_name(), mi.resolve)
            mutation_type_def += mi.to_def()
        mutation_type_def += "}"
        all_types.append(mt)
    print(type_defs, query_type_def, mutation_type_def)
    return make_executable_schema(
        type_defs + query_type_def + mutation_type_def,
        *all_types,
    )
