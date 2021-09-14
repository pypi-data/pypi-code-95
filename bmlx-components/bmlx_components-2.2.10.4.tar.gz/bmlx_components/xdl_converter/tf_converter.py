import queue
import logging
import os
import json
import subprocess
import tempfile
from bmlx.utils import io_utils
from bmlx.fs.file_system import LocalFileSystem
import tensorflow as tf
from tensorflow.core.framework import types_pb2
from xdl.python.ops.ps_ops import ps_local_read_variables
from xdl.python.backend.tf.convert_utils import TF2XDL


def remove_stop_gradient(graph):
    stop_nodes = {}
    for node in graph.node:
        if node.op == "StopGradient":
            stop_nodes[node.name] = node.input[0]

    for node in graph.node:
        for i in range(len(node.input)):
            if node.input[i] in stop_nodes:
                node.input[i] = stop_nodes[node.input[i]]


def find_prev_node(nodes, name, reserve_nodes):
    all_nodes = {node.name: node for node in nodes}
    q = queue.Queue()
    q.put(all_nodes.get(name, None))
    while not q.empty():
        node = q.get()
        if node is not None:
            reserve_nodes[node.name] = node
            for n in node.input:
                n = n[: n.rfind(":")] if n.rfind(":") >= 0 else n
                if n in reserve_nodes:
                    continue
                q.put(all_nodes[n])


def rewrite_graph_input(origin_model_conf, graph):
    short_name_dict = {}
    for name, _ in origin_model_conf["inputs"].items():
        short_name = name.split(":")[0]
        short_name_dict[short_name] = name

    for n in graph.node:
        if n.name not in short_name_dict:
            continue

        input_element = origin_model_conf["inputs"][short_name_dict[n.name]]

        if n.op == "Placeholder":
            if "dim" in input_element and "combiner" in input_element:
                if (
                    input_element["dim"] == 0
                    and input_element["combiner"] != "tile"
                ):
                    input_element["dim"] = n.attr["shape"].shape.dim[1].size
                elif input_element["combiner"] == "tile":
                    assert input_element["dim"] != 0
                    assert (
                        n.attr["shape"].shape.dim[1].size % input_element["dim"]
                        == 0
                    )
                    input_element["tile_count"] = (
                        n.attr["shape"].shape.dim[1].size / input_element["dim"]
                    )
            else:
                assert n.attr["shape"].shape.dim[1].size == input_element["dim"]
        else:
            n.op = "Placeholder"
            n.ClearField("input")
            n.ClearField("attr")
            n.attr["dtype"].type = types_pb2.DataType.DT_FLOAT
            dim1 = n.attr["shape"].shape.dim.add()
            dim1.size = -1
            dim2 = n.attr["shape"].shape.dim.add()
            dim2.size = input_element["dim"]


def get_reserve_nodes(graph, origin_model_conf):
    reserve_nodes = {}
    output_list = origin_model_conf["output"]
    if not isinstance(origin_model_conf["output"], list):
        output_list = [origin_model_conf["output"]]
    for output in output_list:
        find_prev_node(graph.node, output, reserve_nodes)
    return reserve_nodes


def delete_unused_nodes(graph, reserve_nodes):
    find_name = 0
    delete_idxs = []
    idx = 0
    for node in graph.node:
        if node.name in reserve_nodes:
            find_name += 1
        else:
            delete_idxs.append(idx)
        idx += 1

    pre_node_size = len(graph.node)
    for i in delete_idxs[::-1]:
        logging.info("delete node: %s", graph.node[i].name)
        del graph.node[i]

    post_node_size = len(graph.node)

    logging.info(
        "before cutoff size: %d, after cutoff size: %d",
        pre_node_size,
        post_node_size,
    )
    logging.info(
        "reserve_node_size: %d, find_name: %s", len(reserve_nodes), find_name
    )


def delete_unused_inputs(graph, origin_model_conf, reserve_nodes):
    cutoff_nodes = [
        node.name for node in graph.node if node.name not in reserve_nodes
    ]

    unused_input = 0
    exclude_slots = []

    logging.info("cutoff_nodes: %s", cutoff_nodes)
    for name, info in origin_model_conf["inputs"].items():
        short_name = name.split(":")[0]
        if short_name in cutoff_nodes:
            unused_input += 1
            del origin_model_conf["inputs"][name]
            if "slot" in info:
                exclude_slots.append(str(info["slot"]))

    logging.info("total delete input: %d", unused_input)
    logging.info("exclude slot: %s, len:%d", exclude_slots, len(exclude_slots))
    return exclude_slots


