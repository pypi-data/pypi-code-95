from typing import List
from zipfile import ZipFile
from UniversalParser._tools import read_content_from_zipobj
import UniversalParser as UP
from ._tools import *

class UPSheet:

    def __init__(self
            , name: str
            , sheetId: str
            , r_id: str
            , zip_obj: ZipFile
            , sheet_path: str
            , sis: List[str]
        ) -> None:
        self.name = name
        self.sheetId = sheetId
        self.r_id = r_id
        self._sis = sis
        
        self.shape = [1, 1] # 维度信息，[行数, 列数]
        self.size = 0 # 元素个数

        content = read_content_from_zipobj(zip_obj, sheet_path)
        self.manager = UP.parse_xml(content, analysis_text=False)

        self._init_shape()
    
    def _init_shape(self):
        dimension = self.manager.find_nodes_by_tag('dimension', one_=True)
        try:
            begin_loc, end_loc = dimension.ref.strip().split(':')
            begin_info = split_char_number(begin_loc)
            end_info = split_char_number(end_loc)
            self.shape[1] = get_width_by_char(begin_info[0], end_info[0])
            self.shape[0] = int(end_info[1]) - int(begin_info[1]) + 1
        except:
            pass

    def get_cell_by_coordinate(self, coordinate: str) -> str:
        try:
            cell = self.manager.find_node_by_attrs(r=coordinate)
        except:
            return None
        else:
            v = cell.get('v')
            if v is not None: v=self.manager.find_text(v)
            if 't' in cell and 's' == cell.t:
                v = self._sis[int(v)]
            return v if v else None
