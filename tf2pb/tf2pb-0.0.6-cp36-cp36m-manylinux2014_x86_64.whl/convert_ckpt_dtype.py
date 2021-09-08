# -*- coding: utf-8 -*-
'''
    convert_ckpt_dtype.py:  ckpt 32精度 转换16精度
'''
import os
import tensorflow as tf
import tf2pb
#初始化
tf2pb.ready({})
src_ckpt = r'/home/tk/tk_nlp/script/ner/ner_output/bert/model.ckpt-2704'
dst_ckpt = r'/root/model_16fp.ckpt'
#转换32 to 16
tf2pb.convert_ckpt_dtype(src_ckpt,dst_ckpt)
