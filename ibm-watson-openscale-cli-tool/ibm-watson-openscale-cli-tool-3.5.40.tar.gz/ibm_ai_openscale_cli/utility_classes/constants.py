# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale_cli.enums import Environment

"""
Constants used throughout the fast-path CLI.
"""

# Stores the environment mapping to the scikit-learn version trained DDM folder
DRIFT_ARCHIVE_ENV_MAPPING = {
    Environment.PUBLIC_CLOUD.value: "scikit_0.24.2",
    Environment.CPD_3_X.value: "scikit_0.20.2",
    Environment.CPD_4_0_0.value: "scikit_0.20.2",
    Environment.CPD_4_0_1.value: "scikit_0.20.2",
    Environment.CPD_4_0_2_PLUS.value: "scikit_0.24.2"
}
