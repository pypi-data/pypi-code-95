import os
import logging
import re
import tempfile

from bmlx.utils import io_utils
from bmlx_components.utils import ceto_publisher
from bmlx_components.utils.common_tools import digit_to_bytescount
from bmlx_components.utils import rtp_validator

HDFS_HOST_MAP = {
    "eu": "hdfs://bigo-eu",
    "sg": "hdfs://bigocluster",
}
CETO_MODEL_ROOT_DIR = "/data/models"
CETO_EMB_ROOT_DIR = "hdfs://bigocluster/data/embs"

EMB_META_PATTERN = "([a-zA-Z0-9\-_]+/[0-9]+/[0-9]+)/[0-9]+/"

def get_embeddings(emb_bin_path):
    fs, path = io_utils.resolve_filesystem_and_path(emb_bin_path)
    paths = fs.ls(path)

    assert len(paths) >= 1
    fpath = paths[0]

    res_paths = {}
    if fpath.find("emb_bin/meta_") < 0:
        raise ValueError(
            "Invalid emb bin meta file %s, should contains 'emb_bin/meta_0'"
            % fpath
        )
    file_content = io_utils.read_file_string(fpath).decode()
    for line in file_content.split("\n"):
        if not line or len(line) <= 8:
            continue

        dim, misc = line[8:].split("|", 1)
        meta_0_path, start, end, count, size = misc.split(",", 4)
        s = re.match(EMB_META_PATTERN, meta_0_path)
        if not s:
            raise ValueError(
                "Invalid emb path (%s) in meta_0, should has info like 'model_name/1610000000/13/0/' "
                % meta_0_path
            )
        real_path = s.group(1)
        emb_file_size = digit_to_bytescount(int(size))
        logging.info("[emb_%s] size : %s",
            dim, emb_file_size
        )

        emb_path = os.path.join(
            CETO_EMB_ROOT_DIR,
            real_path
        )
        res_paths.update({dim : emb_path})
    return res_paths

def publish_graph_and_emb(
        model_name,
        model_version,
        namespace,
        graph_path,
        embedding_path,
        target,
        validation_samples_path = "",
        validate_accuracy = "",
        validate_rate = "",
    ):
    assert len(target) > 0

    emb_paths = get_embeddings(embedding_path)
    logging.info("[emb_paths] are %s", emb_paths)

    emb_path_for_validate = ""

    # copy file to ceto"s model dir
    graph_dir_name = os.path.join(
        "upload",
        os.path.basename(graph_path)
    )
    logging.info("[graph_dir_name]%s", graph_dir_name)
    ceto_model_base_path = os.path.join(
        namespace, model_name, str(model_version)
    )
    ceto_model_path = os.path.join(
        CETO_MODEL_ROOT_DIR, ceto_model_base_path
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        local_upload_path = os.path.join(
            tmpdir, graph_dir_name
        )
        logging.info("[upload_path]%s", local_upload_path)
        io_utils.download_dir(
            graph_path, local_upload_path
        )
        # upload emb with graph
        for dim in emb_paths:
            io_utils.download_dir(
                emb_paths[dim],
                os.path.join(
                    local_upload_path,
                    f"emb/{dim}"
                )
            )

        for dest in target:
            io_utils.upload_dir(
                local_upload_path,
                os.path.join(
                    HDFS_HOST_MAP[dest].rstrip('/'), ceto_model_path.lstrip('/')
                )
            )
            logging.info("upload graph to %s hdfs finish.", dest)

    if validation_samples_path is not None:
        emb_path_for_validate = os.path.join(
            HDFS_HOST_MAP[target[0]].rstrip('/'), ceto_model_path.lstrip('/'), "emb"
        )
        logging.info("[emb_path_for_validate]%s", emb_path_for_validate)

        check_res = rtp_validator.validate_ahead(
            validation_samples_path,
            graph_path,
            model_name,
            model_version,
            validate_accuracy,
            validate_rate,
            target[0],
            emb_path_for_validate
        )
        if check_res:
            logging.info(
                "============================================================"
            )
            logging.info("[validation_ahead] Pass!")
        else:
            logging.info(
                "============================================================"
            )
            logging.info("[validation_ahead] Fail!")
            raise RuntimeError("Validation failed, stop publishing!")

    # update meta to ceto
    for dest in target:
        ret = ceto_publisher.publish_model_to_ceto(
            model_name, namespace, model_version, ceto_model_path, dest
        )
        if not ret:
            logging.error(
                "Failed to publish model to %s ceto, model name: %s, namespace: %s, model_version: %s, ceto_model_path: %s",
                dest,
                model_name,
                namespace,
                model_version,
                ceto_model_path,
            )
            raise RuntimeError("Failed to publish model to ceto!")
        else:
            logging.info(
                "Successfully publish model to %s ceto, model name: %s, namespace: %s, model_version: %s, ceto_model_path: %s",
                dest,
                model_name,
                namespace,
                model_version,
                ceto_model_path,
            )