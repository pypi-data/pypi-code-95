#!/usr/bin/env python
###############################################################################
# (c) Copyright 2017 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''
Jenkins script to poll Gaudi merge requests to bulid.
'''

import os
import re
import sys

# prepare runtime environment
TOP_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
os.environ['PATH'] = os.pathsep.join(
    [os.path.join(TOP_DIR, 'scripts'),
     os.environ.get('PATH', '')])
sys.path.insert(0, os.path.join(TOP_DIR, 'python'))

COUCHDB_DOC = 'gaudi-processed-merge-requests'


def main():
    '''
    Script logic.
    '''
    from LbNightlyTools.Utils import getAllMergeRequestIDs, Dashboard
    # remove old trigger files
    for f in os.listdir(os.curdir):
        if re.match(r'^gaudi-mr-\d+.txt$', f):
            os.remove(f)

    dash = Dashboard()

    pending = getAllMergeRequestIDs('gaudi/Gaudi', labels=['Test on LHCb'])
    processed = dash.db.get(COUCHDB_DOC, {
        'type': 'gaudi-processed-merge-requests',
        'ids': []
    })

    # create trigger file for each new merge request
    for mr in pending:
        if mr not in processed['ids']:
            with open('gaudi-mr-{0}.txt'.format(mr), 'w') as param_file:
                param_file.write('mr={0}\n'.format(mr))
                print 'created gaudi-mr-{0}.txt'.format(mr)

    # update list of processed MRs (removing those not opened anymore)
    if processed['ids'] != pending:
        processed['ids'] = pending
        dash.db[COUCHDB_DOC] = processed


if __name__ == '__main__':
    main()
