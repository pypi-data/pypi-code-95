
"""

"""


import importlib
import os
import pymel.core as pm



def has_letters(rhs):
    return rhs.lower().islower()

def get_module_docstring(script):
    try:
        doctring = importlib.import_module(script).__doc__
        if has_letters(doctring):
            return doctring.strip()
    except BaseException:
        pass
    return "No doctring"

def run(node, scripts):
    result = []
    for script in scripts:
        try:
            scraper_module = importlib.import_module(script)
            try:
                reload(scraper_module)
            except:
                importlib.reload(scraper_module)
        except ImportError:
            pm.warning(
                "Can't load the script '{}' as a Python module.".format(script))
            raise
        except SyntaxError:
            pm.warning(
                "Syntax error in the scraper script: '{}'.".format(script))
            raise
        result += scraper_module.run(node)
    return result

