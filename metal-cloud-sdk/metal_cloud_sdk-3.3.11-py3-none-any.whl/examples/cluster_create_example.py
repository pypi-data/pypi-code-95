import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from initialize_python_client import BSIClient

bsi = BSIClient.init()

# set up cluster parameters
dictClusterParam = {
    "cluster_label" : "cluster-label",
    "cluster_type" : "cloudera"
}

dictCluster = bsi.cluster_create("infrastructure-label", dictClusterParam)

# the operation needs to be deployed in order for hardware to be provisioned and software installed