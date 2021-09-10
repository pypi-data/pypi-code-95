import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from initialize_python_client import BSIClient

bsi = BSIClient.init()

dictInfrastructure = bsi.infrastructure_delete("infrastructure-label")

# the operation needs to be deployed in order for hardware to be deprovisioned
# since deleting an infrastructure means losing all the data on the drives being deprovisioned, infrastructure_deploy() must be called with the bAllowDataLoss parameter set to True