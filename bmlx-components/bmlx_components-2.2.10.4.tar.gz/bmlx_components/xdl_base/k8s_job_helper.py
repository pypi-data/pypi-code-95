import kubernetes as k8s
import logging
import functools
import kazoo
import os
from typing import Text
from functools import partial
from bmlx.context import BmlxContext
from kazoo.client import KazooClient
from bmlx.utils import proc_utils, json_utils, io_utils
from bmlx.execution.execution import ExecutionInfo
from kubernetes.client.rest import ApiException
from bmlx_components.xdl_base.volcano_job_desc import VolcanoJobDescRender


def launch_k8s_watcher(
    context: BmlxContext,
    execution_info: ExecutionInfo,
    extra_spec,
    command_generator,
):
    @proc_utils.retry(retry_count=3, delay=5, allowed_exceptions=(ApiException))
    def _create_job(custom_object_api, execution_info) -> None:
        namespace = execution_info.exec_properties["namespace"]

        render = VolcanoJobDescRender(
            namespace=namespace,
            image=context.image(),
            runtime_configs=execution_info.exec_properties["runtime_configs"],
            job_name=execution_info.exec_properties["job_id"],
            launch_time=execution_info.exec_properties["launch_time"],
            command_generator=command_generator,
            dns_policy=context.dnsPolicy(),
            dns_config=context.dnsConfig(),
            labels=execution_info.exec_properties["labels"],
            **extra_spec,
        )

        custom_object_api.create_namespaced_custom_object(
            group="batch.volcano.sh",
            version="v1alpha1",
            namespace=namespace,
            plural="jobs",
            body=render.spec(),
        )

        logging.info(
            "xdl train k8s job %s submitted"
            % execution_info.exec_properties["job_id"]
        )

    # --
    k8s_context = execution_info.exec_properties["runtime_configs"][
        "k8s_context"
    ].as_str()
    cluster = execution_info.exec_properties["runtime_configs"][
        "cluster"
    ].as_str("xdl-hk")
    (core_api, custom_obj_api) = _init_api(
        cluster=cluster, k8s_context=k8s_context
    )
    # 解析 XDL 的 K8S执行空间
    namespace = execution_info.exec_properties["namespace"]
    if not _resolve_namespace(core_api, namespace):
        raise RuntimeError("Failed to prepare namespace %s" % namespace)

    # 创建 k8s volcano job
    _create_job(custom_obj_api, execution_info)


def wait_k8s_job_completed(execution_info: ExecutionInfo):
    k8s_context = execution_info.exec_properties["runtime_configs"][
        "k8s_context"
    ].as_str()
    cluster = execution_info.exec_properties["runtime_configs"][
        "cluster"
    ].as_str("xdl-hk")
    (core_api, custom_obj_api) = _init_api(
        cluster=cluster, k8s_context=k8s_context
    )
    job_id = execution_info.exec_properties["job_id"]
    namespace = execution_info.exec_properties["namespace"]

    def _check_job_status():

        try:
            resource = custom_obj_api.get_namespaced_custom_object(
                group="batch.volcano.sh",
                version="v1alpha1",
                plural="jobs",
                namespace=namespace,
                name=job_id,
            )
            try:
                status_desc = resource["status"]["state"]["phase"]
                logging.info("job %s in %s state" % (job_id, status_desc))
                if "Failed" == status_desc:
                    raise proc_utils.UnexpectedErrorException()
                elif "Completed" == status_desc:
                    logging.info("job %s completed" % job_id)
                    return True
                else:
                    return False
            except KeyError as e:
                logging.warning(
                    "unexpect response from server, except: %s, resource content: %s"
                    % (e, resource)
                )
                # 这里raise exception， 目的是为了尽快clean up ，避免影响 xdl 集群
                # raise proc_utils.UnexpectedErrorException()

        except ApiException as e:
            if str(e.status) == "404":
                logging.info(
                    "record was deleted by someone else, we choose to return"
                )
                raise RuntimeError("external deleted")
            logging.exception("call k8s error")
            return False

    timeout = execution_info.exec_properties["runtime_configs"][
        "timeout"
    ].as_number()
    logging.info(
        "launched xdl jobs, we start to polling it's status, timeout: %s"
        % timeout
    )

    return proc_utils.poll_wait_until(
        check_end=_check_job_status,
        cleanup=partial(cleanup_k8s_watcher, execution_info.exec_properties),
        timeout=timeout,
        poll_period=12,
    )


