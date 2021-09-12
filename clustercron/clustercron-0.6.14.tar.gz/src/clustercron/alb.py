# clustercron/alb.py
# vim: ts=4 et sw=4 sts=4 ft=python fenc=UTF-8 ai
# -*- coding: utf-8 -*-

'''
clustercron.alb
---------------

Modules holds class for AWS ElasticLoadBalancing v2 (ALB)
'''

from __future__ import unicode_literals

import logging

import boto3
from botocore.exceptions import NoRegionError

from .lb import Lb

logger = logging.getLogger(__name__)


class Alb(Lb):
    def _get_target_health(self):
        target_health = []
        logger.debug('Get instance health states')
        try:
            client = boto3.client('elbv2')
        except NoRegionError as error:
            if self.region_name is None:
                logger.error('%s', error)
                return target_health
            else:
                client = boto3.client(
                    'elbv2',
                    region_name=self.region_name,
                )
        try:
            targetgroups = client.describe_target_groups(Names=[self.name])
        except client.exceptions.TargetGroupNotFoundException as error:
            logger.error(
                'Could not get TargetGroup `%s`: %s',
                self.name,
                error,
            )
        else:
            try:
                targetgroup_arn = targetgroups.get('TargetGroups')[0][
                    'TargetGroupArn'
                ]
            except Exception as error:
                logger.error(
                    'Could not get TargetGroupArn for `%s`: %s',
                    self.name,
                    error,
                )
            else:
                logger.debug('targetgroup_arn: %s' % targetgroup_arn)
                try:
                    target_health = client.describe_target_health(
                        TargetGroupArn=targetgroup_arn
                    )
                except Exception as error:
                    logger.error('Could not get target health: %s', error)
        return target_health

    def get_healty_instances(self):
        healty_instances = []
        target_health = self._get_target_health()
        if target_health:
            logger.debug('Instance health states: %s', target_health)
            try:
                healty_instances = sorted(
                    x['Target']['Id']
                    for x in target_health.get('TargetHealthDescriptions')
                    if x['TargetHealth']['State'] == 'healthy'
                )
            except Exception as error:
                logger.error('Could not parse healty_instances: %s', error)
            else:
                logger.info(
                    'Healty instances: %s', ', '.join(healty_instances)
                )
        return healty_instances
