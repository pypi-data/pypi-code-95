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

from types import FunctionType
from dora_parser.dialects.presto import Presto
from dora_parser.dialects import Dialect, Formatter
from dora_parser.dialects import EasyToImplement, MediumToImplement, HardToImplement
from dora_parser import logger
import re

types = ["STRING","BOOLEAN","TINYINT","SMALLINT","INTEGER","BIGINT","REAL","DOUBLE","DECIMAL","VARCHAR","CHAR","VARBINARY","JSON","DATE","TIME", "TIMESTAMP","INTERVAL","ARRAY","MAP","ROW","IPADDRESS","IPPREFIX"]
func_comp =["GREATEST", "LEAST"]
func_cond = ["IF", "COALESCE", "NULLIF", "TRY"]
func_conv = ["CAST", "TRY_CAST", "PARSE_PRESTO_DATA_SIZE", "TYPEOF"]
func_math = ["ABS", "CBRT", "CEIL", "CEILING", "COSINE_SIMILARITY", "DEGREES", "E", "EXP", "FLOOR", "FROM_BASE", "INVERSE_NORMAL_CDF", "NORMAL_CDF", "INVERSE_BETA_CDF", "BETA_CDF", "LN", "LOG2", "LOG10", "MOD", "PI", "POW", "POWER", "RADIANS", "RAND", "RANDOM", "RANDOM", "ROUND", "ROUND", "SIGN", "SQRT", "TO_BASE", "TRUNCATE", "WIDTH_BUCKET", "WILSON_INTERVAL_LOWER", "WILSON_INTERVAL_UPPER", "ACOS", "ASIN", "ATAN", "ATAN2", "COS", "COSH", "SIN", "TAN", "TANH", "INFINITY", "IS_FINITE", "IS_INFINITE", "IS_NAN", "NAN"]
func_bit = ["BIT_COUNT", "BITWISE_AND", "BITWISE_NOT", "BITWISE_OR", "BITWISE_paramOR"]
func_string = ["CHR", "CODEPOINT", "CONCAT", "HAMMING_DISTANCE", "LENGTH", "LEVENSHTEIN_DISTANCE", "LOWER", "LPAD", "LTRIM", "REPLACE", "REVERSE", "RPAD", "RTRIM", "SPLIT", "SPLIT_PART", "SPLIT_TO_MAP", "SPLIT_TO_MULTIMAP", "STRPOS", "POSITION", "SUBSTR", "TRIM", "UPPER", "WORD_STEM", "WORD_STEM", "NORMALIZE", "NORMALIZE", "TO_UTF8", "FROM_UTF8"]
func_reg = ["REGEXP_EXTRACT_ALL","REGEXP_EXTRACT","REGEXP_LIKE","REGEXP_REPLACE","REGEXP_SPLIT"]
func_bin = ["LENGTH", "CONCAT", "SUBSTR", "SUBSTR", "TO_BASE64", "FROM_BASE64", "TO_BASE64URL", "FROM_BASE64URL", "TO_HEX", "FROM_HEX", "TO_BIG_ENDIAN_64", "FROM_BIG_ENDIAN_64", "TO_BIG_ENDIAN_32", "FROM_BIG_ENDIAN_32", "TO_IEEE754_32", "FROM_IEEE754_32", "TO_IEEE754_64", "FROM_IEEE754_64", "LPAD", "RPAD", "CRC32", "MD5", "SHA1", "SHA256", "SHA512", "XXHASH64", "SPOOKY_HASH_V2_32", "SPOOKY_HASH_V2_64", "HMAC_MD5", "HMAC_SHA1", "HMAC_SHA256", "HMAC_SHA512"]
fun_json = ["IS_JSON_SCALAR", "JSON_ARRAY_CONTAINS", "JSON_ARRAY_GET", "JSON_ARRAY_LENGTH", "JSON_EXTRACT", "JSON_EXTRACT_SCALAR", "JSON_FORMAT", "JSON_PARSE", "JSON_SIZE"]
func_date = ["CURRENT_DATE", "CURRENT_TIME", "CURRENT_TIMESTAMP", "CURRENT_TIMEZONE", "DATE", "FROM_ISO8601_TIMESTAMP", "FROM_ISO8601_DATE", "FROM_UNIXTIME", "FROM_UNIXTIME", "FROM_UNIXTIME", "LOCALTIME ", "LOCALTIMESTAMP", "NOW", "TO_ISO8601", "TO_MILLISECONDS", "TO_UNIXTIME", "DATE_TRUNC", "DATE_ADD", "DATE_DIFF", "PARSE_DURATION", "DATE_FORMAT", "DATE_PARSE", "FORMAT_DATETIME", "PARSE_DATETIME", "EXTRACT", "DAY", "DAY_OF_MONTH", "DAY_OF_WEEK", "DAY_OF_YEAR", "DOW", "DOY", "HOUR", "MILLISECOND", "MINUTE", "MONTH", "QUARTER", "SECOND", "TIMEZONE_HOUR", "TIMEZONE_MINUTE", "WEEK", "WEEK_OF_YEAR", "YEAR", "YEAR_OF_WEEK", "YOW"]
fun_agg = ["ARBITRARY","ARRAY_AGG","AVG","BOOL_AND","BOOL_OR","CHECKSUM","COUNT","COUNT_IF","EVERY","GEOMETRIC_MEAN","MAX_BY","MIN_BY","MAX","MIN","REDUCE_AGG","SUM","BITWISE_AND_AGG","BITWISE_OR_AGG","HISTOGRAM","MAP_AGG","MAP_UNION","MULTIMAP_AGG","APPROX_DISTINCT","APPROX_PERCENTILE","APPROX_SET","MERGE","MERGE","QDIGEST_AGG","NUMERIC_HISTOGRAM","CORR","COVAR_POP","COVAR_SAMP","KURTOSIS","REGR_INTERCEPT","REGR_SLOPE","SKEWNESS","STDDEV","STDDEV_POP","STDDEV_SAMP","VARIANCE","VAR_POP","VAR_SAMP"]
func_win = ["CUME_DIST", "DENSE_RANK", "NTILE", "PERCENT_RANK", "RANK", "ROW_NUMBER", "FIRST_VALUE", "LAST_VALUE", "NTH_VALUE", "LEAD", "LAG"]
func_array = ["ARRAY_DISTINCT","ARRAY_INTERSECT","ARRAY_UNION","ARRAY_EXCEPT","ARRAY_JOIN","ARRAY_MAX","ARRAY_MIN","ARRAY_POSITION","ARRAY_REMOVE","ARRAY_SORT","ARRAYS_OVERLAP","CARDINALITY","CONCAT","CONTAINS","ELEMENT_AT","FILTER","FLATTEN","NGRAMS","REDUCE","REPEAT","REVERSE","SEQUENCE","SHUFFLE","SLICE","TRANSFORM","ZIP","ZIP_WITH"]
func_map = ["CARDINALITY", "ELEMENT_AT", "MAP", "MAP_FROM_ENTRIES", "MULTIMAP_FROM_ENTRIES", "MAP_ENTRIES", "MAP_CONCAT", "MAP_FILTER", "MAP_KEYS", "MAP_VALUES", "MAP_ZIP_WITH", "TRANSFORM_KEYS", "TRANSFORM_VALUES"]
func_url = ["URL_EXTRACT_FRAGMENT", "URL_EXTRACT_HOST", "URL_EXTRACT_PARAMETER", "URL_EXTRACT_PATH", "URL_EXTRACT_PORT", "URL_EXTRACT_PROTOCOL", "URL_EXTRACT_QUERY", "URL_ENCODE", "URL_DECODE"]
func_geo = ["ST_ASBINARY","ST_ASTEXT","ST_GEOMETRYFROMTEXT","ST_GEOMFROMBINARY","ST_LINEFROMTEXT","ST_LINESTRING","ST_MULTIPOINT","ST_POINT","ST_POLYGON","TO_SPHERICAL_GEOGRAPHY","TO_GEOMETRY","ST_CONTAINS","ST_CROSSES","ST_DISJOINT","ST_EQUALS","ST_INTERSECTS","ST_OVERLAPS","ST_RELATE","ST_TOUCHES","ST_WITHIN","GEOMETRY_UNION","ST_BOUNDARY","ST_BUFFER","ST_DIFFERENCE","ST_ENVELOPE","ST_ENVELOPEASPTS","ST_EXTERIORRING","ST_INTERSECTION","ST_SYMDIFFERENCE","ST_UNION","ST_AREA","ST_CENTROID","ST_CONVEXHULL","ST_COORDDIM","ST_DIMENSION","ST_DISTANCE","ST_DISTANCE","ST_GEOMETRYN","ST_INTERIORRINGN","ST_GEOMETRYTYPE","ST_ISCLOSED","ST_ISEMPTY","ST_ISSIMPLE","ST_ISRING","ST_ISVALID","ST_LENGTH","ST_POINTN","ST_POINTS","ST_paramMAX","ST_YMAX","ST_paramMIN","ST_YMIN","ST_STARTPOINT","SIMPLIFY_GEOMETRY","ST_ENDPOINT","ST_param","ST_Y","ST_INTERIORRINGS","ST_NUMGEOMETRIES","ST_GEOMETRIES","ST_NUMPOINTS","ST_NUMINTERIORRING","LINE_LOCATE_POINT","GEOMETRY_INVALID_REASON","GREAT_CIRCLE_DISTANCE","CONVEX_HULL_AGG","GEOMETRY_UNION_AGG","BING_TILE","BING_TILE_AT","BING_TILES_AROUND","BING_TILE_COORDINATES","BING_TILE_POLYGON","BING_TILE_QUADKEY","BING_TILE_ZOOM_LEVEL","GEOMETRY_TO_BING_TILES"]
func_hyper = ["APPROX_SET", "CARDINALITY", "EMPTY_APPROX_SET", "MERGE"]
func_quan = ["VALUE_AT_QUANTILE", "VALUES_AT_QUANTILES", "QDIGEST_AGG"]
func_etc = ["BAR","COLOR","RENDER","RGB","CURRENT_USER","CHAR2HEXINT","INDEX","SUBSTRING","TO_CHAR","TO_TIMESTAMP","TO_DATE"]
functions = func_comp+func_cond+func_conv+func_math+func_bit+func_string+func_reg+func_bin+fun_json+func_date+fun_agg+func_win+func_array+func_map+func_url+func_geo+func_hyper+func_quan+func_etc


