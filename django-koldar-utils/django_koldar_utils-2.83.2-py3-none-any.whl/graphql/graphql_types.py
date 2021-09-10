from typing import Union

import graphene

TDjangoModelType = type
"""
A type that extends models.Model
"""
TGrapheneType = type
"""
A type that extends graphene.OPbjectType
"""
TGrapheneInputType = type
"""
A type that extends graphene.ObjectInputType
"""

TGrapheneReturnType = Union[graphene.Scalar, graphene.Field]
"""
A type that is put in graphene.ObjectType and represents a query/mutation field
"""
TGrapheneArgument = Union[graphene.Scalar, graphene.InputObjectType, graphene.Argument]
"""
A type that is put in graphene.ObjectType and represents a query/mutation argument
"""