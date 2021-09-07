# -*- coding: utf-8 -*-
'''
    convert_ckpt_dtype.py:  ckpt 32精度 转换16精度
'''
import os
import tensorflow as tf
import tf2pb
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

src_ckpt = r'/home/tk/tk_nlp/script/ner/ner_output/bert/model.ckpt-2704'
dst_ckpt = r'/root/model_16fp.ckpt'
#转换32 to 16
tf2pb.convert_ckpt_dtype(src_ckpt,dst_ckpt)
