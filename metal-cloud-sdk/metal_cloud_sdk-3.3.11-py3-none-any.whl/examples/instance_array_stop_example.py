import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from initialize_python_client import BSIClient

bsi = BSIClient.init()

# stopping an instance array deallocates all its provisioned servers
dictInstanceArray = bsi.instance_array_stop("instance-array-label")

# the operation needs to be deployed in order for hardware to be deprovisioned