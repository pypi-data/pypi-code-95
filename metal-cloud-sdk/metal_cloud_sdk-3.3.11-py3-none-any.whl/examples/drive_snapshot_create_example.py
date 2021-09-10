import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from initialize_python_client import BSIClient

bsi = BSIClient.init()

# get the list of drives belonging to a specified drive array
objDriveArray = bsi.drive_array_get("drive-array-label")
nDriveArrayID = objDriveArray.drive_array_id
strQuery = (
    "SELECT drive_id "
    "FROM drives "
    "WHERE drive_array_id = " + str(nDriveArrayID) + " "
    "LIMIT 10"
)

dictResult = bsi.query("login.email@address.here", strQuery, bsi.COLLAPSE_NONE)
listDrives = dictResult["rows"]
listSnapshots = []

# create snapshots for all the drives in the list
for objDrive in listDrives:
    objSnapshot = bsi.drive_snapshot_create(objDrive["drive_id"])
    listSnapshots.append({"drive_id" : objDrive.drive_id, "drive_snapshot_id" : objSnapshot.drive_snapshot_id})

# snapshots are created instantly and do not require an infrastructure deploy operation