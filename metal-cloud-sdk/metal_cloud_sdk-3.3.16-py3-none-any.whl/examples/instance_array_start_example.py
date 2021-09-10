import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from initialize_python_client import BSIClient

bsi = BSIClient.init()

# starting an instance array allocates servers to all its instances
dictInstanceArray = bsi.instance_array_start("instance-array-label")

# the operation needs to be deployed in order for hardware to be provisioned and software installed