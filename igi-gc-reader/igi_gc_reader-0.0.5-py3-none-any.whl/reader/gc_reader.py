from dataclasses import dataclass
from typing import Iterator, Tuple

from igi_gc_reader.reader.gc_page import GcPageData, get_page_data
from igi_gc_reader.reader.excel_reader import get_excel_reader, IExcelReader
from igi_gc_reader.reader.context_data import ContextData, get_context_data_reader
from igi_gc_reader.reader.classification import ( 
    GcFileClass, class_to_expected_analysis_addr, is_an_analysis)
    

@dataclass(frozen=True)
class GcSheet:
    sheet_name: str
    analysis: str
    analysis_addr: str
    file_class: GcFileClass
    context_data: ContextData
    page_data: GcPageData

    def get_igi_analysis(self):
        """Map from raw analysis text in the sheet to the IGI analysis group."""
        raw_analysis = self.analysis.lower()
        if "sat" in raw_analysis:
            return "Sat-GCMS" if "gcms" in raw_analysis else "Sat-GC"
        if "aro" in raw_analysis: 
            return "Arom-GCMS" if "gcms" in raw_analysis else "Arom-GC"
        return "WO-GCMS" if "gcms" in raw_analysis else "WO-GC"


def build_gc_sheet(xl_reader: IExcelReader, sheet_name: str) -> GcSheet:

    def _get_analysis_and_class(xl_reader: IExcelReader) -> Tuple[GcFileClass, str, str]:
        """Returns tuple of class, analysis and analysis address"""
        for file_class, expected_anal_addresses in class_to_expected_analysis_addr.items():
            for addr in expected_anal_addresses:
                potential_anal_val = xl_reader.read_cell(addr)
                if potential_anal_val and is_an_analysis(potential_anal_val):
                    return file_class, potential_anal_val, str(addr)
        return GcFileClass.Unclassified, "", ""

    file_class, analysis, analysis_addr = _get_analysis_and_class(xl_reader)
    context_data = get_context_data_reader(file_class, xl_reader).get_context_data()
    context_data.set_data_dict(xl_reader)
    page_data = get_page_data(xl_reader, file_class)
    return GcSheet(sheet_name, analysis, analysis_addr, file_class, context_data, page_data)


def get_gc_sheets(wb_path: str) -> Iterator[GcSheet]:
    xl_reader = get_excel_reader(wb_path)
    for sheet in xl_reader.get_sheet_names():
        xl_reader.set_sheet(sheet)
        try:
            yield build_gc_sheet(xl_reader, sheet)
        # ignoring these errors allows us to process workbooks with some but not all valid sheets
        except StopIteration:  # ignore if not page data
            pass
        except NotImplementedError:  # ignore if not supported class type (handled elsewhere)
            pass
    xl_reader.close()
