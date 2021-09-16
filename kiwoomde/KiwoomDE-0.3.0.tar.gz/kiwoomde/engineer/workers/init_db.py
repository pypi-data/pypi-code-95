# -*- coding: utf-8 -*-
from idebug import *


from kiwoomde.engineer.models import *
from kiwoomde import dba



@funcIdentity
def emit_all_schema():
    # 스키마컬렉션들 데이타를 SchemaCSV 로 모두 방출
    for modelName in dba.StaticSchemaModels():
        KWModel(modelName).schema.emit()

    logger.info('Done.')


@funcIdentity
def create_all_schemas():
    for modelName in dba.StaticSchemaModels():
        KWModel(modelName).schema.create()

    logger.info('Done.')


@funcIdentity
def create_meta_models():
    create_devguide_models()
    create_mandata_models()
    create_derived_models()
    logger.info('Done.')


@funcIdentity
def create_devguide_models():
    # DevGuideTextPath 에 있는 가장 기초 데이타의 컬렉션들을 생성
    for modelName in dba.DevGuideModels():
        DevGuideModel(modelName).create_collection()

    logger.info('Done.')


@funcIdentity
def create_mandata_models():
    # ManDataJSONPath 에 있는 수작업으로 작성한 데이타의 컬렉션들을 생성
    for modelName in dba.ManDataModels():
        ManDataModel(modelName).create_collection()

    logger.info('Done.')

@funcIdentity
def create_derived_models():
    # 그 후 파생되는 기초 컬렉션들을 생성: TRInput, TRItem, RealtimeFID
    for modelName in ['TRList','RTList','RealtimeFID']:
        MetaModel(modelName).create_collection()

    logger.info('Done.')
