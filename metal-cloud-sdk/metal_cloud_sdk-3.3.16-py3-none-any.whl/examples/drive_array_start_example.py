import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from initialize_python_client import BSIClient

bsi = BSIClient.init()

# starting a drive array provisions drives according to the configured options
dictDriveArray = bsi.drive_array_start("drive-array-label")

# the operation needs to be deployed in order for hardware to be provisioned