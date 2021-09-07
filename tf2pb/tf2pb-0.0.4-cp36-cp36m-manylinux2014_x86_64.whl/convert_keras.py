# -*- coding: utf-8 -*-
'''
        convert_keras.py: keras h5py 权重 转换pb:
'''
import sys
import tensorflow as tf
import tf2pb
from keras.models import Model
ready_config = {
    "floatx": "float32",  # float16, float32 当前模型(ckpt_filename)的精度
    "fastertransformer":{
        "use":  0,# 0 普通模型转换 , 1 启用fastertransormer
        "cuda_version": "11.3", # 当前支持 10.2, 11.3
        "int8_mode": 0,# 不建议修改
        "remove_padding": False # 不建议修改
    }
}
#初始化
tf2pb.ready(ready_config)

config = {
    'model': None,# 训练构建的模型
    'weight_filename' : '/root/weight_filename.weights', #训练权重 h5py格式
    'input_tensor' : {
        "input_ids": None, # 对应输入Tensor 例如 bert.Input[0]
        "input_mask": None, # 对应输入Tensor 例如 bert.Input[1]
    },
    'output_tensor' : {
        "pred_ids": None,
    },
    'save_pb_file': r'/root/save_pb_file.pb' #保存pb路径
}
#直接转换
tf2pb.freeze_keras_pb(config)