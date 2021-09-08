# clustercron/lb.py
# vim: ts=4 et sw=4 sts=4 ft=python fenc=UTF-8 ai
# -*- coding: utf-8 -*-

'''
clustercron.lb
---------------

Modules holds base class for AWS ElasticLoadBalancing classes
'''

from __future__ import unicode_literals

import logging

import boto.utils

logger = logging.getLogger(__name__)


class Lb(object):
    def __init__(self, name):
        '''
        :param name: name of load balancer or target group
        '''
        self.name = name
        self._get_instance_meta_data()

    def _get_instance_meta_data(self):
        try:
            data = boto.utils.get_instance_identity()
        except Exception as error:
            logger.error('Could not get instance data: %s', error)
            data = {'document': {}}
        self.region_name = data['document'].get('region')
        self.instance_id = data['document'].get('instanceId')

        logger.info('self.region_name: %s', self.region_name)
        logger.info('self.instance_id: %s', self.instance_id)

    def get_healty_instances(self):
        raise NotImplementedError

    def master(self):
        logger.debug('Check if instance is master')
        if self.instance_id is None:
            logger.error('No Instanced Id')
        else:
            healty_instances = self.get_healty_instances()
            if healty_instances:
                return self.instance_id == healty_instances[0]
        return False
