import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from initialize_python_client import BSIClient

bsi = BSIClient.init()

# connecting another instance array interface to a network increases throughput
bsi.instance_array_interface_attach_network(
	"instance-array-label",
	0, # make sure the selected instance array interface is not already connected to a network, as this will disconnect it
	"wan" # instance array interfaces can be attached to the WAN or to any LANs on the infrastructure
)

# the operation needs to be deployed in order for hardware to be provisioned and software installed