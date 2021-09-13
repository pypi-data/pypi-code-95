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
"""Impala Dialect definition"""
from dora_parser.dialects import Dialect

types = ["ARRAY","BIGINT","BOOLEAN","CHAR","DATE","DOUBLE","FLOAT","INT","MAP","REAL","SMALLINT","STRING","STRUCT","TIMESTAMP","TINYINT","VARCHAR"]

func_math = ["ABS","ACOS","ASIN","ATAN","ATAN2","BIN","CEIL","CEILING","DCEIL","CONV","COS","COSH","COT","DEGREES","E","EXP","FACTORIAL","FLOOR","DFLOOR","FMOD","FNV_HASH","GREATEST","HEX","IS_INF","IS_NAN","LEAST","LN","LOG","LOG10","LOG2","MAX_INT","MAX_TINYINT","MAX_SMALLINT","MAX_BIGINT","MIN_INT","MIN_TINYINT","MIN_SMALLINT","MIN_BIGINT","MOD","MURMUR_HASH","NEGATIVE","PI","PMOD","POSITIVE","POW","POWER","DPOW","FPOW","PRECISION","QUOTIENT","RADIANS","RAND","RANDOM","ROUND","DROUND","SCALE","SIGN","SIN","SINH","SQRT","TAN","TANH","TRUNCATE","DTRUNC","TRUNC","UNHEX","WIDTH_BUCKET"]

func_bit = ["BITAND","BITNOT","BITOR","BITXOR","COUNTSET","GETBIT","ROTATELEFT","ROTATERIGHT","SETBIT","SHIFTLEFT","SHIFTRIGHT"]

func_convert = ["CAST","TYPEOF"]

func_date = ["ADD_MONTHS","ADDDATE","CURRENT_TIMESTAMP","DATE_ADD","DATE_PART","DATE_SUB","DATE_TRUNC","DATEDIFF","DAY","DAYNAME","DAYOFWEEK","DAYOFYEAR","DAYS_ADD","DAYS_SUB","EXTRACT","FROM_TIMESTAMP","FROM_UNIXTIME","FROM_UTC_TIMESTAMP","HOUR","HOURS_ADD","HOURS_SUB","INT_MONTHS_BETWEEN","MICROSECONDS_ADD","MICROSECONDS_SUB","MILLISECOND","MILLISECONDS_ADD","MILLISECONDS_SUB","MINUTE","MINUTES_ADD","MINUTES_SUB","MONTH","MONTHNAME","MONTHS_ADD","MONTHS_BETWEEN","MONTHS_SUB","NANOSECONDS_ADD","NANOSECONDS_SUB","NEXT_DAY","NOW","QUARTER","SECOND","SECONDS_ADD","SECONDS_SUB","SUBDATE","TIMEOFDAY","TIMESTAMP_CMP","TO_DATE","TO_TIMESTAMP","TO_UTC_TIMESTAMP","TRUNC","UNIX_TIMESTAMP","UTC_TIMESTAMP","WEEKOFYEAR","WEEKS_ADD","WEEKS_SUB","YEAR","YEARS_ADD","YEARS_SUB"]

func_cond = ["CASE","CASE2","COALESCE","DECODE","IF","IFNULL","ISFALSE","ISNOTFALSE","ISNOTTRUE","ISNULL","ISTRUE","NONNULLVALUE","NULLIF","NULLIFZERO","NULLVALUE","NVL","NVL2","ZEROIFNULL"]

func_string = ["ASCII","BASE64DECODE","BASE64ENCODE","BTRIM","CHAR_LENGTH","CHR","CONCAT","CONCAT_WS","FIND_IN_SET","GROUP_CONCAT","INITCAP","INSTR","LEFT","LENGTH","LEVENSHTEIN","LE_DST","LOCATE","LOWER","LCASE","LPAD","LTRIM","PARSE_URL","REGEXP_ESCAPE","REGEXP_EXTRACT","REGEXP_LIKE","REGEXP_REPLACE","REPEAT","REPLACE","REVERSE","RIGHT","RPAD","RTRIM","SPACE","SPLIT_PART","STRLEFT","STRRIGHT","SUBSTR","SUBSTRING","TRANSLATE","TRIM","UPPER","UCASE"]

func_misc = ["CURRENT_DATABASE","EFFECTIVE_USER","LOGGED_IN_USER","PID","SLEEP","USER","UUID","VERSION","COORDINATOR"]

func_agg = ["APPX_MEDIAN","AVG","COUNT","GROUP_CONCAT","MAX","MIN","NDV","STDDEV","STDDEV_SAMP","STDDEV_POP","SUM","VARIANCE","VARIANCE_SAMP","VARIANCE_POP","VAR_SAMP","VAR_POP"]

functions = func_math + func_bit + func_convert + func_date + func_cond + func_string + func_misc + func_agg

SUPPORTED_DIALECTS = []

class Impala(Dialect):
    def __init__(self, source:str):
        if source not in SUPPORTED_DIALECTS:
            raise ValueError(f"{source} dialect not supported")
        super().__init__(source)
        self.implemented(functions + types)

    @property
    def CHAR(self):
        """string(expr) - Casts the value expr to the target data type string."""
        return lambda x: {'string': x}
    
    @property
    def VARCHAR(self):
        """string(expr) - Casts the value expr to the target data type string."""
        return lambda x: {'string': x}