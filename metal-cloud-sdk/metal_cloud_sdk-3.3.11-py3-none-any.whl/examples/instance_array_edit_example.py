import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from initialize_python_client import BSIClient

bsi = BSIClient.init()

strInstanceArrayLabel = "instance-array-label"

# obtain an instance array operation object
dictInstanceArray = bsi.instance_array_get(strInstanceArrayLabel)
objInstanceArrayOperation = dictInstanceArray.instance_array_operation

# change the hardware configuration of the servers
objInstanceArrayOperation.instance_array_ram_gbytes = 4
objInstanceArrayOperation.instance_array_processor_core_count = 2
objInstanceArrayOperation.instance_array_processor_core_mhz = 3000

dictInstanceArray = bsi.instance_array_edit(strInstanceArrayLabel, objInstanceArrayOperation)

# the operation needs to be deployed in order for hardware to be provisioned or deprovisioned and software installed