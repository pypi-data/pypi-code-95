from ctypes import cdll, c_wchar_p, c_int, c_longlong
import os
from pathlib import Path

__all__ = ['eaAnalyzer', 'eaAnalyzersFinal']

ea_lib = cdll.LoadLibrary(Path(os.path.dirname(__file__) + "/libea.so"))

eaAnalyzerCreate = ea_lib.eaAnalyzerCreate
eaAnalyzerCreate.restype = c_int

eaAnalyzerAddSample = ea_lib.eaAnalyzerAddSample
eaAnalyzerAddSample.restype = None

eaAnalyzerReport = ea_lib.eaAnalyzerReport
eaAnalyzerReport.restype = None

eaAnalyzerChecksPerform = ea_lib.eaAnalyzerChecksPerform
eaAnalyzerChecksPerform.restype = None

eaAnalyzerSamplesReport = ea_lib.eaAnalyzerSamplesReport
eaAnalyzerSamplesReport.restype = None

eaAnalyzersReport = ea_lib.eaAnalyzersReport
eaAnalyzersReport.restype = None

eaAnalyzersChecksPerform = ea_lib.eaAnalyzersChecksPerform
eaAnalyzersChecksPerform.restype = None

eaAnalyzersFinal = ea_lib.eaAnalyzersFinal
eaAnalyzersFinal.restype = None

class eaAnalyzer:
  def __init__(self, name, bit_width, is_signed=False, time=0):
    
    if (not isinstance(name, str)):
      print("Error: name must be a string")
      
    if (not isinstance(bit_width, int)):
      print("Error: bit_width must be of type int")
      
    if (not isinstance(time, int)):
      print("Error: time must be of type int")
    
    Name = c_wchar_p(name)
    Type = c_int(0)
    DataBitWidth = c_int(bit_width)
    DataIsSigned = c_int(1) if is_signed else c_int(0)   
    Time = c_longlong(time)

    self.ID = eaAnalyzerCreate(Name, Type, DataBitWidth, DataIsSigned, Time)
    
  def add_sample(self, data_read, data_expected, time=0):
  
    try:
      data_read = int(data_read)
      data_expected = int(data_expected)
    except ValueError:
      print("data_read and data_expected cannot be casted to int")
    
    if (not isinstance(data_read, int) or not isinstance(data_expected, int)):
      print("Error: data_read and data_expected must be of type int")
      
    DataRead = c_int(data_read)
    DataExpected = c_int(data_expected)
    Time = c_int(time)
    
    eaAnalyzerAddSample(c_int(self.ID), DataRead, DataExpected, Time)
  
  def report_samples(self):
    eaAnalyzerSamplesReport(c_int(self.ID))
  
  def perform_checks(self):
    eaAnalyzerChecksPerform(c_int(self.ID))
  
  def report(self):
    eaAnalyzerReport(c_int(self.ID))

