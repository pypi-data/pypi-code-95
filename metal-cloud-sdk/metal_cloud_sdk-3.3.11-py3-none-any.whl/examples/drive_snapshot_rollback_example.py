import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from initialize_python_client import BSIClient

bsi = BSIClient.init()

# get a list of all the drives, by ID, in a specific drive array
# as well as the ID of the instance each drive is attached to
dictDriveArray = bsi.drive_array_get("drive-array-label")
nDriveArrayID = dictDriveArray.drive_array_id
strQuery = (
    "SELECT drive_id, instance_id "
    "FROM drives "
    "WHERE drive_array_id = " + str(nDriveArrayID) + " "
    "LIMIT 10"
)

dictResult = bsi.query("login.email@goes.here", strQuery, bsi.COLLAPSE_NONE)

listDrivesInstances = dictResult["rows"]

# create a list of the most recent snapshots, including the drive ID and connected instance ID
listSnapshotsDrivesInstances = []
for dictDriveInstance in listDrivesInstances:
    # get the ID of the latest snapshot for each drive
    dictSnapshotsAux = bsi.drive_snapshots(dictDriveInstance["drive_id"])
    nSnapshotID = dictSnapshotsAux[sorted(dictSnapshotsAux.keys()).pop()]["drive_snapshot_id"]
    
    listSnapshotsDrivesInstances.append({"drive_snapshot_id" : nSnapshotID, "drive_id" : dictDriveInstance["drive_id"], "instance_id" : dictDriveInstance["instance_id"]})

# rollback to latest snapshots for each drive
# rollbacks require the servers to be shut down in order to ensure data consistency
# shutting off servers is done instantaneously and does not require a deploy operation
for dictSnapshotDriveInstance in listSnapshotsDrivesInstances:
    powerStatus = bsi.instance_server_power_get(dictSnapshotDriveInstance["instance_id"])
    if powerStatus != bsi.SERVER_POWER_STATUS_OFF:
        bsi.instance_server_power_set(dictSnapshotDriveInstance["instance_id"], bsi.SERVER_POWER_STATUS_OFF)
    bsi.drive_snapshot_rollback(dictSnapshotDriveInstance["drive_snapshot_id"])
    bsi.instance_server_power_set(dictSnapshotDriveInstance["instance_id"], bsi.SERVER_POWER_STATUS_ON)

# rollbacks are performed instantaneously and do not require an infrastructure deploy operation