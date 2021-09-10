import sys
import os.path
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from initialize_python_client import BSIClient

bsi = BSIClient.init()

# deploying all pending operations on the infrastructure
strInfrastructureLabel = "infrastructure-label"
bsi.infrastructure_deploy(strInfrastructureLabel)

# waiting for the deploy operation to conclude
objInfrastructure = bsi.infrastructure_get(strInfrastructureLabel)

while objInfrastructure.infrastructure_operation.infrastructure_deploy_status != "finished":
    time.sleep(3)
    objInfrastructure = bsi.infrastructure_get(strInfrastructureLabel)