# Copyright 2021 IBM All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This file defines the various messages used by the SDK.
"""

REGION_ERROR = "Provide a valid region in App Configuration init"
GUID_ERROR = "Provide a valid guid in App Configuration init"
APIKEY_ERROR = "Provide a valid apiKey in App Configuration init"
COLLECTION_ID_VALUE_ERROR = "Provide a valid collection_id in App Configuration set_context method"
ENVIRONMENT_ID_VALUE_ERROR = "Provide a valid environment_id in App Configuration set_context method"
COLLECTION_INIT_ERROR = "Invalid action in App Configuration. This action can be performed only after a successful " \
                       "initialization operation. Please check the initialization section for errors. "
CONFIGURATION_FILE_NOT_FOUND_ERROR = "configuration_file parameter should be provided while " \
                                     "live_config_update_enabled is false in set_context method."
CONFIGURATION_HANDLER_INIT_ERROR = 'Invalid action in ConfigurationHandler. This action can be performed only after a ' \
                                   'successful initialization. Please check the initialization section for errors. '
CONFIGURATION_HANDLER_METHOD_ERROR = "Invalid action in ConfigurationHandler. Should be a method/function"
CONFIGURATION_API_ERROR = "Invalid configuration. Verify the collection_id, environment_id, apikey, guid and region."
SINGLETON_EXCEPTION = "class must be initialized using the get_instance() method."
FEATURE_INVALID = "Invalid feature_id - "
NO_INTERNET_CONNECTION_ERROR = 'No connection to internet. Please re-connect.'
PROPERTY_INVALID = "Invalid property_id - "
