import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from initialize_python_client import BSIClient

bsi = BSIClient.init()

# changing a cluster's software version requires the cluster to be stopped
# see the documentation entry for cluster_start() for more information
strClusterLabel = "cluster-label"
objCluster = bsi.cluster_get(strClusterLabel, False, 20)
dictClusterOperation = objCluster.cluster_operation
objClusterApp = bsi.cluster_app(strClusterLabel)

# set the new software version and verify whether it is among the supported versions
strClusterNewVersion = "5.3.0"
if strClusterNewVersion in objClusterApp.cluster_app.cluster_software_available_versions:
    dictClusterOperation.cluster_software_version = strClusterNewVersion
    strCluster = bsi.cluster_edit(strClusterLabel, dictClusterOperation)

# the operation needs to be deployed in order for hardware to be provisioned and software installed