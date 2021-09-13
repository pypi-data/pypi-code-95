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
"""Dialects module definition"""
from abc import ABC
from types import FunctionType
from mo_sql_parsing.formatting import Formatter as MoFormatter
from dora_parser import logger

class WordToImplement(NotImplementedError):
    """Raise this exception for functions you do not will implement"""
    def __init__(self, *args):
        super().__init__(*args)
        self.level = 0
        self.id = 'NOTIMPLEMENTED'
        self.params = args

    def __repr__(self) -> repr:
        """Sql query is parsed with moz_sql_parser
        :return: tree
        """ 
        return f"{self.id}:{self.level}:{self.args}"

class EasyToImplement(WordToImplement):
    """Indicates that is a low complexity work to implement"""
    def __init__(self, *args):
        super().__init__(*args)
        self.level = 10
        self.id = 'EASY'

class MediumToImplement(WordToImplement):
    """Indicates that is a medium complexity work to implement"""
    def __init__(self, *args):
        super().__init__(*args)
        self.level = 20
        self.id = 'MEDIUM'
class HardToImplement(WordToImplement):
    """Indicates that is a high complexity work to implement"""
    def __init__(self, *args):
        super().__init__(*args)
        self.level = 30
        self.id = 'HARD'

class Formatter(MoFormatter):
    """Extends mo-sql-parsing Formatter"""
    def _cast(self, pair):
        """Format cast functions as:
            Ex: CAST('value' AS TYPE)"""
        _typ = self.dispatch(pair[1])
        return "CAST({0} AS {1})".format(self.dispatch(pair[0]), _typ[:_typ.find('(')])
    
    def _interval(self, pair):
        """Format INTERVAL values:
            Ex: interval 3 weeks"""
        interval = ["INTERVAL"]
        for _p in pair:
            interval.append(str(self.dispatch(_p)))
        return " ".join(interval)
    
    def _in(self, json):
        """Superclass dont dispatch first argument"""
        valid = self.dispatch(json[1])
        if not valid.startswith("("):
            valid = "({0})".format(valid)
        return "{0} IN {1}".format(self.dispatch(json[0]), valid)

class NoneDialect:
    """Used load the dialect class without translation"""
    types = list()
    functions = list()

class Dialect(ABC):
    """ Dialects Superclass """
    def __init__(self, source:str, formater:MoFormatter=Formatter):
        """Initialization method"""
        # Properties
        self.separator = ""
        self.language = source
        self.formater = formater
        # Add source configs
        try:
            self.source = __import__(
                f"{__package__}.{source}",
                fromlist=['types','functions'])
        except ModuleNotFoundError as err:
            logger.warning(err)
            self.source = NoneDialect()
        logger.debug("IMPORT: %s", self.language)
        # Add attributes from source
        self.not_implemented(self.source.functions + self.source.types)
    
    def not_implemented(self, words:list):
        """Create all reserved words from dialect as properties returning HardToImplement"""
        for _word in words:
            _sign = f"""def {_word}(args): return HardToImplement"""
            _code = compile(_sign, self.source.__name__, "exec")
            try:
                self.__setattr__(_word, FunctionType(_code.co_consts[0], globals(), _word))
            except AttributeError as err:
                logger.debug("Implemented By dialect:%s",_word)

    def implemented(self, words:list):
        """Create all reserved words from dialect as properties returning implemented functions"""
        for _word in words:
            _sign = f"""def {_word}(args): return {{"{str(_word).lower()}":args}}"""
            _code = compile(_sign, __name__, "exec")
            try:
                self.__setattr__(_word, FunctionType(_code.co_consts[0], globals(), _word))
                logger.debug("%s:%s",self.language, _word)
            except AttributeError as err:
                logger.debug("%s:%s",_word,err)

    @property
    def words(self) -> dict:
        """Dictionary with all dialect words implemented"""
        response = dict()
        for _word in self.source.functions + self.source.types:
            response[_word]=self.__getattribute__(_word)
        for _word in dir(self):
            if str(_word).isupper() and not str(_word).startswith('_'):
                response[_word]=self.__getattribute__(_word)
        return response

    def format(self, tree:dict, **kwargs) -> str:
        """Format the tree objet as a SQL query"""
        return self.formater(**kwargs).format(tree)
