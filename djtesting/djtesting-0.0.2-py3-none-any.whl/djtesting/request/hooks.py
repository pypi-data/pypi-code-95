# -*- coding: utf-8 -*-
# @Time    : 2021/9/6 20:08
# @Author  : chinablue
# @Email   : dongjun@reconova.cn
# @File    : hooks.py

# HOOKS = ('args', 'pre_request', 'pre_send', 'post_request', 'response')

HOOKS = ["pre_send", "response"]


def default_hooks():
    return {event: [] for event in HOOKS}


def dispatch_hook(key, hooks, hook_data, **kwargs):
    hooks = hooks or {}

    # 如果存在钩子函数, 就执行钩子函数

    if key in hooks:

        hooks = hooks.get(key)

        # 如果钩子指向的是一个函数, 将其变成列表
        if hasattr(hooks, "__call__"):
            hooks = [hooks]

        for hook in hooks:
            _hook_data = hook(hook_data, **kwargs)

            if _hook_data is not None:
                hook_data = _hook_data

    return hook_data