class AthenaFormatter(Formatter):
    """Extends mo-sql-parsing Formatter for Athena""" 
    def _interval(self, pair):       
        """Format INTERVAL values:            
        Ex : interval '3' day"""        
        _qtd, _unit = pair    
        units = ['millisecond', 'second', 'minute', 'hour', 'day', 'month', 'quarter', 'year']     
        if _unit in units: 
            return f"INTERVAL '{_qtd}' {_unit.upper()}"
        if _unit == 'week':
            _qtd = _qtd * 7
            _unit = 'DAY'
            return f"INTERVAL '{_qtd}' {_unit}"
        return MediumToImplement

SUPPORTED_DIALECTS = ['impala','hive']

class Athena(Presto):
    """Athena extended from Presto Dialect definition"""
    def __init__(self, source:str, formater=AthenaFormatter):
        if source not in SUPPORTED_DIALECTS:
            raise ValueError(f"{source} dialect not supported")
        super().__init__(source, formater=formater)
        self.implemented(functions + types)

    def STATEMENTS(self, key):
        """Dict of DML queries and DDL statements from Impala to Athena
           param: key is used to acess the dict and is formatted as: 'source_dialect'-'end_dialect' """

        statement_dict = {
                        "impala-athena": {
                                "not_allowed": {  "ALTER DATABASE" : r"^(ALTER(\s*)DATABASE)",
                                                  "ALTER TABLE ADD IF NOT EXISTS COLUMNS": r'^(ALTER(\s*)TABLE(.|\n)*?ADD(\s*)(IF(\s*)NOT(\s*)EXISTS)(\s*)COLUMNS)',
                                                  "ALTER TABLE ADD COLUMN":r"^(ALTER(\s*)TABLE(.|\n)*?ADD(\s*)(COLUMN ))",
                                                  "ALTER TABLE ADD COLUMNS WITH COMMENT OR KUDU_ATTRIBUTES":r"^(ALTER(\s*)TABLE(.|\n)*?ADD(.|\n)*?COLUMNS(.|\n)*?(COMMENT|NULL|COMPRESSION|DEFAULT|BLOCK_SIZE|ENCODING))",
                                                  "ALTER TABLE ADD PARTITION WITH CACHED":r"^(ALTER(\s*)TABLE(.|\n)*?ADD(.|\n)*?PARTITION(.|\n)*?(CACHED(\s*)IN ))",
                                                  "ALTER TABLE ALTER":r"^(ALTER(\s*)TABLE(.|\n)*?(ALTER ))",
                                                  "ALTER TABLE DROP":r"^(ALTER(\s*)TABLE(.|\n)*?DROP(\s*)(?!.*PARTITION))",
                                                  "ALTER TABLE DROP PARTITION":r"^(ALTER(\s*)TABLE(.|\n)*?DROP(.|\n)*?PARTITION(.|\n)*?(PURGE))",
                                                  "ALTER TABLE CHANGE":r"^(ALTER(\s*)TABLE(.|\n)*?CHANGE )",
                                                  "ALTER TABLE SET CACHED IN OR UNCACHED":r"^(ALTER(\s*)TABLE(.|\n)*?SET(\s*)(UNCACHED|CACHED(\s*)IN ))",
                                                  "ALTER TABLE SET FILEFORMAT":r'^(ALTER(\s*)TABLE(.|\n)*?SET(\s*)(FILEFORMAT))',
                                                  "ALTER TABLE SET SERDEPROPERTIES":r"^(ALTER(\s*)TABLE(.|\n)*?SET(\s*)(SERDEPROPERTIES))",
                                                  "ALTER TABLE SET ROW FORMAT":r"^(ALTER(\s*)TABLE(.|\n)*?SET(\s*)(ROW(\s*)FORMAT))",
                                                  "ALTER TABLE SET OWNER USER":r"^(ALTER(\s*)TABLE(.|\n)*?(SET(\s*)OWNER(\s*)USER ))",
                                                  "ALTER TABLE RANGE PARTITION":r"^(ALTER(\s*)TABLE(.|\n)*?(RANGE(\s*)PARTITION ))",
                                                  "ALTER TABLE RECOVER PARTITIONS":r"^(ALTER(\s*)TABLE(.|\n)*?(RECOVER(\s*)PARTITIONS))",
                                                  "ALTER TABLE REPLACE COLUMNS WITH COMMENT OR KUDU_ATTRIBUTES":r"^(ALTER(\s*)TABLE(.|\n)*?REPLACE(\s*)COLUMNS(.|\n)*?(COMMENT|NULL|COMPRESSION|DEFAULT|BLOCK_SIZE|ENCODING))",
                                                  "ALTER TABLE RENAME TO":r"^(ALTER(\s*)TABLE(.|\n)*?(RENAME(\s*)TO ))",
                                                  "ALTER TABLE WITH STATSKEY":r"^(ALTER(\s*)TABLE(.|\n)*?(numDVs|numNulls|avgSize|maxSize))",
                                                  "ALTER VIEW" : r"^(ALTER(\s*)VIEW)",
                                                  "COMPUTE STATS":r"^(COMPUTE(.|\n)*?STATS)",
                                                  "COMMENT (START WITH)":r"^(COMMENT)",
                                                  "CREATE FUNCTION":r"^(CREATE(.|\n)*?FUNCTION)",
                                                  "CREATE TABLE AS SELECT":r"^(CREATE(.|\n)*?TABLE(.|\n)*?(AS(\s*)SELECT))",
                                                  "CREATE TABLE EXCEPTIONS":r"^(CREATE(.|\n)*?TABLE(.|\n)*?(PRIMARY(\s*)KEY|FOREIGN(\s*)KEY|SORT(\s*)BY|CACHED(\s*)IN ))",
                                                  "CREATE TABLE LIKE":r"^(CREATE(.|\n)*?TABLE(.|\n)*?(LIKE))",
                                                  "CREATE TABLE KUDU EXCEPTIONS":r"^(CREATE(.|\n)*?TABLE(.|\n)*?(PRIMARY(\s*)KEY|NULL |ENCODING|COMPRESSION|DEFAULT|BLOCK_SIZE|PARTITION(\s*)BY ))",
                                                  "CREATE ROLE":r"^(CREATE(\s*)ROLE)",
                                                  "CREATE VIEW": r"^(CREATE(\s*)VIEW(.|\n)*?(IF(\s*)NOT(\s*)EXISTS|COMMENT|\((.+)\))(.|\n)*?AS(\s*)SELECT)",
                                                  "DELETE":r"^(DELETE)",
                                                  "DESCRIBE DATABASE":r"^(DESCRIBE(.|\n)*?DATABASE)",
                                                  "DROP FUNCTION":r"^(DROP(\s*)FUNCTION)",
                                                  "DROP ROLE":r"^(DROP(\s*)ROLE)",
                                                  "DROP STATS":r"^(DROP(.|\n)*?STATS)",
                                                  "DROP TABLE PURGE":r"^(DROP(\s*)TABLE(.|\n)*?PURGE)",
                                                  "GRANT":r"^(GRANT)",
                                                  "INSERT":r"^(INSERT(.|\n)*?(TABLE |OVERWRITE|PARTITION|VALUES))",
                                                  "INVALIDATE METADATA":r"^(INVALIDATE(\s*)METADATA)",
                                                  "OPTIMIZER HINTS":r"(BROADCAST|SHUFFLE|NOSHUFFLE|SCHEDULE_CACHE_LOCAL|SCHEDULE_DISK_LOCAL|SCHEDULE_REMOTE|CLUSTERED|NOCLUSTERED)",
                                                  "LOAD DATA":r"^(LOAD(\s*)DATA )",
                                                  "REFRESH":r"^(REFRESH)",
                                                  "REVOKE":r"^(REVOKE)",
                                                  "SET":r"^(SET)",
                                                  "SHOW EXCEPTIONS":r"^(SHOW(.|\n)*?(TABLES(.|\n)*?LIKE |FUNCTIONS|GRANT|ROLES|ROLE|FILES(\s*)IN|RANGE|COLUMN(\s*)STATS|TABLE(\s*)STATS))",
                                                  "SHUTDOWN":r"^(:SHUTDOWN)",
                                                  "TRUNCATE":r"^(TRUNCATE)",
                                                  "USE":r"^(USE)",
                                                  "UPDATE":r"^(UPDATE)",
                                                  "UPSERT":r"^(UPSERT)",
                                                  "VALUES (START WITH)":r"^(VALUES)",
                                                  "USE":r"^(USE)",
                                                  "WITH INSERT":r"^(WITH(.|\n)*?INSERT)"
                                },
                                
                                "replace": {
                                                "CREATE EXTERNAL TABLE" : "CREATE TABLE",
                                                "REAL" : "FLOAT"
                                }
                        }
        }
        return statement_dict[key]
        