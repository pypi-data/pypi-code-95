# clustercron/elb.py
# vim: ts=4 et sw=4 sts=4 ft=python fenc=UTF-8 ai
# -*- coding: utf-8 -*-

'''
clustercron.elb
---------------

Modules holds class for AWS ElasticLoadBalancing (ELB)
'''

from __future__ import unicode_literals

import logging

import boto3
from botocore.exceptions import NoRegionError

from .lb import Lb

logger = logging.getLogger(__name__)


class Elb(Lb):
    def _get_instance_health(self):
        inst_health = {'InstanceStates': []}
        logger.debug('Get instance health ')
        try:
            client = boto3.client('elb')
        except NoRegionError as error:
            if self.region_name is None:
                logger.error('%s', error)
                return inst_health
            else:
                client = boto3.client(
                    'elb',
                    region_name=self.region_name,
                )
        try:
            inst_health = client.describe_instance_health(
                LoadBalancerName=self.name,
            )
        except Exception as error:
            logger.error('Could not get instance health: %s', error)
        return inst_health

    def get_healty_instances(self):
        healty_instances = []
        inst_health = self._get_instance_health()
        logger.debug('Instance health states: %s', inst_health)
        try:
            healty_instances = sorted(
                [
                    x['InstanceId']
                    for x in inst_health['InstanceStates']
                    if x['State'] == 'InService'
                ]
            )
        except Exception as error:
            logger.error('Could not parse healty_instances: %s', error)
        else:
            logger.info('Healty instances: %s', ', '.join(healty_instances))
        return healty_instances
