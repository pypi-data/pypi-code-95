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
"""Lakehouse Context"""
import os
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.functions import col as spark_col
from pyspark.sql.functions import lit as spark_lit
from pyspark.sql.functions import expr as spark_expr
from dora_lakehouse import logger, sanitize
from dora_lakehouse.catalog import Table, Column

HASH_COL = os.environ.get('HASH_COL','__data_hash__') # Hash column identifier
DEL_COL = os.environ.get('DEL_COL','__data_delete__') # Delete column identifier
IDX_COL = os.environ.get('IDX_COL','__index_level_0__') # Index column identifier
NAME_SIZE = int(os.environ.get('NAME_SIZE','16'))
MAX_SIZE = int(os.environ.get('MAX_SIZE','128')) #Max file size in MB
MAX_ROWS = int(os.environ.get('MAX_ROWS','10000000')) # Default max rows per file 10 millions
MIN_ROWS = int(os.environ.get('MIN_ROWS','10000')) # Default min rows per file 10 thousand

class PseudoColumn(Column):
    """Moch column class"""
    def representation(self) -> dict:
        return dict(name=self.name,type=self.data_type)

class DataTable(DataFrame):
    """Table data representation"""

    PSEUDO_COLUMNS=[
        PseudoColumn(IDX_COL,"string"),
        PseudoColumn(DEL_COL,"bool"),
        PseudoColumn(HASH_COL,"string")]
    
    @classmethod
    def schema_equalization(cls, data_frame:DataFrame, table:Table) -> DataFrame:
        """Compare the columns (by name) in the table definition of loaded dataframe.
        1. Add all the missing columns on the data frame, with None values
        2. Remove all columns not related with the table definition
        :param rdf: raw data frame
        :return: equalized data frame
        """
        if table.hash_def is None:
            raise ValueError('Cant find data hash function')
        logger.debug("HASH:DEFINITION:%s",table.hash_def)
        _hash_def=f"lpad(abs(ceil({table.hash_def})),{NAME_SIZE},'0')"
        # Apply the same function used on table creation for all df columns
        col_df = [sanitize(_col) for _col in data_frame.columns]
        for _col in table.columns+DataTable.PSEUDO_COLUMNS:
            if _col.name not in col_df: # If this column not in the dataframe
                data_frame = data_frame.withColumn(_col.name, spark_lit(None).cast(_col.sparktype))
            else: # apply the type constraint
                data_frame = data_frame.withColumn(_col.name,data_frame[_col.name].cast(_col.sparktype))
        col_tb = [_col.name for _col in table.columns+DataTable.PSEUDO_COLUMNS]
        for _col in col_df: # For each column of the raw dataframe
            if _col not in col_tb: # if someone are not in the table definition
                data_frame = data_frame.drop(_col) # Remove the column
        return data_frame.select(col_tb).withColumn(HASH_COL, spark_expr(_hash_def)) # To keep column order

    def __init__(self, sparkContext, dataFrame, table:Table, **kwargs):
        super().__init__(self.schema_equalization(dataFrame, table)._jdf, sparkContext)
        self.table = table
        self.context = sparkContext
        self.master_dataframe = kwargs.get('master')
        self.hash_list = kwargs.get('hash')
    
    @property
    def keys(self):
        """Return an list of keys, used for join or ordering"""
        _keys = [_col.name for _col in self.table.indexes]
        if len(_keys)==0: #If table dont have index
            _keys = [IDX_COL] # Use meta column
        return _keys

    @property
    def hashs(self):
        """List of hash IDs"""
        if self.hash_list is None:
            self.hash_list = [_hk[HASH_COL] for _hk in self.select(HASH_COL).distinct().collect()]
        return self.hash_list

    @property
    def master(self):
        """Master dataframe"""
        return self.context.load_master(self.hashs, self.table)

    def update(self, data_table:DataFrame=None):
        """Merge data and write the updates"""
        # Master data frame
        if data_table is None:
            data_table = self.master
        else:
            if data_table.table.checksum() != self.table.checksum():
                logger.error("Expected:%s\nReceives:%s",self.table, data_table.table)
                raise ValueError("Incompatible table definitions")
        mdf = data_table.alias('r') # right table on join
        # Staged data frame
        sdf = self.alias('l') # left table on join
        # Full outer join data frame
        join_condition = [(spark_col(f'r.{idx}')==spark_col(f'l.{idx}')) for idx in self.keys]
        if self.table.update == 'append': # IDX_COL have the sequence
            join_condition.append((spark_col(f'r.{IDX_COL}')==spark_col(f'l.{IDX_COL}')))
        fdf = mdf.join( sdf, on=join_condition, how='full_outer')
        # Out of scope
        offset = fdf.where(" AND ".join([f'l.{idx} IS NULL' for idx in self.keys])).select('r.*')
        if self.table.update == 'overwrite': # If table update mode is 'overwrite'
            offset = offset.withColumn(DEL_COL, spark_lit(True)) # Mark all lines as Deleted
        # New lines
        inserts = fdf.where(" AND ".join([f'r.{idx} IS NULL' for idx in self.keys])).select('l.*')
        # Update common data
        unchange_filter = ['1=2'] # List of filters, starts with False
        update_filter = ['1=1'] # List of filters, starts with True
        for _col in self.table.tiebreaks: # If there is some criteria
            if str(_col.tiebreak[1]).lower()=='max':
                unchange_filter.append(f"""r.{_col.name} > l.{_col.name}""")
                update_filter.append(f"""r.{_col.name} <= l.{_col.name}""")
            elif str(_col.tiebreak[1]).lower()=='min':
                unchange_filter.append(f"""r.{_col.name} < l.{_col.name}""")
                update_filter.append(f"""r.{_col.name} >= l.{_col.name}""")
            else:
                logger.error("Tiebreack option '%s' not implemented.", _col.tiebreak)
                raise NotImplementedError
        unchange = fdf.filter(spark_col(f'l.{IDX_COL}').isNotNull()).where(" OR ".join(unchange_filter)).select('r.*')
        updates  = fdf.filter(spark_col(f'l.{IDX_COL}').isNotNull()).where(" AND ".join(update_filter)).select('l.*')
        # Update dataframe
        self._jdf = offset.union(inserts).union(unchange.union(updates)).dropDuplicates()._jdf
        return self

    def stage(self) -> list:
        """Save Datatable on lake
        :return: hash keys"""
        return self.context.write_stage(self)

    def save(self):
        """Save Datatable on lake"""
        if self.table.save():
            return self.context.write_refined(self)
        