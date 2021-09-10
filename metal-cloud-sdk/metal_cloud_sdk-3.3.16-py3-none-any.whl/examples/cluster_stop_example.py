import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from initialize_python_client import BSIClient

bsi = BSIClient.init()

# stopping a cluster deprovisions all associated servers and drives
dictCluster = bsi.cluster_stop("cluster-label")

# the operation needs to be deployed in order for hardware to be deprovisioned
# since stopping a cluster means losing all the data on the drives being deprovisioned, insfrastructure_deploy() must be called with the bAllowDataLoss parameter set to True