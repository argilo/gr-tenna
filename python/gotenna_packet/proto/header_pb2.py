# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: gotenna_packet/proto/header.proto
# Protobuf Python Version: 4.25.2
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from gotenna_packet.proto import data_type_pb2 as gotenna__packet_dot_proto_dot_data__type__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n!gotenna_packet/proto/header.proto\x1a$gotenna_packet/proto/data_type.proto\"\xbc\x01\n\x0cPBBaseHeader\x12\x12\n\nsender_gid\x18\x01 \x01(\x04\x12\x10\n\x08\x63\x61llsign\x18\x02 \x01(\t\x12\'\n\x0bmessageType\x18\x03 \x01(\x0e\x32\x12.PBMessageDataType\x12\x0f\n\x07keyUuid\x18\x04 \x01(\t\x12\n\n\x02iv\x18\x05 \x01(\x0c\x12-\n\x10\x63onversationType\x18\x06 \x01(\x0e\x32\x13.PBConversationType\x12\x11\n\ttimestamp\x18\x07 \x01(\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'gotenna_packet.proto.header_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_PBBASEHEADER']._serialized_start=76
  _globals['_PBBASEHEADER']._serialized_end=264
# @@protoc_insertion_point(module_scope)
