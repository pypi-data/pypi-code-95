import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from initialize_python_client import BSIClient

bsi = BSIClient.init()

bsi.infrastructure_design_lock_set("infrastructure-label", True)

# the operation applies immediately and does not need to be deployed
# if the lock is set, any attempts to alter the design of an infrastructure (adding/removing elements or editing them) will trigger an error