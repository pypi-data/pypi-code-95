"""A client-side library provided by Ionic Security for the purpose of
programming applications (standalone applications, services, plugins,
etc).

Class Modules:
    agent - The client-side library for all Ionic.com REST API endpoint
            communication.
    chunkcipher - Supports protection of small-medium sized text strings
                  and binary arrays.
    cryptocipher - Supports standard AES 256 GCM / CTR encryption.
    filecipher - Supports protection of files of all types.

Utility Modules:
    cryptoutil - Contains cryptographic hashing, authentication, and key
                 derivation utilities.
    log - Supports flexible and extensible logging for the SDK and any
          consuming application.
    errors - Translation of native library error codes.
    exceptions - Exception classes used by ionicsdk.
"""

import os
versionfilepath=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'VERSION')
__version__=open(versionfilepath).read().strip()
commitfilepath=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'COMMIT')
__commit__=open(commitfilepath).read().strip()

import ionicsdk.log
from ionicsdk.profilemanager import *
from ionicsdk.agent import *
from ionicsdk.chunkcipher import *
from ionicsdk.filecipher import *
from ionicsdk.cryptocipher import *
from ionicsdk.secretshare import *
from ionicsdk.keyvault import *
import ionicsdk.cryptoutil
from ionicsdk.errors import *
from ionicsdk.exceptions import *
from ionicsdk.coverpage import *
