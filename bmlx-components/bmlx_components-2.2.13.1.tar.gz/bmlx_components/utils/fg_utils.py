import os
import sys
import base64
import zlib
import logging
import struct
import yaml
from bmlx.utils import io_utils

def fetch_fg(fg_conf_path, fg_lib_path, local_dir):
    file_content = io_utils.read_file_string(fg_conf_path)
    io_utils.write_string_file(
        os.path.join(local_dir, os.path.basename(fg_conf_path)),
        file_content,
    )

    file_content = io_utils.read_file_string(fg_lib_path)
    io_utils.write_string_file(
        os.path.join(local_dir, os.path.basename(fg_lib_path)), file_content
    )

def parse_featurelog_line(line):
    try:
        compressed_bytes = base64.b64decode(line)
    except Exception as e:
        logging.error("Failed to decode base64 featurelog, exception: %d", e)
        return None

    origin_bytes = zlib.decompress(compressed_bytes)

    return origin_bytes

def compress_originpb_to_line(origin_pb):
    try:
        pb_str = origin_pb.SerializeToString()
        compressed = zlib.compress(pb_str)
        base64_str = base64.b64encode(compressed)
    except Exception as e:
        logging.error("Failed to compress & base64 encode pb to str, exception: %d", e)
        return None
    return base64_str

def fg_process(
    fg_dir: str,
    origin_samples_path: str,
    processed_samples_path: str,
    product_name: str,
    source: str,
):
    # import fg so
    sys.path.insert(0, fg_dir)
    import fglib_py3 as fglib_py

    processor = fglib_py.PyFeatureGenerator()
    # Create, succeed if return not 0
    fg_client = processor.Create()
    if fg_client == 0:
        raise RuntimeError("processor Create failed")

    ret = processor.InitOnce(
        fg_client,
        product_name,
        source,
        os.path.join(fg_dir, "fg.yaml"),
        "./demo.log",
        0,
        "", "", "", "", "",
    )
    with open(os.path.join(fg_dir, "fg.yaml"), "r") as f_fg:
        fg_yaml_data = f_fg.read()
        logging.info("[fg_yaml] is %s", fg_yaml_data)

    if ret != 0:
        raise RuntimeError("processor InitOnce failed")

    with open(processed_samples_path, "wb") as processed_fp:
        with open(origin_samples_path, "r") as origin_fp:
            for line in origin_fp.readlines():
                origin_bytes = parse_featurelog_line(line)
                if not origin_bytes:
                    continue

                processed_ret = processor.ProcessFeatureLog(
                    fg_client, origin_bytes, False, False,
                )
                # 新数据流的格式...
                if len(processed_ret) < 4:
                    sys.stderr.write("[too short]processed_ret: %s\n" % processed_ret)
                processed_fp.write(
                    struct.pack("<Q", len(processed_ret))
                )  # length = len(processed_ret)
                processed_fp.write(bytes(4))  # crc32(length)
                processed_fp.write(processed_ret)
                processed_fp.write(bytes(4))  # crc32(processed_ret)
                

    ret = processor.Release(fg_client)
    if ret != 0:
        raise RuntimeError("processor Release failed")
    return ret

def add_validate_offline_op(yaml_path: str):
    with open(yaml_path, "r", encoding="utf-8") as f_in:
        data = yaml.load(f_in, Loader=yaml.FullLoader)
    
    if 'offline_extra_info' not in data:
        data['offline_extra_info'] = "ValidateOfflineExtraInfo"
        with open(yaml_path, "w", encoding="utf-8") as f_out:
            yaml.dump(data, f_out)