import logging

from master import utils


def join():
    logging.info("[Join]")

    # send join info
    token = utils.get_join_token(ttl_hash=utils.get_ttl_hash())
    kube_version, cni_version, containerd_version = utils.get_compatible_versions()

    join_info = {
        "JOIN_TOKEN": token,
        "KUBERNETES_VERSION": kube_version,
        "KUBERNETES_CNI_VERSION": cni_version,
        "CONTAINERD_VERSION": containerd_version
    }

    return join_info
