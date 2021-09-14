import xdl
import os
import logging
from bmlx.utils import io_utils


def convert_sparse(
    exec_properties,
    ckpt_dir,
    origin_model_conf,
    emb_bin_outputdir,
    converted_model_version,
):
    # 半精度模型，需要设置flag
    half_precision = exec_properties["half_p"]
    if half_precision and xdl.get_task_index() == 0:
        io_utils.write_string_file(
            os.path.join(emb_bin_outputdir, "F16_FLAG"), "1"
        )

    emb_bin_info = origin_model_conf["emb_bin_info"]
    filter_str = ";".join(
        [
            var_name + ":" + slot_lst
            for (var_name, slot_lst) in emb_bin_info.items()
        ]
    )

    keys_count = exec_properties["keys_count"]
    if keys_count is None or not keys_count:
        keys_count = ""
    logging.info("keys_count is %s", keys_count)

    xdl.convert_sparse(
        ckpt_dir,
        emb_bin_outputdir,
        filter_str,
        default_threshold=exec_properties["export_emb_default_threshold"],
        var_threshold=exec_properties.get("var_threshold", {}),
        worker_id=xdl.get_task_index(),
        worker_num=xdl.get_task_num(),
        with_slot=exec_properties.get("with_slot", True),
        halfp=half_precision,
        last_global_step=exec_properties.get("last_global_step", 0),
        inc_num=exec_properties.get("inc_num", 0),
        keys_count=keys_count,
        model_name=exec_properties["model_name"],
        model_version=str(converted_model_version),
        localhdfs_base_dirs=exec_properties["ceto_emb_base_dir"],
    )


def get_sparse_embedding_dims(emb_bin_path):
    meta_0_path = os.path.join(emb_bin_path, "meta_0")
    if not io_utils.exists(meta_0_path):
        raise RuntimeError(
            "No meta_0 file found in emb_bin_path(%s)!" % emb_bin_path
        )

    dims = []
    file_content = io_utils.read_file_string(meta_0_path).decode()
    for line in file_content.split("\n"):
        if not line or len(line) <= 8:
            continue
        dim, _ = line[8:].split("|", 1)
        dims.append(dim)
    return dims
