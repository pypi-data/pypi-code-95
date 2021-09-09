import sys
import traceback

def printError(e, msg):
  error_class = e.__class__.__name__
  detail = e.args[0]
  cl, exc, tb = sys.exc_info() # get callstack
  lastCallStack = traceback.extract_tb(tb)[-1] # get the last record of callstack
  fileName = lastCallStack[0] # get the name of exception happened file
  lineNum = lastCallStack[1] # get the line number of exception happened file
  funcName = lastCallStack[2] #  get the function name of exception happened file
  errMsg = "Erorr: {}, File \"{}\", line {}, in {}: [{}] {}".format(msg, fileName, lineNum, funcName, error_class, detail)
  print(errMsg)