import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from initialize_python_client import BSIClient

bsi = BSIClient.init()

# obtaining an operation object
objDriveArray = bsi.drive_array_get("drive-array-label")
objDriveArrayOperation = objDriveArray.drive_array_operation

# connecting a drive array to an instance array
dictInstanceArray = bsi.instance_array_get("instance-array-label")
objDriveArrayOperation.instance_array_id = dictInstanceArray.instance_array_id

# selecting an OS template
# note that changing the OS template will not affect any active drives, but only drives that are provisioned after the change takes effect
objDriveArrayOperation.volume_template_id = "centos6-6"

dictDriveArrayEditOptions = {
    "update_active_drives_size":False
}

# applying the changes
objDriveArray = bsi.drive_array_edit(objDriveArray.drive_array_id, objDriveArrayOperation, dictDriveArrayEditOptions)

# the operation needs to be deployed in order for hardware to be provisioned or deprovisioned and software installed