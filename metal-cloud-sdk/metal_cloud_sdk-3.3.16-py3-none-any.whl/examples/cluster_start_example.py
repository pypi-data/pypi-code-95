import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from initialize_python_client import BSIClient

bsi = BSIClient.init()

# starting a cluster provisions servers and drives and installs software according to the configured options
dictCluster = bsi.cluster_start("cluster-label")

# the operation needs to be deployed in order for hardware to be provisioned