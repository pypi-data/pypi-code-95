"""
example usage:
s = Storage('<bot credentials in a json file>',"<YOUR URL>").var1()
s["something"] = "other"
s.sync()
"""
from .storage import Storage


