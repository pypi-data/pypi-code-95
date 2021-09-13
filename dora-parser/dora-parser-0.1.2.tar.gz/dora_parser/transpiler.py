# -*- coding: utf-8 -*-
#
# Copyright 2021 Compasso UOL
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Transpiler Class Implementation"""
from dora_parser.dialects import WordToImplement
from dora_parser.parser import Parser
from dora_parser import logger

SUPPORTED_DIALECTS = ['spark','presto','impala','hive', 'athena']
class Transpiler:
    """Transpiler Object"""
    @classmethod
    def _import_dialect(cls, dialect) -> type:
        """Import Dialect by parameter
        :param dialect: Dialect name
        :return: Dialect class"""
        if dialect == 'spark':
            from dora_parser.dialects.spark import Spark
            return Spark
        if dialect == 'presto':
            from dora_parser.dialects.presto import Presto
            return Presto
        if dialect == 'impala':
            from dora_parser.dialects.impala import Impala
            return Impala
        if dialect == 'hive':
            from dora_parser.dialects.hive import Hive
            return Hive
        if dialect == 'athena':
            from dora_parser.dialects.athena import Athena
            return Athena
        raise ValueError(f"--TRANSPILER:DIALECT:{dialect}: NotImplemented'")

    def __init__(self, from_dialect:str, to_dialect:str):
        """Initialize the transpiler class
        :param from_dialect: From SQL dialect
        :param to_dialect: To SQL dialect
        """
        _from_dialect = str(from_dialect).lower()
        _to_dialect = str(to_dialect).lower()
        logger.debug("%s -> %s", _from_dialect, _to_dialect)
        if _from_dialect not in SUPPORTED_DIALECTS or _to_dialect not in SUPPORTED_DIALECTS:
            raise ValueError(f"Only the following dialects are supported:{SUPPORTED_DIALECTS}")
        self.dialect = Transpiler._import_dialect(_to_dialect)(source=_from_dialect)
        self._errors = list()

    def resolve(self, tree:dict) -> dict:
        """Resolve tree based on dialect recursively
        :return: the resulting tree
        """
        if isinstance(tree, dict):
            for key, value in tree.items():
                self.resolve(value)
                try:
                    _word = str(key).upper()
                    if _word in self.dialect.words:
                        _old = tree.pop(key)
                        try:
                            _new = self.dialect.words[_word](value)
                        except Exception as err:
                            logger.error("--DIALECT:IMPLEMENTATION:ERROR:'%s':'%s'",_word,err)
                            _new = WordToImplement(err)
                        if isinstance(_new, WordToImplement):
                            logger.warning("%s NotImplemented:\n--TRANSPILER:%s:LEVEL%s:'%s'", key, _new.id, _new.level, key)
                            self._errors.append({key:(str(_new.id) + ":" + str(_new.level) + ":" + str(_new))})
                            tree[_word]=_old
                        elif isinstance(_new, dict):
                            for _key, _value in _new.items():
                                tree[_key]=_value
                                if str(_key).lower() != str(_word).lower():
                                    logger.info("--TRANSLATE:'%s' TO '%s'",_word, _new)
                        return tree
                except Exception as err:
                    logger.error('%s:%s',key,err)
                    self._errors.append({key:err})
        if isinstance(tree, list):
            for value in tree:
                self.resolve(value)
        return tree
    
    def format(self, tree, **kwargs) -> str:
        """Format to SQL Query, based on dialect
        :param tree: query tree representation
        :return: sql query as string"""
        return self.dialect.format(tree, **kwargs)
    
    def translate(self, parse:Parser, **kwargs) -> list:
        """Translation are maded by two steps: resolve the query tree and format to SQL
        :param parse: Parser object
        :return: list with two values: SQL query and problems
        """
        self._errors = list() # Clean older errors
        _tree = self.resolve(parse.tree)
        logger.debug("RESOLVE:%s", _tree)
        return [
            self.format(_tree, **kwargs),# Query
            self._errors] # Problems
