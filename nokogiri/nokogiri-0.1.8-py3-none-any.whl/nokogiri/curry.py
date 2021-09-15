#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class curry:
    def __init__(self, func, *args, **kwargs):
        self.__fields__ = (func, args, kwargs)
    def _(self, *args, **kwargs):
        _func, _args, _kwargs = self.__fields__
        return self.__class__(
            _func,
            *(*_args, *args), # 部分適用される引数は後ろにくる
            **{**_kwargs, **kwargs},
        )
    def __call__(self, *args, **kwargs):
        _func, _args, _kwargs = self.__fields__
        return _func(
            *(*args, *_args), # 実際に呼ばれる時の引数は前にくる
            **{**_kwargs, **kwargs},
        )
    def __str__(self):
        _func, _args, _kwargs = self.__fields__
        parameters = ', '.join(
            ['・']+[repr(v) for v in _args]+
            [f"{k}={repr(v)}" for k, v in _kwargs.items()]
        )
        return f"{_func.__name__}({parameters})"
    def __getitem__(self, arg):
        return self._(arg)
    def __getattr__(self, arg):
        return self._(arg)
    def __repr__(self):
        return self.__str__()