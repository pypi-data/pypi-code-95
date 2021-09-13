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
"""Presto Dialect definition"""
from dora_parser.dialects import Dialect
from dora_parser.dialects import HardToImplement, MediumToImplement, EasyToImplement
from dora_parser import logger
from types import FunctionType

types = ["BOOLEAN","BYTE","SHORT","INT","LONG","FLOAT","DOUBL","DAT","TIMESTAM","STRIN","BINAR","DECIMAL","INTERVA","ARRAY","STRUCT","MAP"]

functions = ["ABS","ACOS","ACOSH","ADD_MONTHS","AGGREGATE","AND","ANY","APPROX_COUNT_DISTINCT","APPROX_PERCENTILE","ARRAY","ARRAY_CONTAINS","ARRAY_DISTINCT","ARRAY_EXCEPT","ARRAY_INTERSECT","ARRAY_JOIN","ARRAY_MAX","ARRAY_MIN","ARRAY_POSITION","ARRAY_REMOVE","ARRAY_REPEAT","ARRAY_SORT","ARRAY_UNION","ARRAYS_OVERLAP","ARRAYS_ZIP","ASCII","ASIN","ASINH","ASSERT_TRUE","ATAN","ATAN2","ATANH","AVG","BASE64","BETWEEN","BIGINT","BIN","BINARY","BIT_AND","BIT_COUNT","BIT_LENGTH","BIT_OR","BIT_XOR","BOOL_AND","BOOL_OR","BOOLEAN","BROUND","CARDINALITY","CASE","CAST","CBRT","CEIL","CEILING","CHAR","CHAR_LENGTH","CHARACTER_LENGTH","CHR","COALESCE","COLLECT_LIST","COLLECT_SET","CONCAT","CONCAT_WS","CONV","CORR","COS","COSH","COT","COUNT","COUNT_IF","COUNT_MIN_SKETCH","COVAR_POP","COVAR_SAMP","CRC32","CUBE","CUME_DIST","CURRENT_CATALOG","CURRENT_DATABASE","CURRENT_DATE","CURRENT_TIMESTAMP","CURRENT_TIMEZONE","DATE","DATE_ADD","DATE_FORMAT","DATE_FROM_UNIX_DATE","DATE_PART","DATE_SUB","DATE_TRUNC","DATEDIFF","DAY","DAYOFMONTH","DAYOFWEEK","DAYOFYEAR","DECIMAL","DECODE","DEGREES","DENSE_RANK","DIV","DOUBLE","E","ELEMENT_AT","ELT","ENCODE","EVERY","EXISTS","EXP","EXPLODE","EXPLODE_OUTER","EXPM1","EXTRACT","FACTORIAL","FILTER","FIND_IN_SET","FIRST","FIRST_VALUE","FLATTEN","FLOAT","FLOOR","FORALL","FORMAT_NUMBER","FORMAT_STRING","FROM_CSV","FROM_JSON","FROM_UNIXTIME","FROM_UTC_TIMESTAMP","GET_JSON_OBJECT","GREATEST","GROUPING","GROUPING_ID","HASH","HEX","HOUR","HYPOT","IF","IFNULL","IN","INITCAP","INLINE","INLINE_OUTER","INPUT_FILE_BLOCK_LENGTH","INPUT_FILE_BLOCK_START","INPUT_FILE_NAME","INSTR","INT","ISNAN","ISNOTNULL","ISNULL","JAVA_METHOD","JSON_ARRAY_LENGTH","JSON_OBJECT_KEYS","JSON_TUPLE","KURTOSIS","LAG","LAST","LAST_DAY","LAST_VALUE","LCASE","LEAD","LEAST","LEFT","LENGTH","LEVENSHTEIN","LIKE","LN","LOCATE","LOG","LOG10","LOG1P","LOG2","LOWER","LPAD","LTRIM","MAKE_DATE","MAKE_INTERVAL","MAKE_TIMESTAMP","MAP","MAP_CONCAT","MAP_ENTRIES","MAP_FILTER","MAP_FROM_ARRAYS","MAP_FROM_ENTRIES","MAP_KEYS","MAP_VALUES","MAP_ZIP_WITH","MAX","MAX_BY","MD5","MEAN","MIN","MIN_BY","MINUTE","MOD","MONOTONICALLY_INCREASING_ID","MONTH","MONTHS_BETWEEN","NAMED_STRUCT","NANVL","NEGATIVE","NEXT_DAY","NOT","NOW","NTH_VALUE","NTILE","NULLIF","NVL","NVL2","OCTET_LENGTH","OR","OVERLAY","PARSE_URL","PERCENT_RANK","PERCENTILE","PERCENTILE_APPROX","PI","PMOD","POSEXPLODE","POSEXPLODE_OUTER","POSITION","POSITIVE","POW","POWER","PRINTF","QUARTER","RADIANS","RAISE_ERROR","RAND","RANDN","RANDOM","RANK","REFLECT","REGEXP_EXTRACT","REGEXP_EXTRACT_ALL","REGEXP_REPLACE","REPEAT","REPLACE","REVERSE","RIGHT","RINT","RLIKE","ROLLUP","ROUND","ROW_NUMBER","RPAD","RTRIM","SCHEMA_OF_CSV","SCHEMA_OF_JSON","SECOND","SENTENCES","SEQUENCE","SHA","SHA1","SHA2","SHIFTLEFT","SHIFTRIGHT","SHIFTRIGHTUNSIGNED","SHUFFLE","SIGN","SIGNUM","SIN","SINH","SIZE","SKEWNESS","SLICE","SMALLINT","SOME","SORT_ARRAY","SOUNDEX","SPACE","SPARK_PARTITION_ID","SPLIT","SQRT","STACK","STD","STDDEV","STDDEV_POP","STDDEV_SAMP","STR_TO_MAP","STRING","STRUCT","SUBSTR","SUBSTRING","SUBSTRING_INDEX","SUM","TAN","TANH","TIMESTAMP","TIMESTAMP_MICROS","TIMESTAMP_MILLIS","TIMESTAMP_SECONDS","TINYINT","TO_CSV","TO_DATE","TO_JSON","TO_TIMESTAMP","TO_UNIX_TIMESTAMP","TO_UTC_TIMESTAMP","TRANSFORM","TRANSFORM_KEYS","TRANSFORM_VALUES","TRANSLATE","TRIM","TRUNC","TYPEOF","UCASE","UNBASE64","UNHEX","UNIX_DATE","UNIX_MICROS","UNIX_MILLIS","UNIX_SECONDS","UNIX_TIMESTAMP","UPPER","UUID","VAR_POP","VAR_SAMP","VARIANCE","VERSION","WEEKDAY","WEEKOFYEAR","WHEN","WIDTH_BUCKET","WINDOW","XPATH","XPATH_BOOLEAN","XPATH_DOUBLE","XPATH_FLOAT","XPATH_INT","XPATH_LONG","XPATH_NUMBER","XPATH_SHORT","XPATH_STRING","XXHASH64","YEAR","ZIP_WITH","DISTINCT"]

