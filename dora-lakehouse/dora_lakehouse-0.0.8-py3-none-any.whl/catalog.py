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
"""Lakehouse Objects"""
import hashlib
import json
from os import environ
from abc import ABC, abstractmethod
import pyspark.sql.types as SparkType
from dora_lakehouse import sanitize

class Catalog:
    """Base object to create catalog representations"""
    def __init__(self,repr_def):
        """Default constructor"""
        self.repr_def = repr_def

    def __repr__(self) -> str:
        """Catalog oabject represented in a JSON format
        :return: string in JSON format
        """
        try:
            return json.dumps(self.repr_def(), sort_keys=False)
        except:
            return str(dict(self))

    def __iter__(self):
        """Passed an iterable that produces key-value pairs"""
        res = self.repr_def()
        for key in self.repr_def():
            yield (key,res[key])

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return dict(self) == dict(other)
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def value(self) -> dict:
        """Get all values from representation
        :return: Dictionary with formated values
        """
        return self.repr_def()

class Database(Catalog, ABC):
    """
    Database Abstract Representation
    """
    def __init__(self,name:str,description:str=None,location:str=None,parameters:dict=None):
        """Defalt database constructor
        :param name: The name of the database. For Hive compatibility, this is folded to lowercase when it is stored
        :param description: A description of the database. For Hive compatibility, this is folded to lowercase when it is stored
        :param location: The location of the database (for example, an HDFS path).
        :param parameters: These key-value pairs define parameters and properties of the database.
        """
        super().__init__(self.representation)
        self.name = sanitize(name)
        self.description = sanitize(description)
        self.location = sanitize(location)
        self.parameters = parameters
        if parameters is None:
            self.parameters = dict()

    @abstractmethod
    def representation(self) -> dict:
        """Implement this method to change the representation of your database object
        :return: Dictionary Representation, compatible with API"""
    
    @abstractmethod
    def save(self) -> bool:
        """Save the database definition
        :return: True if the object was success persisted
        """

class Column(Catalog, ABC):
    """
    Column Abstract Representation
    """
    # Acceptable tie breack values
    tiebreaks = dict(MAX='max',MIN='min')
    # Acceptable Data types
    types = {
        'bool':SparkType.BooleanType(),
        'boolean':SparkType.BooleanType(),
        'date':SparkType.DateType(),
        'double':SparkType.DoubleType(),
        'int':SparkType.IntegerType(),
        'smallint':SparkType.ShortType(),
        'long':SparkType.LongType(),
        'bigint':SparkType.LongType(),
        'float':SparkType.FloatType(),
        'decimal':SparkType.DecimalType(),
        'string':SparkType.StringType(),
        'varchar':SparkType.StringType(),
        'timestamp':SparkType.TimestampType()}

    @classmethod
    def validate(cls, columns:list) -> list:
        """Validate all columns
        ::param columns: generic list of columns
        :return: column generator"""
        for col in columns:
            if isinstance(col, Column) and col.data_type in list(Column.types.keys()):
                yield col
            else:
                raise ValueError(f"{col} is not a valid Column object")

    def __init__(self,name:str, data_type:str, description:str=None, index:bool=False, partition:bool=False, tiebreaker:tuple=None):
        """ Default column constructor
        :param name: The name of the Column.
        :param data_type: The data type of the Column .
        :param description: A free-form text description.
        :param index: True if this column is a unique identifier. Default is False.
        :param partition : True if this column is used as a partition. Default is False. Only primitive types are supported as partition keys
        :param tiebreaker: if this column is used as a tie breake criteria inform one of the Column.tiebreaks options. Default is None
        """
        super().__init__(self.representation)
        self.name = sanitize(name)
        self.data_type = sanitize(data_type)
        self.index = index
        self.partition = partition
        self.description = description
        if isinstance(description,str):
            self.description = description.strip()
        self.tiebreak = tiebreaker
        if tiebreaker is not None:
            order, value = tiebreaker
            self.tiebreak = (int(order),sanitize(value))
            if sanitize(value) not in Column.tiebreaks.values():
                raise ValueError(f"Acceptable tie breack values: {Column.tiebreaks.values()}")

    @abstractmethod
    def representation(self) -> dict:
        """Implement this method to change the representation of your database object
        :return: Dictionary Representation, compatible with API"""

    @property
    def sparktype(self) -> SparkType:
        """Get the correct Spark object
        :return: SparkType object
        """
        return Column.types.get(self.data_type)

    @property
    def field(self) -> SparkType.StructField:
        """Column as a Spark Struct Field
        :return: Spark Struct Field"""
        return SparkType.StructField(
            name = self.name,
            dataType = self.sparktype,
            nullable = self.isnullable())

    def isindex(self) -> bool:
        """Is this column an index?
        :return: True if is an index. False if not
        """
        return self.index

    def ispartition(self) -> bool:
        """Is this column an partition?
        :return: True if is an partition. False if not
        """
        return self.partition

    def istiebreaker(self) -> bool:
        """Is this column an tiebreack criteria?
        :return: True if is an tiebreack criteria. False if not
        """
        return self.tiebreak is not None

    def isnullable(self) -> bool:
        """Check if the column is able to accept null values"""
        if self.isindex() or self.ispartition() or self.istiebreaker():
            return False
        return True


