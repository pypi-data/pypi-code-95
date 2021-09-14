MODEL_WITH_NEW_TYPE = "XdlV9Model"
RTP_MODEL_CLASS = "RtpXdlV1"


def get_whole_inputs(origin_model_conf, tf_graph_inputs):
    whole_inputs = []
    for (ori_name, _) in origin_model_conf["inputs"].items():
        p_name = ori_name[0:-2]
        if p_name in tf_graph_inputs:
            assert origin_model_conf["inputs"][ori_name]["slot"].isdigit(), (
                "slot %s must be a digit."
                % str(origin_model_conf["inputs"][ori_name]["slot"])
            )

            if origin_model_conf["inputs"][ori_name]["slot"].isdigit():
                whole_inputs.append(
                    int(origin_model_conf["inputs"][ori_name]["slot"])
                )
    return whole_inputs


def rewrite_model_conf(
    origin_model_conf,
    tf_graph_inputs,
    output_node,
    shared_slots,
    emb_dims,
    model_name,
    model_class,
    halfp,
    local_emb: bool,
):
    model_conf = {
        "model_class": model_class,
        "half_precision_compress": halfp,
        "inputs": {},
        "output": output_node,
        "embeddings": [],
        "shared_slots": shared_slots,
    }

    # 1.fill inputs
    for (ori_name, info) in origin_model_conf["inputs"].items():
        p_name = ori_name[0:-2]
        # TODO @mengrui: 这块转换逻辑太trick，后续需要和在线一块重构
        if p_name in tf_graph_inputs:
            model_conf["inputs"][p_name] = info
            model_conf["inputs"][p_name]["slot"] = int(info["slot"])

            if model_class not in (
                MODEL_WITH_NEW_TYPE,
                RTP_MODEL_CLASS,
            ) and model_conf["inputs"][p_name]["type"] in [
                "embedding",
                "statistics",
                "statistis",
                "sub_graph",
            ]:
                model_conf["inputs"][p_name]["type"] = "sparse"

            if (
                model_class != RTP_MODEL_CLASS
                and "dim" in model_conf["inputs"][p_name]
            ):
                del model_conf["inputs"][p_name]["dim"]
            else:
                model_conf["outputs"] = [output_node]

    # 2.fill embeddings
    emb_slot_dim_dict = origin_model_conf["emb_slot_dim_dict"]
    dim_slots_map = {}

    for (emb_slot, dim) in emb_slot_dim_dict.items():
        emb_slot = str(emb_slot)
        dim_slots_map.setdefault(dim, [])
        dim_slots_map[dim].append(int(emb_slot))

    for (dim, emb_slots) in dim_slots_map.items():
        model_conf["embeddings"].append({"dim": int(dim), "slots": emb_slots})

    # 3. fill cyclone info
    if local_emb == False:
        # local_emb == True时是单机版模型，不发cyclone
        for emb_info in model_conf["embeddings"]:
            emb_info["filename"] = "cyclone://%s" % model_name

        model_conf["cyclone_table_names"] = [
            {"value": "cyclone://%s" % model_name, "key": int(i)} for i in emb_dims
        ]

    return model_conf
