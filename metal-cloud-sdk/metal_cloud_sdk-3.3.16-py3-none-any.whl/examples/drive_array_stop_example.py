import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from initialize_python_client import BSIClient

bsi = BSIClient.init()

# stopping a drive array deprovisions all allocated space
dictDriveArray = bsi.drive_array_stop("drive-array-label")

# the operation needs to be deployed in order for hardware to be deprovisioned
# since stopping a drive array means losing all the data on the drives being deprovisioned, insfrastructure_deploy() must be called with the bAllowDataLoss parameter set to True