class Table(Catalog, ABC):
    """
    Table Abstract Representation
    """
    # Supported formats
    support = dict(
        serialization=['orc','parquet','json','csv'],
        compression=['uncompressed', 'bzip2', 'deflate', 'gzip', 'lz4', 'snappy'],
        update=['upsert','append','overwrite'],
        type=["EXTERNAL_TABLE"])

    @classmethod
    def validate(cls, prop:str, option:str) -> list:
        """Validate all available options
        :param prop: property to validate
        :param option: option to validate
        :return: valid option"""
        if option not in cls.support[prop]:
            raise ValueError(f"Unsupported Option: {option}.Available Options: {cls.support[prop]}")
        return option

    def __init__(self, database:Database, name:str, columns:list, hash_def:str, **kwargs):
        """ Default column constructor
        :param database: The catalog database in which to create the new table. For Hive compatibility, this name is entirely lowercase
        :param name: The table name. For Hive compatibility, this is folded to lowercase when it is stored.
        :param location: The physical location of the table.
        :param columns: A list of the Columns in the table.
        :param hash_def: function definition that will be evaluated to calculate the line hash.
        :param update: How this table will be updated. Default is 'append'
        :param source: List of all Source locations.
        :param delete: An SQL expression to check if the register need to be mark as deleted. Default "1=2"
        :param description: A description of the table.
        :param table_type: The type of this table. Default "EXTERNAL_TABLE"
        :param serialization: Serialization Format. Default "parquet"
        :param compression: Sets the compression codec used to store data. Default "snappy"
        :param serde_library: Usually the class that implements the SerDe. Default "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
        :param serde_input: The input format: SequenceFileInputFormat (binary), or TextInputFormat. Default "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
        :param serde_output: The output format: SequenceFileOutputFormat (binary), or IgnoreKeyTextOutputFormat. Default "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"
        :param check: Checksum signature
        """
        super().__init__(self.representation)
        self.database = database
        self.name = sanitize(name)
        self.hash_def = hash_def.strip()
        self.source = kwargs.get('source')
        self.location = kwargs.get('location',f"{environ['BKT_RFN']}/{database.name}/{name}").strip()
        # Order columns by data and partition types
        self.columns = list(
            [_col for _col in Column.validate(columns) if not _col.ispartition()] + 
            [_col for _col in Column.validate(columns) if _col.ispartition()])
        self.table_type = Table.validate('type', kwargs.get('table_type','EXTERNAL_TABLE'))
        self.serialization = Table.validate('serialization',kwargs.get('serialization','parquet'))
        self.compression = Table.validate('compression',kwargs.get('compression','snappy'))
        self.update = Table.validate('update',kwargs.get('update','upsert'))
        self.description = kwargs.get('description','Created By Dora Lakehouse').strip()
        self.serde_library = kwargs.get('serde_library','org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe')
        self.serde_input = kwargs.get('serde_input','org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat')
        self.serde_output = kwargs.get('serde_output','org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat')
        self.check = kwargs.get('check')
        self.delete = kwargs.get('delete','1=2')

    @abstractmethod
    def representation(self) -> dict:
        """Implement this method to change the representation of your Table object
        :return: Dictionary Representation, compatible with API
        """

    @abstractmethod
    def save(self) -> bool:
        """Save and catalog the table definition
        :return: True if the object was success persisted
        """

    @abstractmethod
    def update_partitions(self, files:list) -> list:
        """Update partitions on catalog
        :param files: list of files to register partitions
        :return: bypass the list of files
        """

    def checksum(self) -> str:
        """A checksum is a small-sized block of data derived from Table dictionary for the purpose of detecting changes
        :return: Check String"""
        signature = str(( self.table_type
                        , self.serialization
                        , self.compression
                        , self.update
                        , self.hash_def
                        , self.location
                        , list(self.datacolumns)
                        , list(self.partitions))).encode()
        return hashlib.sha256(signature).hexdigest()
    
    @property
    def full_name(self):
        """Table full name"""
        return f"{self.database.name}.{self.name}"
    @property
    def schema(self) -> SparkType.StructType:
        """Spark Struct type based on table columns"""
        return SparkType.StructType([col.field for col in self.columns])
    @property
    def ischanged(self) -> bool:
        """Check if was any change in the table definition
        :return: True if table change"""
        return self.check != self.checksum()
    @property
    def datacolumns(self):
        """Return an list of all common columns"""
        for col in self.columns:
            if not col.ispartition():
                yield col
    @property
    def partitions(self):
        """Return an list of all partition columns"""
        for col in self.columns:
            if col.ispartition():
                yield col
    @property
    def indexes(self):
        """Return an list of all index columns"""
        for col in self.columns:
            if col.isindex():
                yield col
    @property
    def tiebreaks(self):
        """Return an list of all istiebreak columns"""
        tbks = [col for col in self.columns if col.istiebreaker()]
        tbks.sort(key=lambda a: a.tiebreak[0])
        return tbks
