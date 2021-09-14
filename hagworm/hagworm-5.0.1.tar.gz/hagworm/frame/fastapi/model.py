# -*- coding: utf-8 -*-

from inspect import Signature, Parameter

from pydantic.main import BaseModel, ModelMetaclass
from fastapi import Form


class FormModelMetaclass(ModelMetaclass):

    def __init__(cls, _what, _bases=None, _dict=None):

        super().__init__(_what, _bases, _dict)

        if cls.__fields__:

            params = []

            for field in cls.__fields__.values():

                params.append(
                    Parameter(
                        field.name, Parameter.POSITIONAL_OR_KEYWORD,
                        default=Form(field.default) if not field.required else Form(...),
                        annotation=field.type_
                    )
                )

            cls.__signature__ = Signature(params)


class FormModel(BaseModel, metaclass=FormModelMetaclass):
    pass
