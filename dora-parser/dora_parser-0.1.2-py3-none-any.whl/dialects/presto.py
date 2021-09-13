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
from types import FunctionType
from dora_parser.dialects import Dialect, Formatter
from dora_parser.dialects import EasyToImplement, MediumToImplement, HardToImplement
from dora_parser import logger

types = ["BOOLEAN","TINYINT","SMALLINT","INTEGER","BIGINT","REAL","DOUBLE","DECIMAL","VARCHAR","CHAR","VARBINARY","JSON","DATE","TIME", "TIMESTAMP","INTERVAL","ARRAY","MAP","ROW","IPADDRESS","IPPREFIX"]
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

class PrestoFormatter(Formatter):
    """Extends mo-sql-parsing Formatter for Athena""" 
    def _interval(self, pair):
        """Format INTERVAL values:
        Ex : interval '3' week"""
        _qtd, _unit = pair
        units = ['millisecond', 'second', 'minute', 'hour', 'day', 'week', 'month', 'quarter', 'year']
        if _unit in units: 
            return f"INTERVAL '{_qtd}' {_unit}"
        return MediumToImplement

SUPPORTED_DIALECTS = ['impala','hive']

class Presto(Dialect):
    """Presto Dialect definition"""
    def __init__(self, source:str, formater:Formatter=PrestoFormatter):
        if source not in SUPPORTED_DIALECTS:
            raise ValueError(f"{source} dialect not supported")
        super().__init__(source, formater=formater)
        self.implemented(functions + types)

    @classmethod
    def _BTRIM_(cls, param):
        """Impala BTRIM has a second optional argument that Presto does not has."""
        _param = Presto._LIT_(param)
        if isinstance(_param,list):
            if len(_param)>1:
                return HardToImplement(param)
        return {'trim': param}
    @classmethod
    def _LOCATE_(cls, param):
        """Impala LOCATE has a third optional argument that Presto does not has."""
        _param = Presto._LIT_(param)
        if isinstance(_param,list):
            if len(_param)>2:
                return HardToImplement(param)
        return {'strpos': param}
    @classmethod
    def _TRUNCATE_(cls, param):
        """Impala TRUNCATE has a second optional argument that Presto does not has."""
        _param = Presto._LIT_(param)
        if isinstance(_param,list):
            return MediumToImplement(param)
        return {'truncate': param}
    @classmethod
    def _DATE_ADD_(cls, param):
        """Presto does not accepts an interval expression as an argument,  neither 'week', 'millisecond', 'microsecond', 'nanosecond' or 
        any unit in plural in the interval."""
        _param = Presto._LIT_(param)
        units = ['millisecond', 'second', 'minute', 'hour', 'day', 'week', 'month', 'quarter', 'year']
        if isinstance(_param,list):
            if isinstance(_param[1],int):
               return {'date_add':[{'literal':'day'},_param[1], _param[0]]}
            if isinstance(_param[1],dict): 
                if _param[1]['interval'][1].endswith('s'):
                   unit =  _param[1]['interval'][1]
                   unit = unit[:-1] 
                if _param[1]['interval'][1].lower() in units:
                    return {'date_add': [{'literal': _param[1]['interval'][1]}, _param[1]['interval'][0], param[0]]}
        return HardToImplement(param)
    @classmethod
    def _DATE_SUB_(cls, param):
        """Presto does not accepts an interval expression as an argument,  neither 'week', 'millisecond', 'microsecond', 'nanosecond' or 
        any unit in plural in the interval."""
        _param = Presto._LIT_(param)
        units = ['millisecond', 'second', 'minute', 'hour', 'day', 'week', 'month', 'quarter', 'year']
        if isinstance(_param,list):
            if isinstance(_param[1],int):
                return {'date_add':[{'literal':'day'},-_param[1], _param[0]]}
            if isinstance(_param[1],dict): 
                if _param[1]['interval'][1].endswith('s'):
                   unit =  _param[1]['interval'][1]
                   unit = unit[:-1] 
                if _param[1]['interval'][1].lower() in units:
                    return {'date_add': [{'literal': _param[1]['interval'][1]}, - _param[1]['interval'][0], param[0]]}
        return HardToImplement(param)
    @classmethod
    def _DATE_PART_(cls, param): 
        """Impala: DATE_PART(STRING part, TIMESTAMP / DATE date) -> extract(part from date)"""
        _param = Presto._LIT_(param)
        if isinstance(_param,list):
            if _param[0].get('literal')== 'epoch' or _param[0].get('literal')== 'milliseconds':
                return MediumToImplement(param)
        return {'extract': [param[0].get('literal'), param[1]]}
    @classmethod
    def _EXTRACT_(cls, param): 
        """Impala: EXTRACT(TIMESTAMP/DATE, STRING unit), EXTRACT(unit FROM TIMESTAMP/DATE). Presto only accepts the second option and neither epoch nor milliseconds unit."""
        _param = Presto._LIT_(param)
        if isinstance(_param,list) and isinstance(_param[1], dict):
            if _param[1].get('literal')== 'epoch' or _param[1].get('literal')== 'milliseconds': 
                return MediumToImplement(param)
            return {'extract': [param[1].get('literal'), param[0]]}
        if _param[0]== 'epoch' or _param[0]== 'milliseconds':
                return MediumToImplement(param)
        return {'extract': param}   
    @classmethod
    def _DATE_TRUNC_(cls, param): 
        """There are some units that Presto does not has."""
        _param = Presto._LIT_(param)
        units = ['microseconds' , 'milliseconds', 'decade', 'century', 'millenium']
        if isinstance(_param,list):
            if _param[0].get('literal')  in units:
                return MediumToImplement(param)
        return {'date_trunc': param}  
    @classmethod
    def _TRUNC_(cls, param): 
        """Impala and Presto label of units are different."""
        _param = Presto._LIT_(param)
        year = ['SYYYY', 'YYYY', 'YEAR', 'SYEAR', 'YYY', 'YY', 'Y']
        month = ['MONTH', 'MON', 'MM', 'RM']
        day = ['DDD', 'DD', 'J']
        week = ['DAY', 'DY', 'D']
        hour=  ['HH', 'HH12', 'HH24']
        if isinstance(_param,list):
            if _param[1].get('literal')== 'WW' or _param[1].get('literal')== 'w':
                return MediumToImplement(param)
            if _param[1].get('literal').upper() in year:
                return {'trunc': [{'literal': 'year'}, param[0]]}
            if _param[1].get('literal').upper() == 'Q':
                return {'trunc': [{'literal': 'quarter'}, param[0]]}
            if _param[1].get('literal').upper() in month:
                return {'trunc': [{'literal': 'month'}, param[0]]}
            if _param[1].get('literal').upper() in day:
                return {'trunc': [{'literal': 'day'}, param[0]]}
            if _param[1].get('literal').upper() in week:
                return {'trunc': [{'literal': 'week'}, param[0]]}
            if _param[1].get('literal').upper() in hour:
                return {'trunc': [{'literal': 'hour'}, param[0]]}
            if _param[1].get('literal').upper() == 'MI':
                return {'trunc': [{'literal': 'minute'}, param[0]]}
        return MediumToImplement(param)
    @classmethod
    def _UNIX_TIMESTAMP_(cls, param): 
        """Impala/Hive: unix_timestamp() -> Presto: to_unixtime(current_timestamp)
           Impala/Hive:unix_timestamp('2021-07-28 11:30:01') -> Presto: to_unixtime(cast('2009-03-20 11:30:01' as timestamp))"""
        if len(param) == 0:
            return {'to_unixtime': 'current_timestamp'}    
        if len(param) == 2:
            return MediumToImplement(param)
        logger.warning("-- UNIX_TIMESTAMP: Assumed that no date of type string is passed.")
        return {'to_unixtime': param}       
            
    @classmethod
    def _TO_TIMESTAMP_(cls, param):
        """Impala TO_TIMESTAMP has a second optional pattern argument that Presto does not has."""
        _param = Presto._LIT_(param)
        if isinstance(_param,list):
            if len(_param)==2:
                return MediumToImplement(param)
        return {'from_unixtime': param} 
    @classmethod
    def _LIT_(cls, param):
        """Object literal to list of literals"""
        try:
            if isinstance(param['literal'],list):
                return [{'literal':p} for p in param['literal']]
        except:
            return param
    @property
    def STRING(self):
        """Replace string data type for varchar"""
        if self.language == 'hive' or self.language == 'impala':
            return lambda x : {'varchar': x}  
        return lambda x : {'string': x}
    @property
    def FLOAT(self):
        """Replace float data type for real"""
        if self.language == 'hive' or self.language == 'impala':
            return lambda x : {'real': x}  
        return lambda x : {'float': x}
    @property
    def REAL(self):
        """Replace real data type for double"""
        if self.language == 'impala':
            return lambda x : {'double': x}  
        return lambda x : {'real': x}
    @property
    def TIME(self):
        return lambda x : {'time': x}
    @property
    def VARBINARY(self):
        return lambda x :{'VARBINARY': x}
    @property
    def BINARY(self):
        if self.language == 'hive' or self.language == 'impala':
            return lambda x :{'VARBINARY': x}
        return lambda x : {'binary': x}
    @property
    def ARRAY_CONTAINS(self):
        """array_contains(Array<T>, value): Returns TRUE if the array contains the specified value."""
        if self.language == 'hive':
            return lambda x : {'contains': x}
        return lambda x : {'array_contains': x}
    @property
    def SPLIT(self):
        """split(string str, string pat): Splits str around pat (pat is a regular expression)."""
        if self.language == 'hive':
            return lambda x :{'regexp_split': x}
        return lambda x : {'split': x}
    @property
    def UCASE(self):
        """Returns the string resulting from converting all characters to upper case."""
        if self.language == 'hive' or self.language == 'impala':
            return lambda x :{'upper': x}
        return lambda x : {'ucase': x}
    @property
    def LCASE(self):
        """Returns the string resulting from converting all characters to lower case. """
        if self.language == 'hive' or 'impala':
            return lambda x :{'lower': x}    
        return lambda x : {'lcase': x}
    @property
    def SIZE(self):
        """Returns the number of elements in the map or array type."""
        if self.language == 'hive':
            return lambda x :{'cardinality': x}
        return lambda x : {'size': x}
    @property
    def SORT_ARRAY(self):
        """Sorts the input array in ascending order according to the natural ordering of the array elements and returns it."""
        if self.language == 'hive':
            return lambda x :{'array_sort': x}    
        return lambda x : {'sort_array': x}
    @property
    def LEVENSHTEIN(self):
        """Returns the Levenshtein distance between two strings."""
        if self.language == 'hive':
            return lambda x :{'levenshtein_distance': x}
        return lambda x : {'levenshtein': x}
    @property
    def INSTR(self):
        """instr(string str, string substr): Returns the position of the first occurrence of substr in str. """
        if self.language == 'hive' or self.language == 'impala':
            return lambda x :{'strpos': x} 
        return lambda x : {'instr': x}
    @property
    def CHARACTER_LENGTH(self):
        """Returns the number of UTF-8 characters contained in str."""
        if self.language == 'hive':
            return lambda x :{'length': x}
        return lambda x : {'character_length': x}
    @property
    def CHAR_LENGTH(self):
        """Hive: Shorthand for character_length."""
        if self.language == 'hive':
            return lambda x : self.CHARACTER_LENGTH(x)
        if self.language == 'impala':
            return lambda x : {'length': x}
        return lambda x : {'char_length': x}
    @property
    def UNBASE64(self):
        """Converts the argument from a base 64 string to BINARY."""
        if self.language == 'hive':
            return lambda x :{'from_base64': x} 
        return lambda x : {'unbase64': x}
    @property 
    def BASE64(self):
        """Converts the argument from binary to a base 64 string."""
        if self.language == 'hive':
            return lambda x :{'to_base64': x}    
        return lambda x : {'base64': x}
    @property
    def WEEKOFYEAR(self):
        """Returns the week number of a timestamp string: weekofyear("1970-11-01 00:00:00") = 44."""
        if self.language == 'hive' or self.language == 'impala':
            return lambda x :{'week': x} 
        return lambda x : {'weekofyear': x}
    @property
    def YEAR(self):
        """Returns the year part of a date or a timestamp string."""
        if self.language == 'hive':
            return lambda x :{'year': self.CAST([x, self.TIMESTAMP({})])}        
        return lambda x : {'year': x}
    @property
    def QUARTER(self):
        """Returns the quarter of the year for a date, timestamp, or string."""
        if self.language == 'hive':
            return lambda x :{'quarter': self.CAST([x, self.TIMESTAMP({})])}
        return lambda x : {'quarter': x}
    @property
    def MONTH(self):
        """Returns the month part of a date or a timestamp string."""
        if self.language == 'hive':
            return lambda x :{'month': self.CAST([x, self.TIMESTAMP({})])}    
        return lambda x : {'month': x}
    @property
    def DAYOFMONTH(self):
        """Hive:Returns the day part of a date or a timestamp string.
           Impala:Returns the day part of a date or a timestamp."""
        if self.language == 'hive':
            return lambda x :{'day_of_month': self.CAST([x, self.TIMESTAMP({})])}
        if self.language == 'impala':
            return lambda x :{'day_of_month': x}
        return lambda x : {'dayofmonth': x}
    @property
    def HOUR(self):
        """Returns the hour of the timestamp: hour('2009-07-30 12:58:59') = 12, hour('12:58:59') = 12"""
        if self.language == 'hive':
            return lambda x :{'hour': self.CAST([x, self.TIME({})])}
        return lambda x : {'hour': x}
    @property
    def MINUTE(self):
        """Returns the minute of the timestamp."""
        if self.language == 'hive':
            return lambda x :{'minute': self.CAST([x, self.TIME({})])}
        return lambda x : {'minute': x}
    @property
    def SECOND(self):
        """Returns the second of the timestamp."""
        if self.language == 'hive':
            return lambda x :{'seconds': self.CAST([x, self.TIME({})])}
        return lambda x : {'second': x}
    @property
    def FROM_UNIXTIME(self):
        """Hive: Converts the number of seconds from unix epoch to a string representing the timestamp of that moment
        in the current system time zone, SELECT FROM_UNIXTIME(1626441023) =  2021-07-16 13:10:23 <string
           Presto: FROM_UNIXTIME(1626441023) =  2021-07-16 13:10:23 <TIMESTAMP.
           Impala: FROM_UNIXTIME(1626441023, pattern 'yyyy-MM-dd HH:mm:ss.SSSSSS'/yyyy HH.mm.ss (SSSSSS)), possible solution:
        date_format(from_unixtime( 1626881535), '%d-%M-%y') -- 21-July-21. All patern changes."""
        if self.language == 'hive':
            return lambda x : self.CAST([{'from_unixtime': x}, self.TIMESTAMP({})])
        if self.language == 'impala':
            return MediumToImplement
        return lambda x : {'from_unixtime': x}
    @property
    def FLOOR(self):
        """Hive: Returns the maximum BIGINT that is equal or less than the argument. 
        Presto returns double."""
        if self.language == 'hive':
            return lambda x : self.CAST([{'floor': x},self.BIGINT({})])    
        return lambda x : {'floor': x}
    @property
    def CEIL(self):
        """Hive: Returns the minimum BIGINT that is equal or greater than the argument. 
        Presto returns double."""
        if self.language == 'hive':
            return lambda x : self.CAST([{'ceil': x},self.BIGINT({})])
        return lambda x : {'ceil': x}
    @property
    def CEILING(self):
        """Hive: Returns the minimum BIGINT that is equal or greater than the argument. 
        Presto returns double."""
        if self.language == 'hive':
            return lambda x : self.CEIL(x)
        return lambda x : {'ceiling': x}
    @property
    def DATE_ADD(self): 
        """Hive: Adds a number of days to startdate: date_add('2008-12-31', 1) = '2009-01-01'.
           Presto: date_add(unit, value, timestamp)
           Impala: date_add(now(), interval 6 hours), interval expressions are a problem here, the other date_add() option works just like Hive solution."""
        if self.language == 'hive':
            return lambda x :{'date_add':[{'literal':'day'},x[1],self.CAST([x[0], self.TIMESTAMP({})])]}
        if self.language == 'impala':
            return lambda x : Presto._DATE_ADD_(x)
        return lambda x : {'date_add': x}
    @property
    def YEARS_ADD(self):
        """Returns the value with the number of YEARS added to date."""
        if self.language == 'impala':
            return lambda x : {'date_add':[{'literal':'year'}, x[1], x[0]]}
        return lambda x : {'years_add': x}
    @property
    def YEARS_SUB(self):
        """Returns the value with the number of YEARS subtracted from date."""
        if self.language == 'impala':
            return lambda x : {'date_add':[{'literal':'year'}, - x[1], x[0]]}
        return lambda x : {'years_sub': x}
    @property
    def MONTHS_ADD(self):
        """Returns the value with the number of months added to date."""
        if self.language == 'impala':
            return lambda x : {'date_add':[{'literal':'month'}, x[1], x[0]]}
        return lambda x : {'months_add': x}
    @property
    def MONTHS_SUB(self):
        """Returns the value with the number of months subtracted from date."""
        if self.language == 'impala':
            return lambda x : {'date_add':[{'literal':'month'}, - x[1], x[0]]}
        return lambda x : {'months_sub': x}
    @property
    def WEEKS_ADD(self):
        """Returns the specified date and time plus some number of WEEKs.
           Presto: date_add('week', 5, '2008-12-31 09:12:00)"""
        if self.language == 'impala':
            return lambda x :{'date_add':[{'literal':'week'},x[1], x[0]]}
        return lambda x : {'weeks_add': x}
    @property
    def WEEKS_SUB(self):
        """Returns the specified date and time minus some number of weeks.
           Presto: date_add('week', -5, '2008-12-31 09:12:00)"""
        if self.language == 'impala':
            return lambda x :{'date_add':[{'literal':'week'}, -x[1], x[0]]}
        return lambda x : {'weeks_sub': x}
    @property
    def MINUTES_ADD(self):
        """Returns the specified date and time plus some number of minutes.
           Presto: date_add('minute', 5, '2008-12-31 09:12:00)"""
        if self.language == 'impala':
            return lambda x :{'date_add':[{'literal':'minute'},x[1], x[0]]}
        return lambda x : {'minutes_add': x}
    @property
    def MINUTES_SUB(self):
        """Returns the specified date and time minus some number of minutes.
           Presto: date_add('minute', -5, '2008-12-31 09:12:00)"""
        if self.language == 'impala':
            return lambda x :{'date_add':[{'literal':'minute'}, -x[1], x[0]]}
        return lambda x : {'minutes_sub': x}
    @property
    def SECONDS_ADD(self):
        """Returns the specified date and time plus some number of seconds.
           Presto: date_add('SECOND', 5, '2008-12-31 09:12:00)"""
        if self.language == 'impala':
            return lambda x :{'date_add':[{'literal':'second'},x[1], x[0]]}
        return lambda x : {'seconds_add': x}
    @property
    def SECONDS_SUB(self):
        """Returns the specified date and time minus some number of seconds.
           Presto: date_add('SECONDS', -5, '2008-12-31 09:12:00)"""
        if self.language == 'impala':
            return lambda x :{'date_add':[{'literal':'second'}, -x[1], x[0]]}
        return lambda x : {'seconds_sub': x}
    @property
    def DATE_SUB(self):
        """Hive:Subtracts a number of days to startdate: date_sub('2008-12-31', 1) = '2008-12-30'.
           Presto: date_add('day', -1, '2008-12-31')
           Impala: date_sub(now(), interval 6 hours), interval expressions are a problem here, the other date_sub() option works just like Hive solution."""
        if self.language == 'hive':
            return lambda x :{'date_add':[{'literal':'day'},-x[1],self.CAST([x[0], self.TIMESTAMP({})])]}  
        if self.language == 'impala':
            return lambda x : Presto._DATE_SUB_(x)        
        return lambda x : {'date_sub': x}
    @property
    def DATEDIFF(self):
        """Hive:Returns the number of days from startdate to enddate: datediff('2009-03-01', '2009-02-27') = 2.
           Presto: date_diff(unit, timestamp1/data, timestamp2/data)"""
        if self.language == 'hive' or self.language == 'impala':
            return lambda x :({'date_diff':[{'literal':'day'}, x[1],x[0]]} )
        return lambda x : {'datediff': x}
    @property
    def ADD_MONTHS(self):
        """Hive: Returns a string date by adding the number of months to the argument, 
        example, date:add_months('2009-08-31', 1) = '2009-09-30'.
           Presto: Returns a date: cast(date_add('month', value, timestamp) as varchar)"""
        if self.language == 'hive':
            return lambda x : self.CAST([{'date_add':[{'literal':'month'},x[1],x[0]]},self.VARCHAR({})])
        if self.language == 'impala':
            return lambda x : {'date_add':[{'literal':'month'}, x[1], x[0]]}
        return lambda x : {'add_months': x}
    @property
    def TO_DATE(self):
        """Returns a date object from a timestamp string: to_date('1970-01-01 00:00:00') = '1970-01-01' 
           Presto:cast(date_parse('1970-01-01 00:00:00','%Y-%m-%d %H:%i:%s') as date) """
        if self.language == 'hive':
            return lambda x : self.CAST([{'date_parse': [x, {'literal':'%Y-%m-%d %H:%i:%s'}]}, self.DATE({})])
        if self.language == 'impala':
            return lambda x : {'date': x}
        return lambda x : {'to_date': x}
    @property
    def DATE_FORMAT(self):
        """Converts a date/timestamp/string to a value of string in the format specified by the date format. 
        Example: date_format('2015-04-08', 'y') = '2015'.
           Presto:format_datetime(cast('2015-04-08' as timestamp), 'y')."""
        if self.language == 'hive':
            return lambda x : {'format_datetime':[self.CAST([x[0],self.TIMESTAMP({})]),x[1]]}
        return lambda x : {'date_format': x}
    @property
    def NVL(self):
        """Returns default value if value is null else returns value: nvl(T value, T default_value),
        default_value could be a literal or not on moz."""
        if self.language == 'hive' or self.language == 'impala':
            return lambda x : {'coalesce': [x[0], x[1]]}
        return lambda x : {'nvl': x}
    @property
    def REPEAT(self):
        """Repeats str n times: return string"""
        if self.language == 'hive':
            return lambda x : {'array_join': [{'repeat': [x[0],x[1]]}, {'literal': ' '}]}
        return lambda x : {'repeat': x}
    @property
    def SPACE(self):
        """Repeats space n times: return string"""
        if self.language == 'hive' or self.language == 'impala':
            return lambda x : {'array_join': [{'repeat': [{'literal': ' '}, x]}, {'literal': ''}]}
        return lambda x : {'space': x}
    @property
    def MD5(self):
        """Calculates an MD5 128-bit checksum for the string or binary (as of Hive 1.3.0). The value is returned
        as a string of 32 hex digits: md5('ABC') = '902fbdd2b1df0c4f70b4a5d23525e932'
           Presto: select to_hex(md5(cast('ABC' as varbinary))) =902FBDD2B1DF0C4F70B4A5D23525E932
        select lower(to_hex(md5(cast('ABC' as varbinary)))) = 902fbdd2b1df0c4f70b4a5d23525e932 """
        if self.language == 'hive':
            return lambda x : self.LOWER({'to_hex': {'md5': self.CAST([x, self.VARBINARY({})])}})
        return lambda x : {'md5': x}
    @property
    def CRC32(self):
        """Computes a cyclic redundancy check value for string or binary argument and returns bigint value.
        Example, crc32('ABC') = 2743272264."""
        if self.language == 'hive':
            return lambda x : {'crc32': self.CAST([x, self.VARBINARY({})])}
        return lambda x : {'crc32': x}
    @property
    def SHA1(self):
        """Calculates the SHA-1 digest for string or binary and returns the value as a hex string.
        Example, sha1('ABC') = '3c01bdbb26f358bab27f267924aa2c9a03fcfdb8'.
           Presto:  select lower(to_hex(sha1(cast('ABC' as varbinary)))) =  3c01bdbb26f358bab27f267924aa2c9a03fcfdb8"""
        if self.language == 'hive':
            return lambda x : self.LOWER({'to_hex': {'sha1': self.CAST([x, self.VARBINARY({})])}})
        return lambda x : {'sha1': x}
    @property
    def SHA(self):
        """Same as SHA1."""
        if self.language == 'hive':
            return lambda x : self.LOWER({'to_hex': {'sha1': self.CAST([x, self.VARBINARY({})])}})    
        return lambda x : {'sha': x}
    @property
    def GET_JSON_OBJECT(self): 
        """ Extracts json object from a json string based on json path specified, and returns json string of the extracted json object."""
        if self.language == 'hive':
            return lambda x : {'json_extract_scalar': x}
        return lambda x : {'get_json_object': x} 
    @property
    def ADDDATE(self):
        """Adds days to date and returns the new date value."""
        if self.language == 'impala':
            return lambda x : {'date_add': [{'literal':'day'}, x[1], x[0]]}
        return lambda x : {'adddate': x}
    @property
    def SUBDATE(self):
        """Substracts days to date and returns the new date value."""
        if self.language == 'impala':
            return lambda x : {'date_add': [{'literal':'day'}, - x[1], x[0]]}
        return lambda x : {'subdate': x}
    @property
    def BITAND(self):
        """Bitwise AND operation."""
        if self.language == 'impala':
            return lambda x :{'bitwise_and': x}
        return lambda x : {'bitand': x}
    @property
    def BITNOT(self):
        """Bitwise NOT operation."""
        if self.language == 'impala':
            return lambda x :{'bitwise_not': x}
        return lambda x : {'bitnot': x}
    @property
    def BITOR(self):
        """Bitwise OR operation."""
        if self.language == 'impala':
            return lambda x :{'bitwise_or': x}
        return lambda x : {'bitor': x}
    @property
    def BITXOR(self):
        """Bitwise XOR operation."""
        if self.language == 'impala':
            return lambda x :{'bitwise_xor': x}
        return lambda x : {'bitxor': x}
    @property
    def BTRIM(self):
        """Impala: Removes all instances of one or more characters from the start and end of a STRING value."""
        if self.language == 'impala':
            return lambda x : Presto._BTRIM_(x)
        return lambda x : {'btrim': x}
    @property
    def LOCATE(self):
        """ Returns the position (starting from 1) of the first occurrence of a substring within a longer string.
        The optional postition part does not work.. optionally after a particular position."""
        if self.language == 'impala':
            return lambda x : Presto._LOCATE_(x)
        return lambda x : {'locate': x}
    @property
    def DCEIL(self):
        """Same as ceil."""
        if self.language == 'impala':
            return lambda x :{'ceil': x}
        return lambda x : {'dceil': x}
    @property
    def DROUND(self):
        """Same as round."""
        if self.language == 'impala':
            return lambda x : self.ROUND(x)
        return lambda x : {'dround': x}
    @property
    def DAYNAME(self):
        """Returns the day name of the date argument. The range of return values is 'Sunday' to 'Saturday'."""
        if self.language == 'impala':
            return lambda x :{'format_datetime': [x, {'literal': 'E'}]}
        return lambda x : {'dayname': x}
    @property
    def MONTHNAME(self):
        """Returns the month name of the date argument."""
        if self.language == 'impala':
            return lambda x :{'format_datetime': [x, {'literal': 'MMMM'}]}
        return lambda x : {'monthname': x}
    @property
    def DAYOFYEAR(self):
        """Returns the day field from the date argument, corresponding to the day of the year. """
        if self.language == 'impala':
            return lambda x :{'day_of_year': x}
        return lambda x : {'dayofyear': x}
    @property
    def DAYS_ADD(self):
        """Returns the value with the number of days added to date."""
        if self.language == 'impala':
            return lambda x : {'date_add': [{'literal': 'day'}, x[1], x[0]]}
        return lambda x : {'days_add': x}
    @property
    def DAYS_SUB(self):
        """Returns the value with the number of days subtracted from date."""
        if self.language == 'impala':
            return lambda x : {'date_add': [{'literal': 'day'}, -x[1], x[0]]}
        return lambda x : {'days_sub': x}
    @property
    def HOURS_ADD(self):
        """Returns the specified date and time plus some number of hours."""
        if self.language == 'impala':
            return lambda x : {'date_add': [{'literal': 'hour'}, x[1], x[0]]}
        return lambda x : {'hours_add': x}
    @property
    def HOURS_SUB(self):
        """Returns the specified date and time minus some number of hours."""
        if self.language == 'impala':
            return lambda x : {'date_add': [{'literal': 'hour'}, -x[1], x[0]]}
        return lambda x : {'hours_sub': x}
    @property
    def INT_MONTHS_BETWEEN(self):
        """Returns the number of months from startdate to enddate, representing only the full months that passed."""
        if self.language == 'impala':
            return lambda x :{'date_diff':[{'literal':'month'},x[1],x[0]]} 
        return lambda x : {'int_months_between': x} 
    @property
    def DCEIL(self):
        """Same as ceil."""
        if self.language == 'impala':
            return lambda x :{'ceil': x}
        return lambda x : {'dceil': x}
    @property
    def DFLOOR(self):
        """Same as FLOOR."""
        if self.language == 'impala':
            return lambda x :{'floor': x}
        return lambda x : {'dfloor': x}
    @property
    def DLOG10(self):
        if self.language == 'impala':
            return lambda x : self.LOG10(x)
        return lambda x : {'dlog': x} 
    @property
    def DPOW(self):
        if self.language == 'impala':
            return lambda x : self.POW(x)
        return lambda x : {'dpow': x}
    @property
    def FPOW(self):
        if self.language == 'impala':
            return lambda x : self.POW(x)
        return lambda x : {'fpow': x}
    @property
    def VARIANCE_POP(self):
        if self.language == 'impala':
            return lambda x :{'VAR_POP': x}
        return lambda x : {'variance_pop': x} 
    @property
    def VARIANCE_SAMP(self):
        """Impala: Alias for VAR_SAMP()"""
        if self.language == 'impala':
            return lambda x :{'VAR_SAMP': x}
        return lambda x : {'variance_samp': x} 
    @property
    def STRRIGHT(self):
        """Returns the rightmost characters of the string. """
        if self.language == 'impala':
            return lambda x : {'substr':[x[0],- x[1]]}
        return lambda x : {'strright': x}
    @property
    def STRLEFT(self):
        """Returns the leftmost characters of the string. """
        if self.language == 'impala':
            return lambda x : {'substr':[x[0],1, x[1]]}
        return lambda x : {'strleft': x}
    @property
    def UTC_TIMESTAMP(self): 
        """Presto returns current_timestamp, without the brackets, as utc time zone. """
        if self.language == 'impala':
            return {'select': {'value': 'current_timestamp'}}
        return lambda x : {'utc_timestamp': x}
    @property
    def IFNULL(self):
        """ Alias for the ISNULL() function."""
        if self.language == 'impala':
            return lambda x : self.COALESCE(x)
        return lambda x : {'ifnull': x}
    @property
    def NULLIFZERO(self): 
        """Returns NULL if the numeric expression evaluates to 0, otherwise returns the result of the expression."""
        if self.language == 'impala':
            return lambda x : {'if':[{'eq': [ {'coalesce':[x,0]} , 0 ]},None, x]}
        return lambda x : {'nullifzero': x}
    @property
    def ZEROIFNULL(self):
        """ Returns 0 if the numeric expression evaluates to NULL, otherwise returns the result of the expression."""
        if self.language == 'impala':
            return lambda x : {'if':[{'eq': [ {'coalesce':[x,0]},0]},0, x]}
        return lambda x : {'zeroifnull': x}
    @property
    def IS_INF(self):
        if self.language == 'impala':
            return lambda x : {'is_infinite': x}
        return lambda x : {'is_inf': x}    
    @property
    def ISNULL(self):
        """Returns true if a is NULL and false otherwise."""
        if self.language == 'hive' or self.language == 'impala':
            return lambda x : {'coalesce': x} 
        return lambda x : {'isnull': x} 
    @property
    def ISTRUE(self):
        """Returns TRUE if the expression is TRUE. Returns FALSE if the expression is FALSE or NULL."""
        if self.language == 'impala':
            return lambda x : {'cast':[x,self.BOOLEAN({})]}
        return lambda x : {'istrue': x} 
    @property
    def ISFALSE(self):
        """Returns TRUE if the expression is FALSE. Returns FALSE if the expression is TRUE or NULL."""
        if self.language == 'impala':
            return lambda x : {'not': {'cast':[x,self.BOOLEAN({})]}}
        return lambda x : {'isfalse': x} 
    @property
    def QUOTIENT(self):
        """Returns the first argument divided by the second argument, discarding any fractional part."""
        if self.language == 'impala':
            return lambda x : self.ROUND([{'div': x}, {'literal': 0}])
        return lambda x : {'quotient': x} 
    @property
    def PRECISION(self):
        """Computes the precision (number of decimal digits) needed to represent the type of the argument expression as a DECIMAL value."""
        if self.language == 'impala':
            return lambda x : self.LENGTH(self.REPLACE([self.CAST([x, self.VARCHAR({})]),{'literal':'.'},{'literal':''}]))
        return lambda x : {'precision': x}
    @property
    def TO_TIMESTAMP(self):
        """Converts an integer or string representing a date/time value into the corresponding TIMESTAMP value."""
        if self.language == 'impala':
            return lambda x : Presto._TO_TIMESTAMP_(x)
        return lambda x : {'to_timestamp': x}
    @property
    def DIV(self):
        """Returns the integer part of division. Example 15 div 2 returns 7
           Presto: 15/7 returns 7. Mo parse / as div."""
        if self.language == 'impala':
            return lambda x : {'div': x}
        return lambda x : {'div': x}
    @property
    def NVL2(self):
        """Returns the second argument, ifNotNull, if the first argument is not NULL. Returns the third argument, ifNull, if the first argument is NULL."""
        if self.language == 'impala':
            return EasyToImplement
            #return lambda x : self.IF([x])
        return lambda x : {'nvl2': x}
    @property
    def ISNOTFALSE(self):
        """Tests if a Boolean expression is not FALSE (that is, either TRUE or NULL). Returns TRUE if so. If the argument is NULL, returns TRUE."""
        if self.language == 'impala':
            return lambda x : self.CAST([x, self.BOOLEAN({})])
        return lambda x : {'isnotfalse': x} 
    @property
    def ISNOTTRUE(self):
        """Tests if a Boolean expression is not TRUE (that is, either FALSE or NULL). Returns TRUE if so. If the argument is NULL, returns TRUE."""
        if self.language == 'impala':
            return lambda x : {'not': {'cast':[x,self.BOOLEAN({})]}}
        return lambda x : {'isnottrue': x}
    @property
    def NULLVALUE(self):
        """Returns TRUE if the expression is NULL, and returns FALSE otherwise."""
        if self.language == 'impala':
            return lambda x : {'if': [{'eq':[x, None]}, True, False]}
        return lambda x : {'nullvalue': x}
    @property
    def NONNULLVALUE(self):
        """Returns TRUE if the expression is non-null and returns FALSE if the expression is NULL."""
        if self.language == 'impala':
            return lambda x : {'if': [{'eq':[x, None]}, False, True]}
        return lambda x : {'nonnullvalue': x}   
    @property
    def RIGHT(self):
        """Same as STRRIGHT(). RIGHT() breaks mo-sql-parsing."""
        if self.language == 'impala':
            return lambda x : {'substr':[x[0],- x[1]]}
        return lambda x : {'right': x}
    @property
    def LEFT(self):
        """Same as STRLEFT(). LEFT() breaks mo-sql-parsing."""
        if self.language == 'impala':
            return lambda x : {'substr':[x[0],1, x[1]]}
        return lambda x : {'left': x}
    @property
    def SCALE(self):
        """Computes the scale (number of decimal digits to the right of the decimal point) needed to represent the type of the argument expression as a DECIMAL value."""
        if self.language == 'impala': 
            return EasyToImplement
        return lambda x : {'scale': x}
    @property
    def MAX_INT(self):
        """Returns the largest value of the associated integral type."""
        if self.language == 'impala':
            return EasyToImplement
        return lambda x : {'max_int': x} 
    @property
    def MAX_TINYINT(self):
        """Returns the largest value of the associated integral type."""
        if self.language == 'impala':
            return EasyToImplement
        return lambda x : {'max_tinyint': x}
    @property
    def MAX_SMALLINT(self):
        """Returns the largest value of the associated integral type."""
        if self.language == 'impala':
            return EasyToImplement
        return lambda x : {'max_smallint': x}
    @property
    def MAX_BIGINT(self):
        """Returns the largest value of the associated integral type."""
        if self.language == 'impala':
            return EasyToImplement
        return lambda x : {'max_bigint': x}
    @property
    def MIN_INT(self):
        """Returns the smallest value of the associated integral type (a negative number)."""
        if self.language == 'impala':
            return EasyToImplement
        return lambda x : {'min_int': x}
    @property
    def MIN_TINYINT(self):
        """Returns the smallest value of the associated integral type (a negative number)."""
        if self.language == 'impala':
            return EasyToImplement
        return lambda x : {'min_tinyint': x}
    @property
    def MIN_SMALLINT(self):
        """Returns the smallest value of the associated integral type (a negative number)."""
        if self.language == 'impala':
            return EasyToImplement
        return lambda x : {'min_smallint': x}
    @property
    def MIN_BIGINT(self):
        """Returns the smallest value of the associated integral type (a negative number)."""
        if self.language == 'impala':
            return EasyToImplement
        return lambda x : {'min_bigint': x}
    @property
    def MICROSECONDS_SUB(self):
        if self.language == 'impala':
            return EasyToImplement
        return lambda x : {'microseconds_sub': x}
    @property
    def MICROSECONDS_ADD(self):
        if self.language == 'impala':
            return EasyToImplement
        return lambda x : {'microseconds_add': x}
    @property
    def MILLISECOND(self):
        if self.language == 'impala':
            return EasyToImplement
        return lambda x : {'millisecond': x}
    @property
    def MILLISECONDS_ADD(self):
        if self.language == 'impala':
            return EasyToImplement
        return lambda x : {'milliseconds_add': x}
    @property
    def MILLISECONDS_SUB(self):
        if self.language == 'impala':
            return EasyToImplement
        return lambda x : {'milliseconds_sub': x}
    @property
    def NANOSECONDS_ADD(self):
        if self.language == 'impala':
            return EasyToImplement
        return lambda x : {'nanoseconds_add': x}
    @property
    def NANOSECONDS_SUB(self):
        if self.language == 'impala':
            return EasyToImplement
        return lambda x : {'nanoseconds_sub': x}
    @property
    def FMOD(self):
        """ Returns the modulus of a floating-point number.
            Presto: Attention when using negative values"""
        if self.language == 'impala':
            return EasyToImplement
        return lambda x : {'fmod': x}
    @property
    def EFFECTIVE_USER(self):
        """ Typically returns the same value as USER(). If delegation is enabled, it returns the ID of the delegated user.
            Athena:'Function current_user not registered'"""
        if self.language == 'impala':
            return EasyToImplement
        return lambda x : {'effective_user': x}
    @property
    def DAYOFWEEK(self):
        """Impala: Returns the day field of the date arguement, corresponding to the day of the week. 
        The range of return values is 1 (Sunday) to 7 (Saturday).
           Presto: Returns the ISO day of the week. The value ranges from 1 (Monday) to 7 (Sunday)."""
        if self.language == 'impala':
            return EasyToImplement
        return lambda x : {'dayofweek': x}
    @property
    def EXTRACT(self):
        """Hive: Retrieve fields from source. Differences to Presto: unit name (dayofweek) and the start day of the week, Hive starts on sunday
        and Presto on Monday, example, extract(day_of_week from '2016-10-20 00:20:02'); returns 5 in Hive and 4 in Presto. """
        if self.language == 'hive':
            return MediumToImplement
        if self.language == 'impala':
            return lambda x : Presto._EXTRACT_(x)
        return lambda x : {'extract': x} 
    @property
    def LOGGED_IN_USER(self):
        """Hive: Returns current user name from the session state.
           Presto: Returns the current user running the query with select current_user
           Athena complets the query as "select current_user()" but throws the error: 'Function current_user not registered'"""
        if self.language == 'hive':
            return EasyToImplement
        return lambda x : {'logged_in_user': x} 
    @property
    def HEX(self):
        """HEX(bigint/string/binary a): hex returns the number as a STRING in hexadecimal format if its a int or a binary. Otherwise if the number is a STRING,
        it converts each character into its hexadecimal representation and returns the resulting STRING.
        Presto: to_hex(varbinary), does not accept int or string."""
        if self.language == 'hive' or self.language == 'impala':
            return EasyToImplement
        return lambda x : {'hex': x} 
    @property
    def UNHEX(self):
        """Hive: Interprets each pair of characters as a hexadecimal number and converts to the byte representation of the number.
        Presto: from_hex(varbinary/varchar), Athena throws an error with a varchar argument.
        Options: to_base(255,16) and from_base('ff',16)"""
        if self.language == 'hive' or self.language == 'impala':
            return EasyToImplement
        return lambda x : {'unhex': x} 
    @property
    def POSITIVE(self):
        """Returns the the argument with the positive sign. If the argument is negative, the sign remains."""
        if self.language == 'hive' or self.language == 'impala':
            return EasyToImplement
        return lambda x : {'positive': x}
    @property
    def NEGATIVE(self): 
        """Hive: Returns the the argument with the negative sign. If the argument is negative, the result is positive."""
        if self.language == 'hive' or self.language == 'impala':
            return EasyToImplement
        return lambda x : {'negative': x} 
    @property
    def SLEEP(self): 
        """Pauses the query for a specified number of milliseconds. """
        if self.language == 'impala':
            return EasyToImplement
        return lambda x : {'sleep': x} 
    @property
    def NDV(self): 
        """Impala: An aggregate function that returns an approximate value similar to the result of COUNT(DISTINCT col), the "number of distinct values"."""
        if self.language == 'impala':
            return EasyToImplement
        return lambda x : {'ndv': x} 
    @property
    def CURRENT_TIMESTAMP(self): 
        """Hive: select current_timestamp =2021-07-16 12:28:20.711
           Presto: select current_timestamp = 2021-07-16 12:28:51.490 UTC 
           Impala: current_timestamp() = 2021-07-16 12:32:20.806619000 
           They returned the same timestamp when running a query."""
        if self.language == 'impala':
            return {'select': {'value': 'current_timestamp'}}
        return lambda x : {'current_timestamp': x}
    @property
    def VAR_POP(self):
        """Returns the variance of a numeric column in the group.
           Presto has the same name but it was not tested"""
        if self.language == 'hive':
            return EasyToImplement
        return lambda x : {'var_pop': x} 
    @property
    def VAR_SAMP(self):
        """Hive: Returns the unbiased sample standard deviation of a numeric column in the group.
        Hive to Presto was not tested on the SQL engine.
           Presto/Impala: Returns the sample variance of all input values."""
        if self.language == 'hive':
            return EasyToImplement
        return lambda x : {'var_samp': x} 
    @property
    def COVAR_POP(self):
        """Returns the population covariance of a pair of numeric columns in the group.
           Presto has the same name but it was not tested"""
        if self.language == 'hive':
            return EasyToImplement
        return lambda x : {'covar_pop': x} 
    @property
    def COVAR_SAMP(self):
        """Returns the unbiased sample variance of a numeric column in the group.
           Presto has the same name but it was not tested"""
        if self.language == 'hive':
            return EasyToImplement
        return lambda x : {'covar_samp': x} 
    @property
    def STDDEV_POP(self):
        """Returns the standard deviation of a numeric column in the group.
           Presto has the same name but it was not tested."""
        if self.language == 'hive':
            return EasyToImplement
        return lambda x : {'stddev_pop': x} 
    @property
    def STDDEV_SAMP(self):
        """Returns the unbiased sample standard deviation of a numeric column in the group.
           Presto has the same name but it was not tested."""
        if self.language == 'hive':
            return EasyToImplement
        return lambda x : {'stddev_samp': x} 
    @property
    def CORR(self):
        """Returns the Pearson coefficient of correlation of a pair of a numeric columns in the group.
           Presto has the same name but did not say what/from who is the coefficient."""
        if self.language == 'hive':
            return EasyToImplement
        return lambda x : {'corr': x} 
    @property
    def REGR_SLOPE(self):
        """Returns the slope of the linear regression line
           Presto has the same name but was not tested."""
        if self.language == 'hive':
            return EasyToImplement
        return lambda x : {'regr_slope': x} 
    @property
    def REGR_INTERCEPT(self):
        """Returns the y-intercept of the linear regression line.
           Presto has the same name but was not tested."""
        if self.language == 'hive':
            return EasyToImplement
        return lambda x : {'regr_intercept': x} 
    @property
    def PMOD(self):
        """Returns the positive value of a mod b.
        Point of attention: depending where the negative argument is, the result is negative."""
        if self.language == 'hive' or self.language == 'impala':
            return EasyToImplement
        return lambda x : {'pmod': x} 
    @property
    def PERCENTILE(self):
        """Returns the exact pth percentile of a column in the group. Presto calculates only the approx"""
        if self.language == 'hive':
            return EasyToImplement
        return lambda x : {'percentile': x} 
    @property
    def PERCENTILE_APPROX(self):
        """Returns an approximate pth percentile of a numeric column. Test Presto approx_percentile()"""
        if self.language == 'hive':
            return EasyToImplement
        return lambda x : {'percentile_approx': x} 
    @property
    def REGR_AVGX(self): 
        """Equivalent to avg(dependent)."""
        if self.language == 'hive':
            return EasyToImplement
        return lambda x : {'regr_avgx': x} 
    @property
    def REGR_AVGY(self):
        """Equivalent to avg(independent)."""
        if self.language == 'hive':
            return EasyToImplement
        return lambda x : {'regr_avgy': x} 
    @property
    def DATE_PART(self):
        """Impala: Similar to extract(), example, date_part('day', '2016-05-20 11:21:30.491').
           Presto: extract(day from '2016-10-20 00:20:02'). Does not work with 'epoch' and 'millisecond' units."""
        if self.language == 'impala':
            return lambda x : Presto._DATE_PART_(x)
        return lambda x : {'date_part': x} 
    @property
    def TIMEOFDAY(self):
        """ Returns a string representation of the current date and time, according to the time of the local system, including any time zone designation.
        Ex : Thu Jul 22 16:22:43 2021 UTC"""
        if self.language == 'impala':
            return EasyToImplement
        return lambda x : {'timeofday': x} 
    @property
    def TIMESTAMP_CMP(self):
        """ Tests if one TIMESTAMP value is newer than, older than, or identical to another TIMESTAMP."""
        if self.language == 'impala':
            return EasyToImplement
        return lambda x : {'timestamp_cmp': x} 
    @property
    def GROUP_CONCAT(self):
        """ Impala: Returns a single string representing the argument value concatenated together for each row of the result set.
        If the optional separator string is specified, the separator is added between each pair of concatenated values."""
        if self.language == 'impala':
            return MediumToImplement
        return lambda x : {'group_concat': x}
    @property
    def MONTHS_BETWEEN(self):
        """Hive/Impala: Returns the difference (double) of months between two dates/timestamps, example:
        months_between('1997-02-28 10:30:00', '1996-10-30') = 3.94959677
           Presto: date_diff() returns a bigint"""
        if self.language == 'hive' or self.language == 'impala' :
            return MediumToImplement
        return lambda x : {'months_between': x} 
    @property
    def FROM_TIMESTAMP(self):
        """Impala: Converts a TIMESTAMP value into a string representing the same value, from_timestamp('2021-03-12','dd/MM/yyyy HH:mm:ss.SSSS').
        Presto: date_format(cast('2021-03-12' as timestamp),'%d/%M/%y %h:%m:%s.SSS'). Patterns to format are not the same."""
        if self.language == 'impala':
            return MediumToImplement
        return lambda x : {'from_timestamp': x}
    @property
    def TRUNC(self):
        """Hive: Returns (string) date truncated to the unit specified by the format. Formats:MONTH/MON/MM, YEAR/YYYY/YY. 
        Example: trunc('2015-03-17', 'MM') = 2015-03-01."""
        if self.language == 'impala' or self.language == 'hive':
            return lambda x : Presto._TRUNC_(x)
        return lambda x : {'trunc': x} 
    @property
    def DATE_TRUNC(self): 
        """Returns the ts value truncated to the specified unit. 
           Presto:Does not have: microseconds, miliseconds, decade, century and millennium units."""
        if self.language == 'impala':
            return lambda x : Presto._DATE_TRUNC_(x)
        return lambda x : {'date_trunc': x} 
    @property
    def TRUNCATE(self):
        """Impala: Removes some or all fractional digits from a numeric value."""
        if self.language == 'impala':
            return lambda x : Presto._TRUNCATE_(x)
        return lambda x : {'truncate': x} 
    @property
    def DTRUNC(self):
        """Impala: Removes some or all fractional digits from a numeric value."""
        if self.language == 'impala':
            return lambda x : Presto._TRUNCATE_(x)
        return lambda x : {'dtrunc': x} 
    @property
    def FACTORIAL(self):
        """Returns the factorial of argument."""
        if self.language == 'hive' or self.language == 'impala':
            return MediumToImplement
        return lambda x : {'factorial': x} 
    @property
    def NEXT_DAY(self):
        """Returns the first date which is later than start_date and named as day_of_week."""
        if self.language == 'hive' or self.language == 'impala':
            return MediumToImplement
        return lambda x : {'next_day': x} 
    @property
    def LAST_DAY(self):
        """Returns the last day of the month which the date belongs to."""
        if self.language == 'hive':
            return MediumToImplement
        return lambda x : {'last_day': x} 
    @property
    def BROUND(self):
        """Returns the rounded BIGINT value of a using HALF_EVEN rounding mode. Gaussian rounding.
        Example, bround(2.5) = 2, bround(3.5) = 4."""
        if self.language == 'hive':
            return MediumToImplement
        return lambda x : {'bround': x} 
    @property
    def LOG(self):
        """Returns the base-base logarithm of the argument."""
        if self.language == 'hive' or self.language == 'impala':
            return MediumToImplement
        return lambda x : {'log': x} 
    @property
    def ASCII(self):
        """Returns the numeric value of the first character of str."""
        if self.language == 'hive' or self.language == 'impala':
            return MediumToImplement
        return lambda x : {'ascii': x} 
    @property
    def OCTET_LENGTH(self):
        """Returns the number of octets required to hold the string str in UTF-8 encoding."""
        if self.language == 'hive':
            return MediumToImplement
        return lambda x : {'octet_length': x} 
    @property
    def PRINTF(self):
        """Returns the input formatted according do printf-style format strings."""
        if self.language == 'hive':
            return MediumToImplement
        return lambda x : {'printf': x} 
    @property
    def INITCAP(self):
        """Returns string, with the first letter of each word in uppercase, all other letters in lowercase.
         Wroks on Presto but not on mo_sql: array_join((transform((split('name name2 last name',' ')), x -> concat(upper(substr(x,1,1)),substr(x,2,length(x))))),' ',' ')"""
        if self.language == 'hive' or self.language == 'impala':
            return MediumToImplement
        return lambda x : {'initcap': x} 
    @property
    def COLLECT_SET(self):
        """Returns a set of objects with duplicate elements eliminated."""
        if self.language == 'hive':
            return MediumToImplement
        return lambda x : {'collect_set': x} 
    @property
    def COLLECT_LIST(self):
        """Returns a list of objects with duplicates."""
        if self.language == 'hive':
            return MediumToImplement
        return lambda x : {'collect_list': x} 
    @property
    def SURROGATE_KEY(self):
        """Automatically generate numerical Ids for rows as you enter data into a table."""
        if self.language == 'hive':
            return MediumToImplement
        return lambda x : {'surrogate_key': x} 
    @property
    def SUBSTRING(self):
        """Returns the substring from string A before count occurrences of the delimiter delim. 
        substring_index(string A, string delim, int count).
           Presto split_part() may be useful"""
        if self.language == 'hive':
            return MediumToImplement
        return lambda x : {'substring': x} 
    @property
    def HISTOGRAM_NUMERIC(self):
        """Computes a histogram of a numeric column in the group using b non-uniformly spaced bins.
           Presto numeric_histogram()"""
        if self.language == 'hive':
            return MediumToImplement
        return lambda x : {'histogram_numeric': x} 
    @property
    def CONCAT_WS(self):
        """Hive:Like concat(), but with custom separator SEP."""
        if self.language == 'hive' or self.language == 'impala':
            return MediumToImplement
        return lambda x : {'concat_ws': x} 
    @property
    def ELT(self):
        """Return string at index number. For example elt(2,'hello','world') returns 'world'."""
        if self.language == 'hive':
            return MediumToImplement
        return lambda x : {'elt': x} 
    @property
    def FIELD(self):
        """Returns the index of val in the val1,val2,val3,... list or 0 if not found. 
        Example, field('world','say','hello','world') returns 3. """
        if self.language == 'hive':
            return MediumToImplement
        return lambda x : {'field': x} 
    @property
    def FIND_IN_SET(self):
        """Returns the first occurance of str in strList where strList is a comma-delimited string.
        Example, find_in_set('ab', 'abc,b,ab,c,def') returns 3. """
        if self.language == 'hive' or self.language == 'impala':
            return MediumToImplement
        return lambda x : {'find_in_set': x} 
    @property
    def IN_FILE(self):
        """Returns true if the string str appears as an entire line in filename. """
        if self.language == 'hive':
            return MediumToImplement
        return lambda x : {'in_file': x}
    @property
    def TRANSLATE(self):
        """Translates the input string by replacing the characters present in the from string with the corresponding 
        characters in the to string."""
        if self.language == 'hive' or self.language == 'impala':
            return MediumToImplement
        return lambda x : {'translate': x}
    @property
    def STR_TO_MAP(self):
        """Hive: Splits text into key-value pairs using two delimiters.
           Presto: a similar could be split_to_map"""
        if self.language == 'hive':
            return MediumToImplement
        return lambda x : {'str_to_map': x}
    @property
    def APPX_MEDIAN(self):
        """ An aggregate function that returns a value that is approximately the median (midpoint) of values in the set of input values."""
        if self.language == 'impala':
            return MediumToImplement
        return lambda x : {'appx_median': x}
    @property
    def COUNTSET(self):
        """By default, returns the number of 1 bits in the specified integer value. If the optional second argument is set to zero, it returns the number of 0 bits instead. """
        if self.language == 'impala':
            return MediumToImplement
        return lambda x : {'countset': x}
    @property
    def CONV(self):
        """conv(BIGINT num, INT from_base, INT to_base):Converts a number from a given base to another."""
        if self.language == 'hive'or self.language == 'impala':
            return MediumToImplement
        return lambda x : {'conv': x}
    @property
    def GETBIT(self):
        """Returns a 0 or 1 representing the bit at a specified position."""
        if self.language == 'impala':
            return MediumToImplement
        return lambda x : {'getbit': x} 
    @property
    def UNIX_TIMESTAMP(self):
        """Hive/Impala: unix_timestamp(): Gets current Unix timestamp in seconds.
           Hive/Impala:unix_timestamp(string date): Converts time string in format yyyy-MM-dd HH:mm:ss to Unix timestamp, 
        using the default timezone and the default locale. 

           Hive/Impala:unix_timestamp(string date, string pattern): Convert time string with given pattern. Example,
        unix_timestamp('2015-05-15 12:00:00-07:00', 'yyyy-MM-dd HH:mm:ss-hh:mm')
           Presto: select to_unixtime(date_parse('2015-05-15 12:00:00 - 07:00', '%Y-%m-%d %H:%i:%s - %H:%i')) PATTERN IS A PROBLEM
           """
        if self.language == 'hive' or self.language == 'impala':
            return lambda x : Presto._UNIX_TIMESTAMP_(x)
        return lambda x : {'unix_timestamp': x}
    @property
    def FROM_UTC_TIMESTAMP(self):
        """Hive: Converts a timestamp* in UTC to a given timezone. Example:from_utc_timestamp(2592000000,'PST') and
        from_utc_timestamp(timestamp '1970-01-30 16:00:00','PST') return the timestamp 1970-01-30 08:00:00.
           Presto: Uses the operator AT TIME ZONE for timezones types and from_unixtime for unixtime """
        if self.language == 'hive' or self.language == 'impala':
            return HardToImplement
        return lambda x : {'from_utc_timestamp': x}
    @property
    def TO_UTC_TIMESTAMP(self):
        """Hive: Converts a timestamp* in a given timezone to UTC. Example:to_utc_timestamp(2592000000,'PST') 
        and to_utc_timestamp(timestamp '1970-01-30 16:00:00','PST').
           Presto: Uses the operator AT TIME ZONE for timezones types and to_unixtime for unixtime. Also,
           the time zones are set different, PST in Presto it seems to be PST8PDT in Athena."""
        if self.language == 'hive' or self.language == 'impala':
            return HardToImplement
        return lambda x : {'to_utc_timestamp': x}
    @property
    def BINARY(self):
        """binary(string|binary): casts the xeter into a binary."""
        if self.language == 'hive':
            return HardToImplement
        return lambda x : {'binary': x}
    @property
    def BIN(self):
        """bin(BIGINT a): Returns the number in binary format (string).
        Presto: did not cast integer to binary"""
        if self.language == 'hive' or self.language =='impala':
            return HardToImplement
        return lambda x : {'bin': x}
    @property
    def SHIFTLEFT(self):
        """Bitwise left shift."""
        if self.language == 'hive' or self.language == 'impala':
            return HardToImplement 
        return lambda x : {'shiftleft': x}
    @property
    def SHIFRIGHT(self):
        """Bitwise right shift."""
        if self.language == 'hive' or self.language == 'impala':
            return HardToImplement
        return lambda x : {'shiftright': x}
    @property
    def SHIFRIGHTUNSIGNED(self):
        """Bitwise unsigned right shift."""
        if self.language == 'hive':
            return HardToImplement
        return lambda x : {'shiftrightunsigned': x}
    @property
    def ISNOTNULL(self): 
        """Hive:Returns true if a is not NULL and false otherwise.
           Presto: Operator IS NOT NULL"""
        if self.language == 'hive':
            return HardToImplement
        return lambda x : {'isnotnull': x} 
    @property
    def ENCODE(self):
        """Encodes the first argument into a BINARY using the provided character set (one of 'US-ASCII',
        'ISO-8859-1', 'UTF-8', 'UTF-16BE', 'UTF-16LE', 'UTF-16')."""
        if self.language == 'hive':
            return HardToImplement
        return lambda x : {'encode': x} 
    @property
    def DECODE(self):
        """Hive: Decodes the first argument into a String using the provided character set (one of 'US-ASCII', 
        'ISO-8859-1', 'UTF-8', 'UTF-16BE', 'UTF-16LE', 'UTF-16').
           Impala: Compares the first argument, expression, to the search expressions using the IS NOT DISTINCT operator, and returns:
        - The corresponding result when a match is found.
        - The first corresponding result if there are more than one matching search expressions.
        - The default expression if none of the search expressions matches the first argument expression.
        - NULL if the final default expression is omitted and none of the search expressions matches the first argument."""
        if self.language == 'hive' or self.language == 'impala':
            return HardToImplement
        return lambda x : {'decode': x} 
    @property
    def CONTEXT_NGRAMS(self):
        """Returns the top-k contextual N-grams from a set of tokenized sentences."""
        if self.language == 'hive':
            return HardToImplement
        return lambda x : {'context_ngrams': x} 
    @property
    def NGRAMS(self):
        """Returns the top-k N-grams from a set of tokenized sentences, such as those returned by the sentences() UDAF."""
        if self.language == 'hive':
            return HardToImplement
        return lambda x : {'ngrams': x} 
    @property
    def SENTENCES(self):
        """Tokenizes a string of natural language text into words and sentences, for example, 
        sentences('Hello there! How are you?') returns ( ("Hello", "there"), ("How", "are", "you") )"""
        if self.language == 'hive':
            return HardToImplement
        return lambda x : {'sentences': x} 
    @property
    def SHA2(self):
        """Calculates the SHA-2 family of hash functions.
        Presto only implements 256 and 512."""
        if self.language == 'hive':
            return HardToImplement
        return lambda x : {'sha2': x} 
    @property
    def REGR_SXX(self):
        """Equivalent to regr_count"""
        if self.language == 'hive':
            return HardToImplement
        return lambda x : {'regr_sxx': x} 
    @property
    def REGR_SXY(self):
        """Equivalent to regr_count"""
        if self.language == 'hive':
            return HardToImplement
        return lambda x : {'regr_sxy': x} 
    @property
    def REGR_SYY(self):
        """Equivalent to regr_count"""
        if self.language == 'hive':
            return HardToImplement
        return lambda x : {'regr_syy': x} 
    @property
    def REGR_COUNT(self):
        """Returns the number of non-null pairs used to fit the linear regression line."""
        if self.language == 'hive':
            return HardToImplement
        return lambda x : {'regr_count': x} 
    @property
    def REGR_R2(self):
        """Returns the coefficient of determination for the regression."""
        if self.language == 'hive':
            return HardToImplement
        return lambda x : {'regr_r2': x} 
    @property
    def SOUNDEX(self):
        """Returns soundex code of the string. For example, soundex('Miller') results in M460."""
        if self.language == 'hive':
            return HardToImplement
        return lambda x : {'soundex': x} 
    @property
    def REFLECT(self):
        """Calls a Java method by matching the argument signature, using reflection."""
        if self.language == 'hive':
            return HardToImplement
        return lambda x : {'reflect': x} 
    @property
    def HASH(self):
        """Returns a hash value of the arguments. """
        if self.language == 'hive':
            return HardToImplement
        return lambda x : {'hash': x} 
    @property
    def QUOTE(self):
        """Returns the quoted string (Includes escape character for any single quotes HIVE-4."""
        if self.language == 'hive':
            return HardToImplement
        return lambda x : {'quote': x} 
    @property
    def AES_ENCRYPT(self):
        """Encrypt input using AES."""
        if self.language == 'hive':
            return HardToImplement
        return lambda x : {'aes_encrypt': x} 
    @property
    def AES_DECRYPT(self):
        """Decrypt input using AES."""
        if self.language == 'hive':
            return HardToImplement
        return lambda x : {'aes_decrypt': x} 
    @property
    def CURRENT_DATABASE(self):
        """Returns current database name."""
        if self.language == 'hive' or self.language == 'impala':
            return HardToImplement
        return lambda x : {'current_database': x} 
    @property
    def VERSION(self):
        """Returns the Hive version ."""
        if self.language == 'hive' or self.language == 'impala':
            return HardToImplement
        return lambda x : {'version': x} 
    @property
    def UUID(self):
        """ Returns a universal unique identifier, a 128-bit value encoded as a string with groups of hexadecimal digits separated by dashes."""
        if self.language == 'impala':
            return HardToImplement
        return lambda x : {'uuid': x} 
    @property
    def PARSE_URL(self):
        """Returns the specified part from the URL.
           Presto: has specific functions like url_extract_fragment/host/parameter(url) to do something like parse_url."""
        if self.language == 'hive' or self.language == 'impala':
            return HardToImplement
        return lambda x : {'parse_url': x} 
    @property
    def VARIANCE(self):
        """Hive:Returns the variance of a numeric column in the group.
        Presto/Impala: Returns the sample variance of all input values."""
        if self.language == 'hive':
            return HardToImplement
        return lambda x : {'variance': x} 
    @property
    def ASSERT_TRUE(self):
        """Throw an exception if 'condition' is not true, otherwise return null."""
        if self.language == 'hive':
            return HardToImplement
        return lambda x : {'assert_true': x} 
    @property 
    def CURRENT_USER(self): 
        """Returns current user name from the configured authenticator manager."""
        if self.language == 'hive':
            return HardToImplement 
        return lambda x : {'current_user': x} 
    @property
    def BASE64DECODE(self):
        """Impala:All return values produced by BASE64ENCODE() are a multiple of 4 bytes in length."""
        if self.language == 'impala':
            return HardToImplement
        return lambda x : {'base64decode': x}
    @property
    def BASE64ENCODE(self):
        """Impala:All return values produced by BASE64ENCODE() are a multiple of 4 bytes in length."""
        if self.language == 'impala':
            return HardToImplement
        return lambda x : {'base64encode': x}
    @property
    def COSH(self):
        """Returns the hyperbolic cosine of the argument."""
        if self.language == 'impala':
            return HardToImplement
        return lambda x : {'cosh': x}
    @property
    def COT(self):
        """Returns the cotangent of the argument."""
        if self.language == 'impala':
            return HardToImplement
        return lambda x : {'cot': x} 
    @property
    def FNV_HASH(self):
        """ Returns a consistent 64-bit value derived from the input argument, for convenience of implementing hashing logic in an application."""
        if self.language == 'impala':
            return HardToImplement
        return lambda x : {'fnv_hash': x}
    @property
    def JARO_DISTANCE(self):
        """Returns the Jaro distance between two input strings."""
        if self.language == 'impala':
            return HardToImplement
        return lambda x : {'jaro_distance': x} 
    @property
    def JARO_DIST(self):
        """Shorthand for JARO_DISTANCE."""
        if self.language == 'impala':
            return HardToImplement
        return lambda x : {'jaro_dist': x} 
    @property
    def JARO_SIMILARITY(self):
        """Returns the Jaro similarity of two strings."""
        if self.language == 'impala':
            return HardToImplement
        return lambda x : {'jaro_similarity': x} 
    @property
    def JARO_SIM(self):
        """Shorthand for JARO_SIMILARITY."""
        if self.language == 'impala':
            return HardToImplement
        return lambda x : {'jaro_sim': x} 
    @property
    def JARO_WINKER_DISTANCE(self):
        """Returns the Jaro-Winkler distance of two input strings."""
        if self.language == 'impala':
            return HardToImplement
        return lambda x : {'jaro_winker_distance': x} 
    @property
    def JW_DST(self):
        """Returns the Jaro-Winkler distance of two input strings."""
        if self.language == 'impala':
            return HardToImplement
        return lambda x : {'jw_dst': x}
    @property
    def JARO_WINKER_SIMILARITY(self):
        """ Returns the Jaro-Winkler Similarity between two input strings"""
        if self.language == 'impala':
            return HardToImplement
        return lambda x : {'jaro_winker_similarity': x} 
    @property
    def JW_SIM(self):
        """ Returns the Jaro-Winkler Similarity between two input strings"""
        if self.language == 'impala':
            return HardToImplement
        return lambda x : {'jw_sim': x} 
    @property
    def MURMUR_HASH(self):
        """Returns a consistent 64-bit value derived from the input argument, 
        for convenience of implementing MurmurHash2 non-cryptographic hash function."""
        if self.language == 'impala':
            return HardToImplement
        return lambda x : {'murmur_hash': x}
    @property
    def PID(self):
        """Returns the process ID of the impalad daemon that the session is connected to. You can use it during low-level debugging, to issue Linux commands that trace, show the arguments, and so on the impalad process."""
        if self.language == 'impala':
            return HardToImplement
        return lambda x : {'pid': x} 
    @property
    def SINH(self):
        """Returns the hyperbolic sin of the argument."""
        if self.language == 'impala':
            return HardToImplement
        return lambda x : {'sinh': x}
    @property
    def TANH(self):
        """Returns the hyperbolic tangent of the argument."""
        if self.language == 'impala':
            return HardToImplement
        return lambda x : {'tanh': x}
    @property
    def ROTATELEFT(self):
        """Rotates an integer value left by a specified number of bits."""
        if self.language == 'impala':
            return HardToImplement
        return lambda x : {'rotateleft': x}
    @property
    def ROTATERIGHT(self):
        """Rotates an integer value right by a specified number of bits."""
        if self.language == 'impala':
            return HardToImplement
        return lambda x : {'rotateright': x}
    @property
    def SETBIT(self):
        """By default, changes a bit at a specified position to a 1, if it is not already."""
        if self.language == 'impala':
            return HardToImplement
        return lambda x : {'setbit': x} 
    @property
    def USER(self):
        """Returns the username of the Linux user who is connected to the impalad daemon. """
        if self.language == 'impala':
            return HardToImplement
        return lambda x : {'user': x}
    @property
    def RLIKE(self):
        """Comparisson operator.
           Hive: Implements Java regex Matcher and Presto implements Java Patter class. In queries test they presented the same behavior.
           Impala: implements Google RE2 library."""
        if self.language == 'hive':
            return MediumToImplement 
        if self.language == 'impala':
            return HardToImplement
        return lambda x : {'rlike': x}
    @property
    def REGEXP_EXTRACT(self):
        """Hive\Presto: Returns the same result.
           Impala: Returns some different results when running the same statements in Hive\Presto, so,
        pay attention when uncommenting this function. """
        if self.language == 'impala':
            return HardToImplement
        return lambda x : {'regexp_extract': x} 
    @property
    def REGEXP_LIKE(self):
        """Hive\Presto: Returns the same result.
           Impala: Returns some different results when running the same statements in Hive\Presto, so,
        pay attention when uncommenting this function. """
        if self.language == 'impala':
            return HardToImplement
        return lambda x : {'regexp_like': x} 
    @property
    def REGEXP_REPLACE(self):
        """Hive\Presto: Returns the same result.
           Impala: Returns some different results when running the same statements in Hive\Presto, so,
        pay attention when uncommenting this function. """
        if self.language == 'impala':
            return HardToImplement
        return lambda x : {'regexp_replace': x} 