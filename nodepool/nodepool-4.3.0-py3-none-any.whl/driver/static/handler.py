# Copyright 2017 Red Hat
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging

from nodepool import zk
from nodepool.driver import NodeRequestHandler


class StaticNodeRequestHandler(NodeRequestHandler):
    log = logging.getLogger("nodepool.driver.static."
                            "StaticNodeRequestHandler")

    DONE_STATES = {zk.READY, zk.FAILED}

    def _check_node_state(self, node, deleted):
        return not (node.state in self.DONE_STATES or deleted)

    @property
    def alive_thread_count(self):
        # We don't spawn threads to launch nodes, so always return 1.
        return 1

    def imagesAvailable(self):
        '''
        This driver doesn't manage images, so always return True.
        '''
        return True

    def hasRemainingQuota(self, ntype):
        # A pool of static nodes can manage nodes with different labels.
        # There is no global quota that we can exceed here. Return true
        # so we can wait for the required node type and don't block
        # other node requests.
        return True

    def launch(self, node):
        self.log.debug("Waiting for node %s to be ready", node.id)
        self.zk.watchNode(node, self._check_node_state)

    def launchesComplete(self):
        node_states = [node.state for node in self.nodeset]
        return all(s in self.DONE_STATES for s in node_states)

    def checkReusableNode(self, node):
        return self.manager.checkNodeLiveness(node)