SUPPORTED_DIALECTS = ['impala']

class Spark(Dialect):
    def __init__(self, source:str):
        if source not in SUPPORTED_DIALECTS:
            raise ValueError(f"{source} dialect not supported")
        super().__init__(source)
        self.implemented(functions + types)

    def format(self, tree:dict) -> str:
        """Format the tree objet as a SQL query"""
        return self.formater(ansi_quotes=False).format(tree)

    @classmethod
    def _BTRIM_(cls, param):
        """Impala BTRIM has optional params to consider"""
        _param = Spark._LIT_(param)
        if isinstance(_param,list):
            return {'trim':[_par for _par in _param[::-1]]}
        return {'trim':param}
    @classmethod
    def _INSTR_(cls, param):
        """Not Implement the optional third and fourth arguments. This arguments let you find instances of the substr other than the first instance starting from the left."""
        _param = Spark._LIT_(param)
        if isinstance(_param,list):
            if len(_param)>2:
                return MediumToImplement(param)
        return {'instr': param}
    @classmethod
    def _REGEXP_LIKE_(cls, param):
        """The optional third argument consists of letter flags that change how the match is performed, such as i for case-insensitive matching"""
        _param = Spark._LIT_(param)
        if isinstance(_param,list):
            if len(_param)>2:
                return HardToImplement(param)
        logger.warning("--REGEX: Impala uses the Google RE2 library")
        return {'rlike':param}
    @classmethod
    def _DATE_TRUNC_(cls, param):
        """The unit argument is not case-sensitive. This argument string can be one of 'fmts'"""
        spark_fmts = ["YEAR", "YYYY", "YY", "QUARTER", "MONTH", "MM", "MON", "WEEK", "DAY", "DD", "HOUR", "MINUTE", "SECOND", "MILLISECOND", "MICROSECOND"]
        try:
            if Spark._LIT_(param)[0] in spark_fmts:
                return {'date_trunc': param}
            if Spark._LIT_(param)[0].get('literal') in spark_fmts:
                return {'date_trunc': param}
            raise ValueError(f"Spark data formats:{spark_fmts}")
        except Exception as err:
            logger.warning(err)
            return MediumToImplement(param)
    @classmethod
    def _TRUNC_(cls, param):
        """The unit argument is not case-sensitive. This argument string can be one of 'fmts'"""
        spark_fmts = ["YEAR", "YYYY", "YY","QUARTER","MONTH", "MM", "MON","WEEK"]
        try:
            if Spark._LIT_(param)[1] in spark_fmts:
                return {'trunc': param}
            if Spark._LIT_(param)[1].get('literal') in spark_fmts:
                return {'trunc': param}
            raise ValueError(f"Spark data formats:{spark_fmts}")
        except Exception as err:
            logger.warning(err)
            return MediumToImplement(param)
    @classmethod
    def _LIT_(cls, param):
        """Object literal to list of literals"""
        try:
            if isinstance(param['literal'],list):
                return [{'literal':p} for p in param['literal']]
        except:
            return param
    @classmethod
    def _DECODE_(cls, param):
        """Impala: Compares the first argument, expression, to the search expressions using the IS NOT DISTINCT operator, and returns:
            * The corresponding result when a match is found.
            * The first corresponding result if there are more than one matching search expressions.
            * The default expression if none of the search expressions matches the first argument expression.
            * NULL if the final default expression is omitted and none of the search expressions matches the first argument."""
        try:
            _case = Spark._LIT_(param)[0]
            _params = Spark._LIT_(param)[1:]
            _else = _params.pop()
            _when = [{'when': {'eq': [_case, _params[(idx*2)]]}, 'then':_params[(idx*2+1)]} for idx in range(int(len(_params)/2))]
            _when.append(_else)
            return {'case':_when}
        except Exception as err:
            logger.warning(err)
            return MediumToImplement(param)
    #Functions
    @property
    def DCEIL(self):
        """Impala: Returns the smallest integer that is greater than or equal to the argument"""
        if self.language == 'impala':
            return lambda x: self.CEIL(x)
        return lambda x: {'dceil':x}
    @property
    def DFLOOR(self):
        """Impala: Returns the largest integer that is less than or equal to the argument"""
        if self.language == 'impala':
            return lambda x: self.FLOOR(x)
        return lambda x: {'dfloor':x}
    @property
    def FMOD(self):
        """Impala: Returns the modulus of a floating-point number."""
        if self.language == 'impala':
            return lambda x: self.DOUBLE(self.MOD(x))
        return lambda x: {'fmod':x}
    @property
    def FNV_HASH(self):
        """Impala: Returns a consistent 64-bit value derived from the input argument
            > https://impala.apache.org/docs/build/html/topics/impala_math_functions.html#math_functions__fnv_hash"""
        if self.language=='impala':
            return HardToImplement
    @property
    def IS_INF(self):
        """Impala: Tests whether a value is equal to the special value "inf", signifying infinity."""
        if self.language == 'impala':
            return lambda x: {'eq': [x, self.DOUBLE({'literal':'infinity'})]}
        return lambda x: {'is_inf':x}
    @property
    def IS_NAN(self):
        """Impala: Tests whether a value is equal to the special value "NaN", signifying 'not a number'"""
        if self.language == 'impala':
            return lambda x: {'eq': [x, self.DOUBLE({'literal':'nan'})]}
        return lambda x: {'is_nan':x}
    @property
    def DLOG1(self):
        """Impala: Returns the natural logarithm of the argument"""
        if self.language == 'impala':
            return lambda x: self.LN(x)
        return lambda x: {'dlog1':x}
    @property
    def LOG2(self):
        """Impala: Returns the natural logarithm of the argument"""
        if self.language == 'impala':
            return lambda x: self.LN([{'literal':2},x])
        return lambda x: {'log2':x}
    @property
    def MAX_INT(self):
        """Returns the largest value of the associated integral type."""
        if self.language=='impala':
            return MediumToImplement
        return lambda x: {'max_int': x}
    @property
    def MAX_TINYINT(self):
        """Returns the largest value of the associated integral type."""
        if self.language=='impala':
            return MediumToImplement
        return lambda x: {'max_tinyint': x}
    @property
    def MAX_SMALLINT(self):
        """Returns the largest value of the associated integral type."""
        if self.language=='impala':
            return MediumToImplement
        return lambda x: {'max_smallint': x}
    @property
    def MAX_BIGINT(self):
        """Returns the largest value of the associated integral type."""
        if self.language=='impala':
            return MediumToImplement
        return lambda x: {'max_bigint': x}
    @property
    def MIN_INT(self):
        """Returns the smallest value of the associated integral type (a negative number)."""
        if self.language=='impala':
            return MediumToImplement
        return lambda x: {'min_int': x}
    @property
    def MIN_TINYINT(self):
        """Returns the smallest value of the associated integral type (a negative number)."""
        if self.language=='impala':
            return MediumToImplement
        return lambda x: {'min_tinyint': x}
    @property
    def MIN_SMALLINT(self):
        """Returns the smallest value of the associated integral type (a negative number)."""
        if self.language=='impala':
            return MediumToImplement
        return lambda x: {'min_smallint': x}
    @property
    def MIN_BIGINT(self):
        """Returns the smallest value of the associated integral type (a negative number)."""
        if self.language=='impala':
            return MediumToImplement
        return lambda x: {'min_bigint': x}
    @property
    def MURMUR_HASH(self):
        """Impala: Returns a consistent 64-bit value derived from the input argument, for convenience of implementing MurmurHash2 non-cryptographic hash function."""
        if self.language=='impala':
            return HardToImplement
        return lambda x: {'murmur_hash': x}
    @property
    def QUOTIENT(self):
        """Impala: Returns the first argument divided by the second argument, discarding any fractional part. Avoids promoting integer arguments to DOUBLE as happens with the / SQL operator. Also includes an overload that accepts DOUBLE arguments, discards the fractional part of each argument value before dividing, and again returns BIGINT. With integer arguments, this function works the same as the DIV operator."""
        if self.language == 'impala':
            return lambda x: self.ROUND([{'div': x},{'literal':0}])
        return lambda x: {'quotient':x}
    @property
    def DROUND(self):
        """Impala: Returns the first argument divided by the second argument, discarding any fractional part. Avoids promoting integer arguments to DOUBLE as happens with the / SQL operator. Also includes an overload that accepts DOUBLE arguments, discards the fractional part of each argument value before dividing, and again returns BIGINT. With integer arguments, this function works the same as the DIV operator."""
        if self.language == 'impala':
            return lambda x: self.ROUND(x)
        return lambda x: {'dround':x}
    @property
    def SUBSTRING_INDEX(self):
        """Spark: substring_index(str, delim, count) - Returns the substring from str before count occurrences of the delimiter delim. If count is positive, everything to the left of the final delimiter (counting from the left) is returned. If count is negative, everything to the right of the final delimiter (counting from the right) is returned. The function substring_index performs a case-sensitive match when searching for delim."""
        return lambda x: {'substring_index':x}
    @property
    def SCALE(self):
        """Purpose: Computes the scale (number of decimal digits to the right of the decimal point) needed to represent the type of the argument expression as a DECIMAL value."""
        if self.language == 'impala':
            return lambda x: self.LENGTH(self.SUBSTRING_INDEX([self.STRING(x), {'literal':'.'},{'literal':-1}]))
        return lambda x: {'scale':x}
    @property
    def PRECISION(self):
        """Impala: Computes the precision (number of decimal digits) needed to represent the type of the argument expression as a DECIMAL value."""
        if self.language == 'impala':
            return lambda x: self.LENGTH(self.REPLACE([self.STRING(x),{'literal':'.'},{'literal':''}]))
        return lambda x: {'precision': x}
    @property
    def DSQRT(self):
        """Impala: Returns the square root of the argument"""
        if self.language == 'impala':
            return lambda x: self.SQRT(x)
        return lambda x: {'dsqrt':x}
    @property
    def TRUNCATE(self):
        """Impala: Returns the square root of the argument"""
        if self.language == 'impala':
            return MediumToImplement
        return lambda x: {'truncate':x}
    @property
    def WIDTH_BUCKET(self):
        """Impala: Returns the bucket number in which the expr value would fall in the histogram where its range between min_value and max_value is divided into num_buckets buckets of identical sizes."""
        if self.language == 'impala':
            return EasyToImplement
        return lambda x: {'width_bucket':x}
    @property
    def BASE64DECODE(self):
        """Impala: Converts the argument from a base 64 string str to a binary"""
        if self.language == 'impala':
            return lambda x: {'unbase64':x}
        return lambda x: {'base64decode':x}
    @property
    def BASE64ENCODE(self):
        """Impala: Converts the argument from a binary bin to a base 64 string"""
        if self.language == 'impala':
            return lambda x: {'base64':x}
        return lambda x: {'base64encode':x}
    @property
    def BTRIM(self):
        """Impala: Removes all instances of one or more characters from the start and end of a STRING value."""
        if self.language == 'impala':
            return lambda x: Spark._BTRIM_(x)
        return lambda x: {'btrim':x}
    @property
    def INSTR(self):
        """Impala: Returns the position (starting from 1) of the first occurrence of a substr within a longer string."""
        if self.language == 'impala':
            return Spark._INSTR_
        return lambda x: {'instr':x}
    @property
    def JARO_DISTANCE(self):
        """Impala: Returns the Jaro distance between two input strings. The Jaro distance is a measure of similarity between two strings and is the complementary of JARO_SIMILARITY(), i.e. (1 - JARO_SIMILARITY())."""
        return HardToImplement
    @property
    def JARO_SIMILARITY(self):
        """Impala: Returns the Jaro similarity of two strings. The higher the Jaro similarity for two strings is, the more similar the strings are."""
        return HardToImplement
    @property
    def JARO_WINKLER_DISTANCE(self):
        """Impala: Returns the Jaro-Winkler distance of two input strings. It is the complementary of JARO_WINKLER_SIMILARITY(), i.e. 1 - JARO_WINKLER_SIMILARITY()."""
        return HardToImplement
    @property
    def JARO_WINKLER_SIMILARITY(self):
        """Impala: Returns the Jaro-Winkler Similarity between two input strings. The Jaro-Winkler similarity uses a prefix weight, specified by scaling factor, which gives more favorable ratings to strings that match from the beginning for a set prefix length, up to a maximum of four characters."""
        return HardToImplement
    @property
    def STRLEFT(self):
        """Impala: Returns the leftmost characters of the string. Shorthand for a call to SUBSTR() with 2 arguments"""
        if self.language == 'impala':
            return lambda x: self.LEFT(x)
        return lambda x: {'strleft':x}
    @property
    def STRRIGHT(self):
        """Impala: Returns the rightmost characters of the string. Shorthand for a call to SUBSTR() with 2 arguments"""
        if self.language == 'impala':
            return lambda x: self.RIGHT(x)
        return lambda x: {'strright':x}
    @property
    def CHAR_LENGTH(self):
        """Impala: Returns the length in characters of the argument string, ignoring any trailing spaces in CHAR values"""
        if self.language == 'impala':
            return lambda x: {'length':x}
        return lambda x: {'char_length':x}
    @property
    def LENGTH(self):
        """Impala: Returns the length in characters of the argument string, ignoring any trailing spaces in CHAR values"""
        if self.language == 'impala':
            return lambda x: self.CHAR_LENGTH(self.TRIM(x))
        return lambda x: {'length':x}
    @property
    def REGEXP_ESCAPE(self):
        """Impala: The REGEXP_ESCAPE() function returns a string escaped for the special character in RE2 library so that the special characters are interpreted literally rather than as special characters"""
        if self.language == 'impala':
            return MediumToImplement
        return lambda x: {'regexp_escape':x}
    @property
    def REGEXP_LIKE(self):
        """Impala: Returns true or false to indicate whether the source string contains anywhere inside it the regular expression given by the pattern. The optional third argument consists of letter flags that change how the match is performed, such as i for case-insensitive matching."""
        if self.language == 'impala':
            return Spark._REGEXP_LIKE_
        return lambda x: {'regexp_like':x}
    @property
    def SPLIT_PART(self):
        """Impala: Returns the requested indexth part of the input source string split by the delimiter."""
        if self.language == 'impala':
            return lambda x: {'array_position':[{'split':[x[0],x[1]]},x[2]]} if isinstance(x,list) else {'array_position':[{'split':[x['literal'][0],x['literal'][1]]},x['literal'][2]]}
        return lambda x: {'split_part':x}
    @property
    def ADDDATE(self):
        """Impala: Adds days to date and returns the new date value. The days value can be negative, which gives the same result as the SUBDATE() function."""
        if self.language == 'impala':
            return lambda x: {'date_add':x}
        return lambda x: {'adddate':x}
    @property
    def DATE_ADD(self):
        """Impala: Adds a specified number of days to the date argument"""
        if self.language == 'impala':
            return lambda x: {'add': [x[0],{'interval': [x[1], 'days']}]} if isinstance(x[1],int) else {'add': x}
        return lambda x: {'date_add':x}
    @property
    def DAYS_ADD(self):
        """Impala: Returns the value with the number of days added to date"""
        if self.language == 'impala':
            return lambda x: {'date_add':x}
        return lambda x: {'days_add':x}
    @property
    def DATE_SUB(self):
        """Impala: Subtracts a specified number of days from a TIMESTAMP value"""
        if self.language == 'impala':
            return lambda x: {'sub': [x[0],{'interval': [x[1], 'days']}]} if isinstance(x[1],int) else {'sub': x}
        return lambda x: {'date_sub':x}
    @property
    def DATE_CMP(self):
        """Impala: Compares date1 and date2 and returns:"""
        if self.language == 'impala':
            return lambda x: {'case': [{'when': {'gt': [{'datediff': x}, 0]}, 'then': 1}, {'when': {'lt': [{'datediff': x}, 0]}, 'then': -1}, 0]}
        return lambda x: {'date_cmp':x}
    @property
    def DAYS_SUB(self):
        """Impala: Returns the value with the number of days subtracted from date."""
        if self.language == 'impala':
            return lambda x: {'date_sub':x}
        return lambda x: {'days_sub':x}
    @property
    def DAYNAME(self):
        """Impala: Returns the day name of the date argument. The range of return values is 'Sunday' to 'Saturday'."""
        if self.language == 'impala':
            return lambda x: {'date_format':[x,{'literal':'EEEE'}]}
        return lambda x: {'dayname':x}
    @property
    def FROM_TIMESTAMP(self):
        """Impala: Converts a TIMESTAMP value into a string representing the same value."""
        if self.language == 'impala':
            return lambda x: {'date_format':x}
        return lambda x: {'from_timestamp':x}
    @property
    def HOURS_ADD(self):
        """Impala: Returns the specified date and time plus some number of hours"""
        if self.language == 'impala':
            return lambda x: {'add': [Spark._LIT_(x)[0],{'interval': [Spark._LIT_(x)[1], 'hours']}]}
        return lambda x: {'hours_add':x}
    @property
    def HOURS_SUB(self):
        """Impala: Returns the specified date and time minus some number of hours"""
        if self.language == 'impala':
            return lambda x: {'sub': [Spark._LIT_(x)[0],{'interval': [Spark._LIT_(x)[1], 'hours']}]}
        return lambda x: {'hours_sub':x}
    @property
    def INT_MONTHS_BETWEEN(self):
        """Impala: Returns the number of months from startdate to enddate, representing only the full months that passed."""
        if self.language == 'impala':
            return lambda x: self.FLOOR(self.MONTHS_BETWEEN(x))
        return lambda x: {'int_months_between':x}
    @property
    def MICROSECONDS_ADD(self):
        """Impala: Returns the specified date and time plus some number of microseconds"""
        if self.language == 'impala':
            return lambda x: {'add': [Spark._LIT_(x)[0],{'interval': [Spark._LIT_(x)[1], 'microseconds']}]}
        return lambda x: {'microseconds_add':x}
    @property
    def MICROSECONDS_SUB(self):
        """Impala: Returns the specified date and time plus some number of microseconds"""
        if self.language == 'impala':
            return lambda x: {'sub': [Spark._LIT_(x)[0],{'interval': [Spark._LIT_(x)[1], 'microseconds']}]}
        return lambda x: {'microseconds_sub':x}
    @property
    def MILLISECONDS_ADD(self):
        """Impala: Returns the specified date and time plus some number of milliseconds"""
        if self.language == 'impala':
            return lambda x: {'add': [Spark._LIT_(x)[0],{'interval': [Spark._LIT_(x)[1], 'milliseconds']}]}
        return lambda x: {'milliseconds_add':x}
    @property
    def MILLISECONDS_SUB(self):
        """Impala: Returns the specified date and time minus some number of milliseconds."""
        if self.language == 'impala':
            return lambda x: {'sub': [Spark._LIT_(x)[0],{'interval': [Spark._LIT_(x)[1], 'milliseconds']}]}
        return lambda x: {'milliseconds_sub':x}
    @property
    def MINUTE(self):
        """Impala: Returns the minute field from a TIMESTAMP value"""
        if self.language == 'impala':
            return lambda x: {'date_part': [{'literal':'MINUTES'},self.TIMESTAMP(Spark._LIT_(x))]}
        return lambda x: {'minute':x}
    @property
    def MINUTES_ADD(self):
        """Impala: Returns the specified date and time plus some number of minutes"""
        if self.language == 'impala':
            return lambda x: {'add': [Spark._LIT_(x)[0],{'interval': [Spark._LIT_(x)[1], 'MINUTES']}]}
        return lambda x: {'minutes_add':x}
    @property
    def MINUTES_SUB(self):
        """Impala: Returns the specified date and time minus some number of minutes."""
        if self.language == 'impala':
            return lambda x: {'sub': [Spark._LIT_(x)[0],{'interval': [Spark._LIT_(x)[1], 'MINUTES']}]}
        return lambda x: {'minutes_sub':x}
    @property
    def MONTH(self):
        """Impala: Returns the month field, represented as an integer, from the date argument"""
        if self.language == 'impala':
            return lambda x: {'date_part': [{'literal':'MONTH'},self.TIMESTAMP(Spark._LIT_(x))]}
        return lambda x: {'month':x}
    @property
    def MONTHNAME(self):
        """Impala: Returns the month name of the date argument"""
        if self.language == 'impala':
            return lambda x: {'date_format': [x, {'literal':'MMMM'}]}
        return lambda x: {'monthname':x}
    @property
    def MONTHS_ADD(self):
        """Impala: Returns the value with the number of months added to date."""
        if self.language == 'impala':
            return lambda x: {'add': [Spark._LIT_(x)[0],{'interval': [Spark._LIT_(x)[1], 'MONTHS']}]}
        return lambda x: {'months_add':x}
    @property
    def MONTHS_SUB(self):
        """Impala: Returns the specified date and time minus some number of minutes."""
        if self.language == 'impala':
            return lambda x: {'sub': [Spark._LIT_(x)[0],{'interval': [Spark._LIT_(x)[1], 'MONTHS']}]}
        return lambda x: {'months_sub':x}
    @property
    def NANOSECONDS_ADD(self):
        """Impala: Returns the specified date and time plus some number of nanoseconds."""
        if self.language == 'impala':
            return lambda x: {'add': [Spark._LIT_(x)[0],{'interval': [Spark._LIT_(x)[1], 'microseconds']}]}
        return lambda x: {'nanoseconds_add':x}
    @property
    def NANOSECONDS_SUB(self):
        """Impala: Returns the specified date and time minus some number of nanoseconds."""
        if self.language == 'impala':
            return lambda x: {'sub': [Spark._LIT_(x)[0],{'interval': [Spark._LIT_(x)[1], 'microseconds']}]}
        return lambda x: {'nanoseconds_sub':x}
    @property
    def SECONDS_ADD(self):
        """Impala: Returns the specified date and time plus some number of seconds."""
        if self.language == 'impala':
            return lambda x: {'add': [Spark._LIT_(x)[0],{'interval': [Spark._LIT_(x)[1], 'seconds']}]}
        return lambda x: {'seconds_add':x}
    @property
    def SECONDS_SUB(self):
        """Impala: Returns the specified date and time minus some number of seconds."""
        if self.language == 'impala':
            return lambda x: {'sub': [Spark._LIT_(x)[0],{'interval': [Spark._LIT_(x)[1], 'seconds']}]}
        return lambda x: {'seconds_sub':x}
    @property
    def SUBDATE(self):
        """Impala: Subtracts days from date and returns the new date value"""
        if self.language == 'impala':
            return lambda x: {'date_sub':x}
        return lambda x: {'subdate':x}
    @property
    def TIMEOFDAY(self):
        """Impala: Returns a string representation of the current date and time, according to the time of the local system, including any time zone designation."""
        if self.language == 'impala':
            return lambda x: {'date_format': [self.NOW(x), {'literal':'E MMM d H:m:s y O'}]}
        return lambda x: {'timeofday':x}
    @property
    def TIMESTAMP_CMP(self):
        """Impala: Tests if one TIMESTAMP value is newer than, older than, or identical to another TIMESTAMP"""
        if self.language == 'impala':
            return lambda x: self.DATE_CMP(x)
        return lambda x: {'timestamp_cmp':x}
    @property
    def TO_UTC_TIMESTAMP(self):
        """Impala: Converts a specified timestamp value in a specified time zone into the corresponding value for the UTC time zone"""
        if self.language == 'impala':
            return EasyToImplement
        return lambda x: {'to_utc_timestamp':x}
    @property
    def UNIX_TIMESTAMP(self):
        """Impala: Returns a Unix time, which is a number of seconds elapsed since '1970-01-01 00:00:00' UTC. If called with no argument, the current date and time is converted to its Unix time. If called with arguments, the first argument represented as the TIMESTAMP or STRING is converted to its Unix time."""
        if self.language == 'impala':
            return MediumToImplement
        return lambda x: {'unix_timestamp':x}
    @property
    def UTC_TIMESTAMP(self):
        """Impala: Returns a Unix time, which is a number of seconds elapsed since '1970-01-01 00:00:00' UTC. If called with no argument, the current date and time is converted to its Unix time. If called with arguments, the first argument represented as the TIMESTAMP or STRING is converted to its Unix time."""
        if self.language == 'impala':
            return MediumToImplement
        return lambda x: {'unix_timestamp':x}
    @property
    def WEEK(self):
        """Impala: Returns the corresponding week (1-53) from the date argument"""
        if self.language == 'impala':
            return lambda x: {'weekofyear':x}
        return lambda x: {'week':x}
    @property
    def WEEKS_ADD(self):
        """Impala: Returns the value with the number of WEEKS added to date."""
        if self.language == 'impala':
            return lambda x: {'add': [Spark._LIT_(x)[0],{'interval': [Spark._LIT_(x)[1], 'WEEKS']}]}
        return lambda x: {'weeks_add':x}
    @property
    def WEEKS_SUB(self):
        """Impala: Returns the value with the number of WEEKS subtracted from date."""
        if self.language == 'impala':
            return lambda x: {'sub': [Spark._LIT_(x)[0],{'interval': [Spark._LIT_(x)[1], 'WEEKS']}]}
        return lambda x: {'weeks_sub':x}
    @property
    def YEARS_ADD(self):
        """Impala: Returns the value with the number of years added to date."""
        if self.language == 'impala':
            return lambda x: {'add': [Spark._LIT_(x)[0],{'interval': [Spark._LIT_(x)[1], 'YEARS']}]}
        return lambda x: {'years_add':x}
    @property
    def YEARS_SUB(self):
        """Impala: Returns the value with the number of years subtracted from date."""
        if self.language == 'impala':
            return lambda x: {'sub': [Spark._LIT_(x)[0],{'interval': [Spark._LIT_(x)[1], 'YEARS']}]}
        return lambda x: {'years_sub':x}
    @property
    def DATE_TRUNC(self):
        """Impala: Returns the ts value truncated to the specified unit."""
        if self.language == 'impala':
            return Spark._DATE_TRUNC_
        return lambda x: {'date_trunc':x}
    @property
    def TRUNC(self):
        """Impala: Returns the ts truncated to the unit specified."""
        if self.language == 'impala':
            return Spark._TRUNC_
        return lambda x: {'trunc':x}
    @property
    def DATE_PART(self):
        """Impala: Similar to EXTRACT(), with the argument order reversed. Supports the same date and time units as EXTRACT(). For compatibility with SQL code containing vendor extensions."""
        if self.language == 'impala':
            return EasyToImplement
        return lambda x: {'date_part':x}
    @property
    def EXTRACT(self):
        """Impala: Returns one of the numeric date or time fields, specified by unit, from ts."""
        if self.language == 'impala':
            return EasyToImplement
        return lambda x: {'extract':x}
    @property
    def DECODE(self):
        """Impala: Can be used as shorthand for a CASE expression"""
        if self.language == 'impala':
            return Spark._DECODE_
        return lambda x: {'decode':x}
    @property
    def ISFALSE(self):
        """Impala: Returns TRUE if the expression is FALSE. Returns FALSE if the expression is TRUE or NULL."""
        if self.language == 'impala':
            return lambda x: {'eq':[self.IFNULL([self.BOOLEAN(x),True]),False]}
        return lambda x: {'isfalse':x}
    @property
    def ISTRUE(self):
        """Impala: Returns TRUE if the expression is TRUE. Returns FALSE if the expression is FALSE or NULL."""
        if self.language == 'impala':
            return lambda x: {'eq':[self.IFNULL([self.BOOLEAN(x),False]),True]}
        return lambda x: {'istrue':x}
    @property
    def ISNOTFALSE(self):
        """Impala: Tests if a Boolean expression is not FALSE (that is, either TRUE or NULL). Returns TRUE if so. If the argument is NULL, returns TRUE."""
        if self.language == 'impala':
            return lambda x: {'not':{'eq':[self.IFNULL([self.BOOLEAN(x),True]),False]}}
        return lambda x: {'isnotfalse':x}
    @property
    def ISNOTTRUE(self):
        """Impala: Tests if a Boolean expression is not TRUE (that is, either FALSE or NULL). Returns TRUE if so. If the argument is NULL, returns TRUE"""
        if self.language == 'impala':
            return lambda x: {'not':{'eq':[self.IFNULL([self.BOOLEAN(x),False]),True]}}
        return lambda x: {'isnottrue':x}
    @property
    def NONNULLVALUE(self):
        """Impala: Returns TRUE if the expression is non-null and returns FALSE if the expression is NULL."""
        if self.language == 'impala':
            return lambda x: {'not':self.ISNULL(x)}
        return lambda x: {'nonnullvalue':x}
    @property
    def NULLIFZERO(self):
        """Impala: Returns NULL if the numeric expression evaluates to 0, otherwise returns the result of the expression"""
        if self.language == 'impala':
            return lambda x: self.NULLIF([x,0])
        return lambda x: {'nullifzero':x}
    @property
    def ZEROIFNULL(self):
        """Impala: Returns 0 if the numeric expression evaluates to NULL, otherwise returns the result of the expression"""
        if self.language == 'impala':
            return lambda x: self.IFNULL([x,0])
        return lambda x: {'zeroifnull':x}
    @property
    def NULLVALUE(self):
        """Impala: Returns TRUE if the expression is NULL, and returns FALSE otherwise"""
        if self.language == 'impala':
            return lambda x: self.BOOLEAN(self.ISNULL(x))
        return lambda x: {'nullvalue':x}
    @property
    def APPX_MEDIAN(self):
        """Impala: An aggregate function that returns a value that is approximately the median (midpoint) of values in the set of input values."""
        if self.language == 'impala':
            return HardToImplement
        return lambda x: {'appx_median':x}
    @property
    def DISTINCT(self):
        """Spark: Collects and returns a set of unique elements."""
        return lambda x: {'distinct':x}
    @property
    def COLLECT_LIST(self):
        """Spark: Collects and returns a list of unique elements."""
        return lambda x: {'collect_list':x}
    @property
    def GROUP_CONCAT(self):
        """Impala: An aggregate function that returns a single string representing the argument value concatenated together for each row of the result set"""
        if self.language == 'impala':
            return lambda x: self.CONCAT_WS([Spark._LIT_(x)[1],self.COLLECT_LIST(Spark._LIT_(x)[0])]) if isinstance(x,list) else self.CONCAT_WS([{'literal':', '},self.COLLECT_LIST(x)])
        return lambda x: {'group_concat':x}
    @property
    def NDV(self):
        """Impala: An aggregate function that returns an approximate value similar to the result of COUNT(DISTINCT col), the "number of distinct values"."""
        if self.language == 'impala':
            return lambda x: self.COUNT(self.DISTINCT(x))
        return lambda x: {'ndv':x}
    @property
    def VARIANCE_SAMP(self):
        """Impala: Returns the sample variance calculated from values of a group."""
        if self.language == 'impala':
            return lambda x: {'var_samp':x}
        return lambda x: {'variance_samp':x}
    @property
    def VARIANCE_POP(self):
        """Impala: Returns the population variance calculated from values of a group."""
        if self.language == 'impala':
            return lambda x: {'var_pop':x}
        return lambda x: {'variance_pop':x}
    @property
    def EFFECTIVE_USER(self):
        """Impala: Typically returns the same value as USER()."""
        if self.language == 'impala':
            return HardToImplement
        return lambda x: {'effective_user':x}
    @property
    def LOGGED_IN_USER(self):
        """Impala: Typically returns the same value as USER()."""
        if self.language == 'impala':
            return HardToImplement
        return lambda x: {'logged_in_user':x}
    @property
    def PID(self):
        """Impala: Returns the process ID of the impalad daemon that the session is connected to."""
        if self.language == 'impala':
            return HardToImplement
        return lambda x: {'pid':x}
    @property
    def SLEEP(self):
        """Impala: Pauses the query for a specified number of milliseconds."""
        if self.language == 'impala':
            return HardToImplement
        return lambda x: {'sleep':x}
    @property
    def USER(self):
        """Impala: Returns the username of the Linux user who is connected to the impalad daemon."""
        if self.language == 'impala':
            return HardToImplement
        return lambda x: {'user':x}
    @property
    def COORDINATOR(self):
        """Impala: Returns the name of the host which is running the impalad daemon that is acting as the coordinator for the current query."""
        if self.language == 'impala':
            return HardToImplement
        return lambda x: {'coordinator':x}

    def STATEMENTS(self, key):
        """Dict of DML queries and DDL statements from Impala to Spark
           param: key is used to acess the dict and is formatted as: 'source_dialect'-'end_dialect' """

        statement_dict = {        
                        "impala-spark": {

                                "not_allowed": {  "ALTER DATABASE" : r"^(ALTER(\s*)DATABASE )",
                                                  "ALTER TABLE ADD IF NOT EXISTS COLUMNS": r'^(ALTER(\s*)TABLE(.|\n)*?ADD(\s*)(IF(\s*)NOT(\s*)EXISTS)(\s*)COLUMNS)',
                                                  "ALTER TABLE ADD COLUMN":r"^(ALTER(\s*)TABLE(.|\n)*?ADD(\s*)(COLUMN ))",
                                                  "ALTER TABLE ADD COLUMNS WITH COMMENT OR KUDU_ATTRIBUTES":r"^(ALTER(\s*)TABLE(.|\n)*?ADD(.|\n)*?COLUMNS(.|\n)*?(COMMENT|NULL|COMPRESSION|DEFAULT|BLOCK_SIZE|ENCODING))",
                                                  "ALTER TABLE CHANGE WITH COMMENT OR KUDU_ATTRIBUTES":r"^(ALTER(\s*)TABLE(.|\n)*?CHANGE(.|\n)*?(COMMENT|NULL|COMPRESSION|DEFAULT|BLOCK_SIZE|ENCODING))",
                                                  "ALTER TABLE ADD PARTITION WITH LOCATION OR CACHE":r"^(ALTER(\s*)TABLE(.|\n)*?ADD(.|\n)*?PARTITION(.|\n)*?(LOCATION|CACHED(\s*)IN ))",
                                                  "ALTER TABLE ALTER":r"^(ALTER(\s*)TABLE(.|\n)*?(ALTER ))",
                                                  "ALTER TABLE DROP":r"^(ALTER(\s*)TABLE(.|\n)*?DROP(\s*)(?!.*PARTITION))",
                                                  "ALTER TABLE RANGE PARTITION":r"^(ALTER(\s*)TABLE(.|\n)*?(RANGE(\s*)PARTITION ))",
                                                  "ALTER TABLE REPLACE COLUMNS":r"^(ALTER(\s*)TABLE(.|\n)*?(REPLACE(\s*)COLUMNS ))",
                                                  "ALTER TABLE RECOVER PARTITIONS":r"^(ALTER(\s*)TABLE(.|\n)*?(RECOVER(\s*)PARTITIONS))",
                                                  "ALTER TABLE SET CACHED IN OR UNCACHED":r"^(ALTER(\s*)TABLE(.|\n)*?SET(\s*)(UNCACHED|CACHED(\s*)IN ))",
                                                  "ALTER TABLE SET ROW FORMAT":r"^(ALTER(\s*)TABLE(.|\n)*?SET(\s*)(ROW(\s*)FORMAT))",
                                                  "ALTER TABLE SET OWNER USER":r"^(ALTER(\s*)TABLE(.|\n)*?(SET(\s*)OWNER(\s*)USER ))",
                                                  "ALTER TABLE WITH STATSKEY":r"^(ALTER(\s*)TABLE(.|\n)*?(numDVs|numNulls|avgSize|maxSize))",
                                                  "ALTER VIEW": r"^(ALTER(\s*)VIEW(.|\n)*?((\((.+)\)(.|\n)*?AS(\s*)SELECT)|COMMENT|SET(\s*)OWNER(\s*)USER ))",
                                                  "COMPUTE STATS":r"^(COMPUTE(.|\n)*?STATS)",
                                                  "COMMENT (START WITH)":r"^(COMMENT)",
                                                  "CREATE FUNCTION":r"^(CREATE(.|\n)*?FUNCTION)",
                                                  "CREATE TABLE EXCEPTIONS":r"^(CREATE(.|\n)*?TABLE(.|\n)*?(PRIMARY(\s*)KEY|FOREIGN(\s*)KEY|SORT(\s*)BY|WITH(\s*)SERDEPROPERTIES|CACHED(\s*)IN ))",
                                                  "CREATE TABLE LIKE":r"^(CREATE(.|\n)*?TABLE(.|\n)*?(LIKE))",
                                                  "CREATE TABLE KUDU EXCEPTIONS":r"^(CREATE(.|\n)*?TABLE(.|\n)*?(PRIMARY(\s*)KEY|NULL|ENCODING|COMPRESSION|DEFAULT|BLOCK_SIZE|PARTITION(\s*)BY ))",
                                                  "CREATE ROLE":r"^(CREATE(\s*)ROLE )",
                                                  "DELETE":r"^(DELETE)",
                                                  "DESCRIBE FORMATTED":r"^(DESCRIBE(.|\n)*?FORMATTED)",
                                                  "DROP FUNCTION":r"^((DROP(\s*)AGGREGATE(\s*)FUNCTION)|DROP(\s*)FUNCTION(.|\n)*?((\((.+)\))))",
                                                  "DROP ROLE":r"^(DROP(\s*)ROLE)",
                                                  "DROP STATS":r"^(DROP(.|\n)*?STATS)",
                                                  "DROP TABLE WITH PURGE":r"^(DROP(\s*)TABLE(.|\n)*?PURGE)",
                                                  "GRANT":r"^(GRANT)",
                                                  "INSERT VALUES":r"^(INSERT(.|\n)*?VALUES)",
                                                  "INVALIDATE METADATA":r"^(INVALIDATE(\s*)METADATA)",
                                                  "OPTIMIZER HINTS":r"(BROADCAST|SHUFFLE|NOSHUFFLE|SCHEDULE_CACHE_LOCAL|SCHEDULE_DISK_LOCAL|SCHEDULE_REMOTE|CLUSTERED|NOCLUSTERED)",
                                                  "REFRESH PARTITION":r"^(REFRESH(.|\n)*?PARTITION)",
                                                  "REFRESH":r"^(REFRESH(\s*)(AUTHORIZATION|FUNCTIONS))",
                                                  "REVOKE":r"^(REVOKE)",
                                                  "SET":r"^(SET)",
                                                  "SHOW FUNCTIONS":r"^(SHOW(\s*)(AGGREGATE|ANALYTIC)(.|\n)*?FUNCTIONS|(SHOW(\s*)FUNCTIONS(\s*)IN ))",
                                                  "SHOW EXCEPTIONS":r"^(SHOW(.|\n)*?(CREATE(\s*)VIEW|GRANT|ROLES|ROLE|FILES(\s*)IN |RANGE|COLUMN(\s*)STATS|TABLE(\s*)STATS))",
                                                  "SHUTDOWN":r"^(:SHUTDOWN)",
                                                  "TRUNCATE":r"^(TRUNCATE)",
                                                  "UPDATE":r"^(UPDATE)",
                                                  "UPSERT":r"^(UPSERT)",
                                                  "VALUES (START WITH)":r"^(VALUES)",
                                                  "WITH INSERT":r"^(WITH(.|\n)*?INSERT)"
                                },

                                "replace": {
                                                "STRING" : "CHAR",
                                                "STRING" : "VARCHAR"
                                }
                        }
        }
        return statement_dict[key]
