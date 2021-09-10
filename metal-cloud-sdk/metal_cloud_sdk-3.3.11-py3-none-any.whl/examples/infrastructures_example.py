import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from initialize_python_client import BSIClient

bsi = BSIClient.init()

# the function returns a dictionary of all infrastructures the specified user has administrative permissions on
dictInfrastructures = bsi.infrastructures("login.email@goes.here")
