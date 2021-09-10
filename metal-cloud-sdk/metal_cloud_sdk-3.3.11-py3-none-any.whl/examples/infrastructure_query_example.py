import sys
import os.path
import json
from initialize_python_client import BSIClient
from metal_cloud_sdk.constants import Constants

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

bsi = BSIClient.init()
strUserID = "your_login_email@goes.here"

"""
* First we need to create an infrastructure. Alternatively you can use an already creted infrastructure.
"""
# select the datacenter where the infrastructure will be created
dictDatacenters = bsi.datacenters()
strKey = dictDatacenters.keys()[0]
strDatacenter = dictDatacenters[strKey].datacenter_name

strInfrastructureName = "infrastructure-label-query"

# setting up the infrastructure object parameter
dictInfrastructureCreateParams = {
    "infrastructure_label": strInfrastructureName,
    "datacenter_name": strDatacenter
}

objInfrastructure = bsi.infrastructure_create(strUserID, dictInfrastructureCreateParams, None)
nInfrastructureID = objInfrastructure.infrastructure_id

"""
* The query must contain SELECT, FROM, WHERE, ORDER BY and LIMIT.
* In the SELECT part * is not accepted.
"""
bsi.query(
    strUserID,
    """
        SELECT
            instance_array_id,
            instance_array_label,
            instance_array_instance_count,
            instance_array_ram_gbytes,
            instance_array_processor_count
        FROM instance_arrays
        WHERE
            (
                instance_array_instance_count >= 0
                OR
                instance_array_instance_count >= 10
            )
            AND
            (
                instance_array_processor_count >= 1
                AND
                instance_array_instance_count >= 0
            )
            AND
            (
                instance_array_ram_gbytes > 1
                OR
                instance_array_ram_gbytes < 1
            )
        ORDER BY
            instance_array_id ASC
        LIMIT 0, 10
    """,
    Constants.COLLAPSE_ARRAY_SUBROWS
)

dictInstanceArrayParams = {
   "instance_array_label": "instance-array-label",
   "instance_array_instance_count": 1,
   "instance_array_ipv4_subnet_create_auto": True,
   "instance_array_ram_gbytes": 1,
   "instance_array_processor_core_mhz": 2128,
   "instance_array_processor_core_count": 1,
   "instance_array_processor_count":1
}

dictInstanceArray = bsi.instance_array_create(strInfrastructureName, dictInstanceArrayParams)
nInstanceArrayID = dictInstanceArray.instance_array_id

bsi.query(
    strUserID,
    """
        SELECT
            instance_array_id,
            instance_array_label,
            instance_array_instance_count,
            instance_array_ram_gbytes,
            instance_array_processor_count
        FROM instance_arrays
        WHERE
            (instance_array_label LIKE """ + json.dumps("instance-array-label%") + """)
        ORDER BY
            instance_array_id ASC
        LIMIT 0, 10
    """,
    Constants.COLLAPSE_ARRAY_SUBROWS
)