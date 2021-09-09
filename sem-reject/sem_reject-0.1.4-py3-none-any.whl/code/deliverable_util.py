import os
import pathlib
import shutil
from typing import Text, Any, Type
import random
from typing import Union, Callable, Dict

from deliverable_model.metacontent import MetaContent
from deliverable_model.builder import (
    DeliverableModelBuilder,
    MetadataBuilder,
    ProcessorBuilder,
    ModelBuilder,
)
from deliverable_model.builtin import LookupProcessor
from deliverable_model.builtin.processor import BILUOEncodeProcessor, PadProcessor
from deliverable_model.processor_base import ProcessorBase
from mtnlpmodel.utils.decoder_util import BIOEncodeProcessor

import numpy as np
from typing import Any
from deliverable_model.response import Response
from deliverable_model.converter_base import ConverterBase
from deliverable_model.request import Request


class RequestProcessorForVector(ProcessorBase):
    def preprocess(self, request: Request) -> Request:
        tmp_cls_query_list = []
        tmp_cls_query_list.append(request.query)
        request['data'] = tmp_cls_query_list
        return request

    @classmethod
    def load(cls, *args, **kwargs):
        return cls()


class RequestProcessor(ProcessorBase):
    def preprocess(self, request: Request) -> Request:
        # request['cls_input'] = request.query

        return request

    @classmethod
    def load(cls, *args, **kwargs):
        return cls()


class ConverterForRequest(ConverterBase):
    def call(self, request: Request) -> Any:
        # request['cls_input'] = request.query
        return ([request['data']], {})


class ConverterForResponse_(ConverterBase):
    def __call__(self, response) -> Response:
        response_data = response
        # cls branch
        cls_tmp_response = np.argmax(response_data[1])
        cls_tmp_restorer, cls_result_restorer = [], []
        cls_tmp_restorer.append(cls_tmp_response)
        cls_result_restorer.append(cls_tmp_restorer)
        result = Response([])
        result["CLS"] = cls_result_restorer
        return result


import numpy as np
def softmax(x):
    return np.exp(x)/np.sum(np.exp(x),axis=0)


class ConverterForResponse(ConverterBase):
    def __call__(self, response) -> Response:
        response_data = response
        # cls branch
        cls_tmp_response = np.argmax(response_data[0])
        cls_tmp_score = response_data[0][cls_tmp_response]
        cls_tmp_restorer, cls_result_restorer = [], []
        cls_tmp_restorer.append(cls_tmp_response)
        cls_result_restorer.append(cls_tmp_restorer)
        result = Response([])
        result["CLS"] = cls_result_restorer
        result["CLS_score"] = cls_tmp_score
        return result


def export_as_deliverable_model(
    output_dir,
    tensorflow_saved_model=None,
    converter_for_request = None,
    converter_for_response = None,
    keras_saved_model=None,
    keras_h5_model=None,
    meta_content_id="algorithmId-corpusId-configId-runId",
    lookup_tables = None,
    padding_parameter=None,
    addition_model_dependency=None,
    custom_object_dependency=None,
):
    # check parameters
    assert any(
        [tensorflow_saved_model, keras_saved_model, keras_h5_model]
    ), "one and only one of [tensorflow_saved_model, keras_saved_model, keras_h5_model] must be set up"
    assert (
        sum(
            int(bool(i))
            for i in [tensorflow_saved_model, keras_saved_model, keras_h5_model]
        )
        == 1
    ), "one and only one of [tensorflow_saved_model, keras_saved_model, keras_h5_model] must be set up"

    # default value
    addition_model_dependency = (
        [] if addition_model_dependency is None else addition_model_dependency
    )
    custom_object_dependency = (
        [] if custom_object_dependency is None else custom_object_dependency
    )

    # setup main object
    deliverable_model_builder = DeliverableModelBuilder(output_dir)

    # metadata builder
    metadata_builder = MetadataBuilder()

    meta_content = MetaContent(meta_content_id)

    metadata_builder.set_meta_content(meta_content)

    metadata_builder.save()

    # processor builder

    vocabulary_lookup_table = lookup_tables.get('vocab_lookup', None)
    label_lookup_table = lookup_tables.get('label_lookup', None)

    processor_builder = ProcessorBuilder()

    pad_processor = PadProcessor(padding_parameter=padding_parameter)
    pad_processor_handle = processor_builder.add_processor(pad_processor)

    request_processor = RequestProcessor()
    request_processor_handle = processor_builder.add_processor(request_processor)
    cls_vacab_lookup_processor = LookupProcessor(vocabulary_lookup_table)
    # cls_vacab_lookup_processor.pre_input_key = 'CLS'
    cls_vocab_lookup_processor_handle = processor_builder.add_processor(cls_vacab_lookup_processor)

    label_lookup_processor = LookupProcessor(label_lookup_table, **{"post_input_key": 'CLS', "post_output_key": 'CLS'})
    label_lookup_processor_handle = processor_builder.add_processor(label_lookup_processor)

    # # pre process: encoder[memory text] > lookup[str -> num] > pad[to fixed length]
    processor_builder.add_preprocess(request_processor_handle)
    processor_builder.add_preprocess(cls_vocab_lookup_processor_handle)
    processor_builder.add_preprocess(pad_processor_handle)

    # # post process: lookup[num -> str] > encoder
    processor_builder.add_postprocess(label_lookup_processor_handle)

    processor_builder.save()

    # model builder
    model_builder = ModelBuilder()
    model_builder.append_dependency(addition_model_dependency)
    model_builder.set_custom_object_dependency(custom_object_dependency)

    if converter_for_request:
        model_builder.add_converter_for_request(converter_for_request)

    if converter_for_response:
        model_builder.add_converter_for_response(converter_for_response)

    if tensorflow_saved_model:
        model_builder.add_tensorflow_saved_model(tensorflow_saved_model)
    elif keras_saved_model:
        model_builder.add_keras_saved_model(keras_saved_model)
    else:
        model_builder.add_keras_h5_model(keras_h5_model)

    model_builder.save()

    # compose all the parts
    deliverable_model_builder.add_processor(processor_builder)
    deliverable_model_builder.add_metadata(metadata_builder)
    deliverable_model_builder.add_model(model_builder)

    metadata = deliverable_model_builder.save()

    return metadata


