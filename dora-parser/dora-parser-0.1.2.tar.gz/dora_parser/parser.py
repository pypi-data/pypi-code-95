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
"""Parser Implementation"""
import re
from mo_sql_parsing import parse as moz_parser
from mo_parsing.exceptions import ParseException
from dora_parser import logger

class Parser():
    """Parser Object"""

    @classmethod
    def clean(cls, query) -> str:
        """Remove query comments and line breaks
        :return: clean sql query
        """
        return re.sub(r'(--.*?\n)|(/\*(.|\n)*?\*/)', '', query)

    def __init__(self,query:str):
        """Initialize the parser class
        :param query: sql query that will be translate
        """
        self.query =  Parser.clean(query)
        try:
            self.tree = moz_parser(self.query)
        except ParseException as err:
            logger.error("Query not supported:\n--PARSER:%s",err)
            raise err

    def __repr__(self) -> repr:
        """Sql query is parsed with moz_sql_parser
        :return: tree
        """ 
        return str(self.tree)
