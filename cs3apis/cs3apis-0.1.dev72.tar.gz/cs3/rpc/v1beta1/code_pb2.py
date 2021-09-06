# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: cs3/rpc/v1beta1/code.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='cs3/rpc/v1beta1/code.proto',
  package='cs3.rpc.v1beta1',
  syntax='proto3',
  serialized_options=b'\n\023com.cs3.rpc.v1beta1B\tCodeProtoP\001Z\nrpcv1beta1\242\002\003CRX\252\002\017Cs3.Rpc.V1Beta1\312\002\017Cs3\\Rpc\\V1Beta1',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x1a\x63s3/rpc/v1beta1/code.proto\x12\x0f\x63s3.rpc.v1beta1*\xd3\x03\n\x04\x43ode\x12\x10\n\x0c\x43ODE_INVALID\x10\x00\x12\x0b\n\x07\x43ODE_OK\x10\x01\x12\x12\n\x0e\x43ODE_CANCELLED\x10\x02\x12\x10\n\x0c\x43ODE_UNKNOWN\x10\x03\x12\x19\n\x15\x43ODE_INVALID_ARGUMENT\x10\x04\x12\x1a\n\x16\x43ODE_DEADLINE_EXCEEDED\x10\x05\x12\x12\n\x0e\x43ODE_NOT_FOUND\x10\x06\x12\x17\n\x13\x43ODE_ALREADY_EXISTS\x10\x07\x12\x1a\n\x16\x43ODE_PERMISSION_DENIED\x10\x08\x12\x18\n\x14\x43ODE_UNAUTHENTICATED\x10\t\x12\x1b\n\x17\x43ODE_RESOURCE_EXHAUSTED\x10\n\x12\x1c\n\x18\x43ODE_FAILED_PRECONDITION\x10\x0b\x12\x10\n\x0c\x43ODE_ABORTED\x10\x0c\x12\x15\n\x11\x43ODE_OUT_OF_RANGE\x10\r\x12\x16\n\x12\x43ODE_UNIMPLEMENTED\x10\x0e\x12\x11\n\rCODE_INTERNAL\x10\x0f\x12\x14\n\x10\x43ODE_UNAVAILABLE\x10\x10\x12\x12\n\x0e\x43ODE_DATA_LOSS\x10\x11\x12\x14\n\x10\x43ODE_REDIRECTION\x10\x12\x12\x1d\n\x19\x43ODE_INSUFFICIENT_STORAGE\x10\x13\x42X\n\x13\x63om.cs3.rpc.v1beta1B\tCodeProtoP\x01Z\nrpcv1beta1\xa2\x02\x03\x43RX\xaa\x02\x0f\x43s3.Rpc.V1Beta1\xca\x02\x0f\x43s3\\Rpc\\V1Beta1b\x06proto3'
)

_CODE = _descriptor.EnumDescriptor(
  name='Code',
  full_name='cs3.rpc.v1beta1.Code',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='CODE_INVALID', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='CODE_OK', index=1, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='CODE_CANCELLED', index=2, number=2,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='CODE_UNKNOWN', index=3, number=3,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='CODE_INVALID_ARGUMENT', index=4, number=4,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='CODE_DEADLINE_EXCEEDED', index=5, number=5,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='CODE_NOT_FOUND', index=6, number=6,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='CODE_ALREADY_EXISTS', index=7, number=7,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='CODE_PERMISSION_DENIED', index=8, number=8,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='CODE_UNAUTHENTICATED', index=9, number=9,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='CODE_RESOURCE_EXHAUSTED', index=10, number=10,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='CODE_FAILED_PRECONDITION', index=11, number=11,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='CODE_ABORTED', index=12, number=12,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='CODE_OUT_OF_RANGE', index=13, number=13,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='CODE_UNIMPLEMENTED', index=14, number=14,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='CODE_INTERNAL', index=15, number=15,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='CODE_UNAVAILABLE', index=16, number=16,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='CODE_DATA_LOSS', index=17, number=17,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='CODE_REDIRECTION', index=18, number=18,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='CODE_INSUFFICIENT_STORAGE', index=19, number=19,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=48,
  serialized_end=515,
)
_sym_db.RegisterEnumDescriptor(_CODE)

Code = enum_type_wrapper.EnumTypeWrapper(_CODE)
CODE_INVALID = 0
CODE_OK = 1
CODE_CANCELLED = 2
CODE_UNKNOWN = 3
CODE_INVALID_ARGUMENT = 4
CODE_DEADLINE_EXCEEDED = 5
CODE_NOT_FOUND = 6
CODE_ALREADY_EXISTS = 7
CODE_PERMISSION_DENIED = 8
CODE_UNAUTHENTICATED = 9
CODE_RESOURCE_EXHAUSTED = 10
CODE_FAILED_PRECONDITION = 11
CODE_ABORTED = 12
CODE_OUT_OF_RANGE = 13
CODE_UNIMPLEMENTED = 14
CODE_INTERNAL = 15
CODE_UNAVAILABLE = 16
CODE_DATA_LOSS = 17
CODE_REDIRECTION = 18
CODE_INSUFFICIENT_STORAGE = 19


DESCRIPTOR.enum_types_by_name['Code'] = _CODE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)


DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)
