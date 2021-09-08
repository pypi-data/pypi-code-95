# -*- coding: utf-8 -*-
import copy
import logging
from notification.models import TaskHistory
from dbaas_aclapi import helpers
from dbaas_aclapi.acl_base_client import get_acl_client


logging.basicConfig()
LOG = logging.getLogger("AclTask")
LOG.setLevel(logging.DEBUG)


class ReplicateACLError(Exception):
    pass


class RunJobError(Exception):
    pass


def replicate_acl_for(database, old_ip, new_ip):
    raise Exception("A")
    acl_client = get_acl_client(database.environment)
    for rule in helpers.iter_on_acl_rules(acl_client, {"destination": old_ip}):
        try:
            copy_acl_rule(rule, new_ip, acl_client, database)
            LOG.info("Rule copied: {}".format(rule))
        except Exception as e:
            error = "Rule could not be copied: {}. {}".format(rule, e)
            LOG.warn(error)
            raise Exception(error)

def destroy_acl_for(database, ip):
    acl_client = get_acl_client(database.environment)

    for environment_id, vlan_id, rule_id in helpers.iter_on_acl_query_results(
        acl_client, {"destination": ip}
    ):
        try:
            response = acl_client.delete_acl(environment_id, vlan_id, rule_id)
        except Exception as e:
            LOG.warn("Rule could not be deleted! {}".format(e))
        else:
            if 'job' in response:
                LOG.info("Rule deleted. Job: {}".format(response['job']))


def copy_acl_rule(rule, new_ip, acl_client, database):
    data = {"kind": "object#acl", "rules": []}
    new_rule = copy.deepcopy(rule)
    new_rule['destination'] = '{}/32'.format(new_ip)
    if acl_client.is_rule_executed(new_rule):
        LOG.info(
            ("ACL for rule: {} is already replicated and executed for new "
             "rule: {}".format(
                rule, new_rule
             ))
        )
        return
    data['rules'].append(new_rule)
    acl_environment, vlan = new_rule['source'].split('/')

    response, status_code = acl_client.grant_acl_for(
        environment=acl_environment, vlan=vlan, payload=data
    )
    if status_code != 201:
        raise ReplicateACLError(
            "\nError on ACL Replication \nstatus: {} \nResponse: {}".format(
                status_code, response
            )
        )
    else:
        run_job_resp, run_job_status = acl_client.run_job(
            response['job'],
            timeout=30
        )


def register_task(request, user):
    LOG.info(
        "id: {} | task: {} | kwargs: {} | args: {}".format(
            request.id,
            request.task,
            request.kwargs,
            str(request.args)
        )
    )

    task_history = TaskHistory.register(
        request=request, user=user,
        worker_name=get_worker_name()
    )
    task_history.update_details(persist=True, details="Loading Process...")

    return task_history


def get_worker_name():
    from billiard import current_process
    p = current_process()
    return p.initargs[1].split('@')[1]