def delete_unused_emb_info(origin_model_conf, exclude_slots):
    emb_slot_to_slot_dict = {}
    exclude_emb_slots = []
    for var_name, info in origin_model_conf["inputs"].items():
        if "emb_slot" in info and "slot" in info:
            emb_slot_str = str(info["emb_slot"])

            emb_slot_to_slot_dict.setdefault(emb_slot_str, [])
            emb_slot_to_slot_dict[emb_slot_str].append(str(info["slot"]))

    for var_name, _ in origin_model_conf["emb_bin_info"].items():
        idx = var_name.rfind("/")
        emb_slot = var_name

        if idx != -1:
            emb_slot = var_name[idx + 1 :]

        need_del = True
        for slot in emb_slot_to_slot_dict[emb_slot]:
            if slot not in exclude_slots:
                need_del = False
                break

        if need_del:
            exclude_emb_slots.append(emb_slot)
            del origin_model_conf["emb_bin_info"][var_name]

    logging.info(
        "exclude_emb_slots: %s, len:%d",
        exclude_emb_slots,
        len(exclude_emb_slots),
    )

    for slot, _ in origin_model_conf["emb_slot_dim_dict"].items():
        if slot in exclude_emb_slots:
            del origin_model_conf["emb_slot_dim_dict"][slot]


def remove_unused_subgraph(origin_model_conf, graph):
    rewrite_graph_input(origin_model_conf, graph)
    remove_stop_gradient(graph)
    reserve_nodes = get_reserve_nodes(graph, origin_model_conf)
    delete_unused_nodes(graph, reserve_nodes)
    exclude_slots = delete_unused_inputs(
        graph, origin_model_conf, reserve_nodes
    )
    delete_unused_emb_info(origin_model_conf, exclude_slots)


def convert_graph(output_node, model_path):
    with tf.compat.v1.Session() as sess:
        # 1. import graph
        tf.compat.v1.train.import_meta_graph(
            os.path.join(model_path, "tf_predict_graph_0.pb")
        )
        names = []
        denses = []
        for v in tf.compat.v1.global_variables():
            names.append(v.name[0:-2])
            denses.extend(
                ps_local_read_variables(
                    model_path,
                    [v.name[0:-2]],
                    [TF2XDL.convert_type(v.dtype.base_dtype)],
                )
            )

        # 2. trans dense to const and frozen graph
        assert len(denses) == len(names)

        i = 0
        for v in tf.compat.v1.global_variables():
            if v.name[0:-2] == names[i]:
                op = v.assign(denses[i])
                sess.run(op)
                i += 1
        assert len(denses) == i

        real_output_node = None
        # protect_identity = []
        for n in tf.compat.v1.get_default_graph().as_graph_def().node:
            if n.name.endswith(output_node):
                assert real_output_node is None, (
                    "Node endswith %s doesn't uniq in graph" % output_node
                )
                real_output_node = n.name

        assert real_output_node is not None, (
            "Can't find output node endswith %s in tf graph" % output_node
        )

        logging.info("real_output_node: %s", real_output_node)

        frozen_graph = tf.compat.v1.graph_util.convert_variables_to_constants(
            sess,
            tf.compat.v1.get_default_graph().as_graph_def(),
            [real_output_node],
        )

        frozen_graph = tf.compat.v1.graph_util.remove_training_nodes(
            frozen_graph
        )

        return frozen_graph, real_output_node


def get_tf_graph_inputs(origin_model_conf, frozen_graph):
    trace_vars = []
    for _, info in origin_model_conf["trace_vars"].items():
        trace_vars.append(info["target_tensor"][0:-2])
    logging.info("trace_vars: %s", trace_vars)

    inputs = []
    for n in frozen_graph.node:
        if n.op == "Placeholder" or n.name in trace_vars:
            inputs.append(n.name)
    return inputs


def optimize_graph(
    optimize_tool_remote_path,
    fronzen_graph,
    model_conf,
    optimized_graph_remote_path,
):
    assert io_utils.exists(optimize_tool_remote_path)

    with tempfile.TemporaryDirectory() as tempdir:
        local_graph_path = os.path.join(tempdir, "graph.bin")
        local_conf_path = os.path.join(tempdir, "model.json")

        io_utils.write_string_file(
            local_graph_path, fronzen_graph.SerializeToString()
        )
        io_utils.write_string_file(
            local_conf_path,
            json.dumps(model_conf, indent=4, sort_keys=True).encode(),
        )

        optimize_tool_path = os.path.join(
            tempdir, os.path.basename(optimize_tool_remote_path)
        )
        io_utils.write_string_file(
            optimize_tool_path,
            io_utils.read_file_string(optimize_tool_remote_path),
        )
        # tensorflow 等so lib 在xdl convert 安装的时候，放到了该目录，直接使用
        optimize_lib_path = "/usr/lib/python3.7/site-packages/model_convert-1.0-py3.7.egg/model_convert/"
        command = "chmod +x {} && LD_LIBRARY_PATH={}:$LD_LIBRARY_PATH {} --model_path={} --output_dir ./".format(
            optimize_tool_path,
            optimize_lib_path,
            optimize_tool_path,
            tempdir,
        )

        subprocess.run(command, shell=True, check=True)

        fs = LocalFileSystem()
        result_files = [
            file_path
            for file_path in fs.ls(tempdir)
            if file_path.find("final") >= 0
        ]

        if not io_utils.exists(optimized_graph_remote_path):
            io_utils.mkdirs(optimized_graph_remote_path)

        for file_path in result_files:
            remote_path = os.path.join(
                optimized_graph_remote_path, os.path.basename(file_path)
            )
            io_utils.write_string_file(
                remote_path, io_utils.read_file_string(file_path)
            )
