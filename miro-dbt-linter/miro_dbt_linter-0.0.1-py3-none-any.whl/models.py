import inspect
import json
import pathlib
import os
import warnings
import pydantic
import importlib
import sys
from typing import Union, Dict, List

from .rules import LintRule
from .settings import Settings, Project


class NodeReference(object):

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError(f'Node reference must be a string, got {type(v)}')
        else:
            return cls(unique_id=v)

    def __init__(self, unique_id):
        self.unique_id = unique_id

    def __eq__(self, other):
        if hasattr(other, 'unique_id'):
            return self.unique_id == other.unique_id
        else:
            return False

    def __hash__(self):
        return hash(self.unique_id)

    def __getattr__(self, attr):
        if attr in dir(self.node):
            return getattr(self.node, attr)
        else:
            raise AttributeError

    def __repr__(self):
        return f"<NodeReference {self.unique_id}>"

    @property
    def project(self):
        return Settings.project

    @property
    def node(self):
        return self.project.manifest.nodes[self]


class DependsOn(pydantic.BaseModel):
    nodes: List[NodeReference]
    macros: List[str]

    class Config:
        extra: 'allow'
        arbitrary_types_allowed = True


class Node(pydantic.BaseModel):

    class Config:
        extra = 'allow'

    @property
    def project(self):
        return Settings.project

    config: dict
    path: str
    original_file_path: str
    resource_type: str
    database: str
    unique_id: str
    depends_on: 'DependsOn'
    name: str
    alias: str
    tags: List[str]
    db_schema: str = pydantic.Field(alias='schema')

    def __str__(self):
        return f"<{self.resource_type.capitalize()}Node {self.name}>"

    def __hash__(self):
        return hash(self.unique_id)

    @classmethod
    def from_unique_id(cls, unique_id):
        return NodeReference(unique_id)

    @property 
    def children(self):
        return self.project.manifest.child_map[self]

    @property
    def parents(self):
        return self.project.manifest.parent_map[self]

    @property
    def tests(self):
        results = []
        for node in self.children:
            if node.resource_type == 'test':
                results.append(node)
        return results

    @property
    def catalog(self):
        return self.project.catalog.nodes[self]


class CatalogNodeColumn(pydantic.BaseModel):
    type: str
    index: int
    name: str
    comment: Union[str, None]


class CatalogNode(pydantic.BaseModel):
    metadata: dict
    columns: Dict[str, CatalogNodeColumn]


class Manifest(pydantic.BaseModel):
    metadata: dict
    nodes: Dict[NodeReference, Node]
    project: Project
    child_map: Dict[NodeReference, List[NodeReference]]
    parent_map: Dict[NodeReference, List[NodeReference]]

    @classmethod
    def from_path(cls, path):
        with open(path, 'r') as f:
            data = json.load(f)
            return cls(
                project=Settings.project,
                metadata=data['metadata'], 
                nodes=data['nodes'],
                child_map=data['child_map'],
                parent_map=data['parent_map']
            )

    def get_model_from_path(self, path):
        for node_id, node in self.nodes.items():
            if node.resource_type == 'model' and node.original_file_path.endswith(str(path)):
                return node
        else:
            raise AttributeException


class Catalog(pydantic.BaseModel):
    metadata: dict
    nodes: Dict[NodeReference, CatalogNode]
    project: Project

    @classmethod
    def from_path(cls, path):
        with open(path, 'r') as f:
            data = json.load(f)
            return cls(metadata=data['metadata'], nodes=data['nodes'], 
                       project=Settings.project)