def export_as_vector_deliverable_model(
    output_dir,
    tensorflow_saved_model=None,
    converter_for_request: Union[None, Callable] = None,
    converter_for_response: Union[None, Callable] = None,
    keras_saved_model=None,
    keras_h5_model=None,
    meta_content_id="algorithmId-corpusId-configId-runId",
    lookup_tables: Dict = None,
    padding_parameter=None,
    addition_model_dependency=None,
    custom_object_dependency=None,
):
    # check parameters
    assert any(
        [tensorflow_saved_model, keras_saved_model, keras_h5_model]
    ), "one and only one of [tensorflow_saved_model, keras_saved_model, keras_h5_model] must be set up"
    assert (
        sum(
            int(bool(i))
            for i in [tensorflow_saved_model, keras_saved_model, keras_h5_model]
        )
        == 1
    ), "one and only one of [tensorflow_saved_model, keras_saved_model, keras_h5_model] must be set up"

    # default value
    addition_model_dependency = (
        [] if addition_model_dependency is None else addition_model_dependency
    )
    custom_object_dependency = (
        [] if custom_object_dependency is None else custom_object_dependency
    )

    # setup main object
    deliverable_model_builder = DeliverableModelBuilder(output_dir)

    # metadata builder
    metadata_builder = MetadataBuilder()

    meta_content = MetaContent(meta_content_id)

    metadata_builder.set_meta_content(meta_content)

    metadata_builder.save()

    # processor builder

    vocabulary_lookup_table = lookup_tables.get('vocab_lookup', None)

    processor_builder = ProcessorBuilder()

    pad_processor = PadProcessor(padding_parameter=padding_parameter)
    pad_processor_handle = processor_builder.add_processor(pad_processor)

    request_processor = RequestProcessorForVector()
    request_processor_handle = processor_builder.add_processor(request_processor)
    cls_vacab_lookup_processor = LookupProcessor(vocabulary_lookup_table)
    cls_vocab_lookup_processor_handle = processor_builder.add_processor(cls_vacab_lookup_processor)

    # # pre process: encoder[memory text] > lookup[str -> num] > pad[to fixed length]
    processor_builder.add_preprocess(request_processor_handle)
    processor_builder.add_preprocess(cls_vocab_lookup_processor_handle)
    processor_builder.add_preprocess(pad_processor_handle)

    # # # post process: lookup[num -> str] > encoder
    # processor_builder.add_postprocess(decoder_processor_handle)

    processor_builder.save()

    # model builder
    model_builder = ModelBuilder()
    model_builder.append_dependency(addition_model_dependency)
    model_builder.set_custom_object_dependency(custom_object_dependency)

    if converter_for_request:
        model_builder.add_converter_for_request(converter_for_request)

    if converter_for_response:
        model_builder.add_converter_for_response(converter_for_response)

    if tensorflow_saved_model:
        model_builder.add_tensorflow_saved_model(tensorflow_saved_model)
    elif keras_saved_model:
        model_builder.add_keras_saved_model(keras_saved_model)
    else:
        model_builder.add_keras_h5_model(keras_h5_model)

    model_builder.save()

    # compose all the parts
    deliverable_model_builder.add_processor(processor_builder)
    deliverable_model_builder.add_metadata(metadata_builder)
    deliverable_model_builder.add_model(model_builder)

    metadata = deliverable_model_builder.save()

    return metadata