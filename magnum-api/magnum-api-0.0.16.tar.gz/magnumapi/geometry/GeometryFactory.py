from enum import Enum, auto
from typing import List, Dict
import json

import pandas as pd

from magnumapi.geometry.CosThetaBlock import AbsoluteCosThetaBlock, RelativeCosThetaBlock
from magnumapi.geometry.CosThetaGeometry import RelativeCosThetaGeometry
from magnumapi.geometry.Geometry import Geometry
from magnumapi.geometry.RectangularBlock import RectangularBlock
from magnumapi.geometry.roxie.AbsoluteCosThetaBlockDefinition import AbsoluteCosThetaBlockDefinition
from magnumapi.geometry.roxie.RectangularBlockDefinition import RectangularBlockDefinition
from magnumapi.geometry.roxie.RelativeCosThetaBlockDefinition import RelativeCosThetaBlockDefinition
from magnumapi.geometry.roxie.CableDatabase import CableDatabase
import magnumapi.tool_adapters.roxie.RoxieAPI as RoxieAPI


class GeometryType(Enum):
    """GeometryType is an enum type used to distinguish between an absolute and relative geometry.

    """
    ABSOLUTE = auto()
    RELATIVE = auto()


class GeometryFactory:
    """ GeometryFactory implements a factory design pattern and is used to produce:
    - rectangular geometry
    - absolute cos-theta geometry
    - relative cos-theta geometry

    """

    # A dictionary from geometry type to block type
    geometry_type_to_block = {1: AbsoluteCosThetaBlock,
                              2: RectangularBlock}

    # A dictionary from geometry type to block definition type
    geometry_type_to_block_definition = {1: AbsoluteCosThetaBlockDefinition,
                                         2: RectangularBlockDefinition}

    @classmethod
    def init_with_json(cls, json_file_path: str, cadata: CableDatabase) -> Geometry:
        """ Class method initializing a Geometry instance from a JSON file.

        :param json_file_path: a path to a json file
        :param cadata: a CableDatabase instance
        :return: initialized geometry instance
        """
        block_defs = cls.read_json_file(json_file_path)
        return cls.init_with_dict(block_defs, cadata)

    @staticmethod
    def read_json_file(json_file_path: str) -> List[dict]:
        """ Static method reading a json file and returning a list of dictionaries with block definitions.

        :param json_file_path: a path to a json file
        :return: a list of dictionaries with geometry definition (block definition)
        """
        with open(json_file_path) as f:
            lst_dct = json.load(f)
        return lst_dct

    @classmethod
    def init_with_dict(cls, block_defs: List[Dict], cadata: CableDatabase) -> Geometry:
        """ Class method initializing a Geometry instance from a list of dictionaries with block definition.

        :param block_defs: a list of dictionaries with geometry definition (block definition)
        :param cadata: a CableDatabase instance
        :return: initialized geometry instance
        """
        geom_type = cls.retrieve_geometry_type_dict(block_defs)

        if geom_type == GeometryType.ABSOLUTE:
            return cls.init_absolute_with_dict(block_defs, cadata)

        if geom_type == GeometryType.RELATIVE:
            return cls.init_relative_with_dict(block_defs, cadata)

    @staticmethod
    def retrieve_geometry_type_dict(block_defs: List[Dict]) -> GeometryType:
        """ Static method returning a geometry type enumeration for a given list of block definitions.
        An AttributeError is raised in case of inconsistencies in the definition.

        :param block_defs: list of block definitions
        :return: a geometry type enumeration
        """
        if all(['alpha_r' in dct.keys() for dct in block_defs]):
            return GeometryType.RELATIVE
        elif any(['alpha_r' in dct.keys() for dct in block_defs]):
            raise AttributeError(
                'Error, inconsistent geometry definition. '
                'The geometry definition should consist of either all relative definitions or none.')
        else:
            return GeometryType.ABSOLUTE

    @staticmethod
    def init_absolute_with_dict(block_defs: List[Dict], cadata: CableDatabase) -> Geometry:
        """ Static method initializing an absolute geometry (either rectangular or cos-theta) from a list of block
        definitions.

        :param block_defs: a list of block definitions
        :param cadata: a CableDatabase instance
        :return: initialized absolute geometry instance
        """
        blocks = []
        for block_def in block_defs:
            BlockClass = GeometryFactory.geometry_type_to_block[block_def['type']]
            BlockDefinitionClass = GeometryFactory.geometry_type_to_block_definition[block_def['type']]
            block_abs = BlockDefinitionClass(**block_def)
            block = BlockClass(block_def=block_abs,
                               cable_def=cadata.get_cable_definition(block_abs.condname),
                               insul_def=cadata.get_insul_definition(block_abs.condname),
                               strand_def=cadata.get_strand_definition(block_abs.condname),
                               conductor_def=cadata.get_conductor_definition(block_abs.condname))

            blocks.append(block)

        return Geometry(blocks=blocks)

    @staticmethod
    def init_relative_with_dict(block_defs: List[Dict], cadata: CableDatabase) -> Geometry:
        """ Static method initializing an absolute cos-theta geometry from a list of block definitions.

        :param block_defs: a list of block definitions
        :param cadata: a CableDatabase instance
        :return: initialized relative geometry instance
        """
        blocks = []
        for block_def in block_defs:
            block_rel = RelativeCosThetaBlockDefinition(**block_def)
            block = RelativeCosThetaBlock(block_def=block_rel,
                                          cable_def=cadata.get_cable_definition(block_rel.condname),
                                          insul_def=cadata.get_insul_definition(block_rel.condname),
                                          strand_def=cadata.get_strand_definition(block_rel.condname),
                                          conductor_def=cadata.get_conductor_definition(block_rel.condname))
            blocks.append(block)

        return RelativeCosThetaGeometry(blocks=blocks)

    @classmethod
    def init_with_data(cls, data_file_path: str, cadata: CableDatabase) -> Geometry:
        """ Class method initializing a Geometry instance from a DATA ROXIE file.

        :param data_file_path: a path to a json file
        :param cadata: a CableDatabase instance
        :return: initialized geometry instance
        """
        block_df = RoxieAPI.read_bottom_header_table(data_file_path, keyword='BLOCK')
        return cls.init_with_df(block_df, cadata)

    @classmethod
    def init_with_csv(cls, csv_file_path: str, cadata: CableDatabase) -> Geometry:
        """ Class method initializing a Geometry instance from a CSV file.

        :param csv_file_path: a path to a csv file
        :param cadata: a CableDatabase instance
        :return: initialized geometry instance
        """
        block_df = pd.read_csv(csv_file_path, index_col=0)
        return cls.init_with_df(block_df, cadata)

    @classmethod
    def init_with_df(cls, block_df: pd.DataFrame, cadata: CableDatabase) -> Geometry:
        """ Class method initializing a Geometry instance from a dataframe with block definition.

        :param block_df: a dataframe with geometry definition (block definition)
        :param cadata: a CableDatabase instance
        :return: initialized geometry instance
        """
        geom_type = cls.retrieve_geometry_type_df(block_df)
        if geom_type == GeometryType.ABSOLUTE:
            return cls.init_absolute_with_df(block_df, cadata)

        if geom_type == GeometryType.RELATIVE:
            return cls.init_relative_with_df(block_df, cadata)

    @staticmethod
    def retrieve_geometry_type_df(block_df: pd.DataFrame) -> "GeometryType":
        """ Static method returning a geometry type enumeration for a given dataframe with block definitions.
        An AttributeError is raised in case of inconsistencies in the definition.

        :param block_defs: list of block definitions
        :return: a geometry type enumeration
        """
        if ('alpha_r' in block_df.columns) and ('phi_r' in block_df.columns):
            return GeometryType.RELATIVE
        elif ('alpha_r' in block_df.columns) or ('phi_r' in block_df.columns):
            raise AttributeError('Error, inconsistent geometry definition')
        else:
            return GeometryType.ABSOLUTE

    @staticmethod
    def init_absolute_with_df(block_df: pd.DataFrame, cadata: CableDatabase) -> Geometry:
        """ Static method initializing an absolute geometry (either rectangular or cos-theta) from a dataframe with
        block definitions.

        :param block_df: a dataframe with block definitions
        :param cadata: a CableDatabase instance
        :return: initialized absolute geometry instance
        """
        blocks = []
        for _, row in block_df.iterrows():
            BlockClass = GeometryFactory.geometry_type_to_block[row['type']]
            BlockDefinitionClass = GeometryFactory.geometry_type_to_block_definition[row['type']]
            if row['type'] == 2:
                row = row.rename(BlockClass.roxie_to_magnum_dct)

            block_def = BlockDefinitionClass(**row.to_dict())
            block = BlockClass(block_def=block_def,
                               cable_def=cadata.get_cable_definition(block_def.condname),
                               insul_def=cadata.get_insul_definition(block_def.condname),
                               strand_def=cadata.get_strand_definition(block_def.condname),
                               conductor_def=cadata.get_conductor_definition(block_def.condname))

            blocks.append(block)

        return Geometry(blocks)

    @staticmethod
    def init_relative_with_df(block_df: pd.DataFrame, cadata: CableDatabase) -> Geometry:
        """ Static method initializing an absolute cos-theta geometry from a dataframe with block definitions.

        :param block_df: a dataframe with block definitions
        :param cadata: a CableDatabase instance
        :return: initialized relative geometry instance
        """
        blocks = []
        for row_dict in block_df.to_dict('records'):
            block_rel = RelativeCosThetaBlockDefinition(**row_dict)

            block = RelativeCosThetaBlock(block_def=block_rel,
                                          cable_def=cadata.get_cable_definition(block_rel.condname),
                                          insul_def=cadata.get_insul_definition(block_rel.condname),
                                          strand_def=cadata.get_strand_definition(block_rel.condname),
                                          conductor_def=cadata.get_conductor_definition(block_rel.condname))

            blocks.append(block)

        return RelativeCosThetaGeometry(blocks=blocks)
