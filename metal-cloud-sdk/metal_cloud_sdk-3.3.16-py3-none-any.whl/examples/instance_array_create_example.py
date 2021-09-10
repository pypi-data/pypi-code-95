import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from initialize_python_client import BSIClient

bsi = BSIClient.init()

# the provided hardware options are treated as a minimum configuration when looking for available servers
dictInstanceArrayParams = {
    "instance_array_label": "instance-array-label",
    "instance_array_instance_count": 1,
    "instance_array_ipv4_subnet_create_auto": True,
    "instance_array_ram_gbytes": 1,
    "instance_array_processor_core_mhz": 2128,
    "instance_array_processor_core_count": 1,
    "instance_array_processor_count":1
}

dictInstanceArray = bsi.instance_array_create("infrastructure-label", dictInstanceArrayParams)

# the operation needs to be deployed in order for hardware to be provisioned