# -*- coding: utf-8 -*-
'''
前言:
        tf2pb tensorflow模型转换pb
        convert_ckpt.py: 将tf模型ckpt转换pb模型 tf-serving pb和 fastertransformer pb
        convert_ckpt_dtype.py:  精度转换 , 将tf模型ckpt 32精度转换16精度
        convert_keras.py: 将keras h5py模型转换pb
        convert_ckpt.py 转换 fastertransformer pb 可提高1.9x加速.
        建议pb模型均可以通过nn-sdk推理
        fastertransformer pb 当前只支持linux tensorflow 1.15 cuda11.3 cuda10.0 , 其他pb不依赖。
        推荐 tensorflow 链接如下,建议使用cuda11.3.1 环境tensorflow 1.15
        tensorflow链接: https://pan.baidu.com/s/1PXelYOJ2yqWfWfY7qAL4wA 提取码: rpxv 复制这段内容后打开百度网盘手机App，操作更方便哦
'''
