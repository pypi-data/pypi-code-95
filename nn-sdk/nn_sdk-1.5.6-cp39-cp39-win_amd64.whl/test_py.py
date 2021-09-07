# -*- coding: utf-8 -*-
from nn_sdk import *
config = {
    "model_dir": r'/root/model.ckpt',
    "aes":{
        "use":False,
        "key":bytes([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]),
        "iv":bytes([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]),
    },
    "log_level": 4,
    'engine':0,
    "device_id": 0,
    'tf':{
        "ConfigProto": {
            "log_device_placement": False,
            "allow_soft_placement": True,
            "gpu_options": {
                "allow_growth": True
            },
            "graph_options":{
                "optimizer_options":{
                    "global_jit_level": 1
                }
            },
        },
        "engine_version": 1,
        "model_type": 1,# 0 pb , 1 ckpt
        "fastertransformer":{
            "use": False,
            "cuda_version":"11.3", #当前依赖 tf2pb,支持10.2 11.3 ,
        }
    },
    'onnx':{
        "engine_version": 1,
    },
    'trt':{
        "engine_version": 8,
        "enable_graph": 0,
    },
    "graph": [
        {
            "input": [
                {"node":"input_ids:0", "data_type":"int64", "shape":[1, 256]},
                {"node":"input_mask:0", "data_type":"int64", "shape":[1, 256]}
            ],
            "output": [
                {"node":"pred_ids:0", "data_type":"int64", "shape":[1, 256]},
            ],
        }
    ]}

seq_length = 256
input_ids = [[1] * seq_length]
input_mask = [[1] * seq_length]
sdk_inf = csdk_object(config)
if sdk_inf.valid():
    net_stage = 0
    ret, out = sdk_inf.process(net_stage, input_ids,input_mask)
    print(ret)
    print(out)
    sdk_inf.close()