def cleanup_k8s_watcher(
    exec_properties, ret=False, exec_info=None, throwError=True,
):
    k8s_context = exec_properties["runtime_configs"]["k8s_context"].as_str()
    cluster = exec_properties["runtime_configs"]["cluster"].as_str("xdl-hk")
    (core_api, custom_obj_api) = _init_api(
        cluster=cluster, k8s_context=k8s_context
    )
    job_id = exec_properties["job_id"]

    @proc_utils.retry(3, allowed_exceptions=(ApiException))
    def remove_job(namespace, job_id):
        try:
            custom_obj_api.delete_namespaced_custom_object(
                group="batch.volcano.sh",
                version="v1alpha1",
                plural="jobs",
                namespace=namespace,
                name=job_id,
                body=k8s.client.V1DeleteOptions(),
            )
            logging.info("cleanup job %s" % job_id)
        except ApiException as e:
            if str(e.status) == "404":
                logging.info("record was deleted already")

    def remove_zk_key():
        zk = KazooClient(
            hosts=",".join(
                exec_properties["runtime_configs"]["zk_addr"].as_str_seq()
            )
        )
        zk.start()
        try:
            zk.delete(f"/mlplat/bmlx/xdl-k8s/ps/{job_id}")
            zk.delete(f"/mlplat/bmlx/xdl-k8s/ps/{job_id}-ck")
        except kazoo.exceptions.NoNodeError:
            pass

    logging.info("cleanup received: %s %s" % (ret, exec_info))
    if exec_info:
        logging.warn("run %s error: %s" % (job_id, exec_info))
    else:
        if ret:
            logging.info("job %s success" % job_id)
        else:
            logging.warning("job %s failed" % job_id)

    logging.info("remove job %s" % job_id)

    remove_job(
        namespace=exec_properties["namespace"], job_id=job_id,
    )

    remove_zk_key()

    if not ret or exec_info:
        if throwError:
            raise RuntimeError("run component error: %s" % exec_info)
        else:
            logging.warning(
                "run component error, ret：%d, exec info: %s", ret, exec_info
            )
            return f"run component error, ret：{ret}, exec info: {exec_info}"
    return "success"


def _resolve_namespace(core_api, ns_name):
    try:
        ns_list = core_api.list_namespace()
    except ApiException as e:
        logging.error("Failed to list namespace, error: %s", e)
        return False

    for ns in ns_list.items:
        if ns.metadata.name == ns_name:
            return True

    try:
        body = k8s.client.V1Namespace(
            metadata=k8s.client.V1ObjectMeta(name=ns_name)
        )
        core_api.create_namespace(body)
        return True
    except ApiException as e:
        logging.error("Failed to create namespace, error: %s", e)
        return False


def _init_api(cluster, k8s_context):
    """
    初始化k8s api, 主要为了提交volcano jobs
    """
    config_file = f"{os.environ['HOME']}/.kube/config.{cluster}"
    if not io_utils.exists(config_file):
        config_file = f"{os.environ['HOME']}/.kube/config"
    if not io_utils.exists(config_file):
        raise RuntimeError(
            "Failed to get k8s config file %s or %s"
            % (
                f"{os.environ['HOME']}/.kube/config.{cluster}",
                f"{os.environ['HOME']}/.kube/config",
            )
        )
    try:
        k8s.config.load_kube_config(config_file=config_file)
    except Exception as e:
        logging.error(
            "loading kubeconfig error!, please check you kube env: %s" % e
        )
        raise RuntimeError()

    core_api = k8s.client.CoreV1Api()
    custom_obj_api = k8s.client.CustomObjectsApi()
    return (core_api, custom_obj_api)
