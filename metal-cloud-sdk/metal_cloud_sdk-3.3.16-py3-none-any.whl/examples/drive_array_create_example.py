import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from initialize_python_client import BSIClient

bsi = BSIClient.init()

# configure the size, performance and OS template that will be installed on the drives
dictDriveArrayParams = {
  "drive_array_label" : "drive-array-label",
  "drive_array_count" : 2,
  "volume_template_id" : "", 
  "drive_array_storage_type" : "iscsi_ssd",
  "drive_size_mbytes_default" : 40960,
  "drive_array_expand_with_instance_array" : True
}

strOSTemplate = "centos7-5"
dictAvailableTemplates = bsi.volume_templates_public()
for i in dictAvailableTemplates.keys():
	if strOSTemplate == i:
		dictDriveArrayParams["volume_template_id"] = strOSTemplate
		break

dictDriveArray = bsi.drive_array_create("infrastructure-label", dictDriveArrayParams)

# the operation needs to be deployed in order for hardware to be provisioned and software installed