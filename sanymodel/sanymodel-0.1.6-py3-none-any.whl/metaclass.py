# -*- coding: utf-8 -*-
# @Time : 2021/8/28 19:04
# @Author : gaozq
# @File : metaclass.py
# @Software: PyCharm
# @contact: gaozq3@sany.com.cn
# -*- 功能说明 -*-
#
# -*- 功能说明 -*-
import inspect
import sys
import functools


class Field(object):

    def __init__(self, name, datatype, source='File'):
        self.name = name
        self.datatype = datatype
        self.source = source

    @classmethod
    def set_instance_method(cls, func):
        @functools.wraps(func)
        def dummy(self, *args, **kwargs):
            return func(*args, **kwargs)

        setattr(cls, func.__name__, dummy)


class Turbine(object):

    def __init__(self, wind_farm, turbine_num):
        self.wind_farm = wind_farm
        self.turbine_num = turbine_num


class Sensor(object):

    def __init__(self, type_name, physical_quantity):
        self.type_name = type_name
        self.physical_quantity = physical_quantity


class Topic(object):

    def __init__(self, name, ):
        self.name = name

#
# print(__name__)
# print(sys.modules[__name__])
# print(sys.modules.get('sanymodel.func.SensorFaultDiagnosis'))
# print()
#
# print(inspect.getmembers(sys.modules.get('sanymodel.func.SensorFaultDiagnosis'), inspect.isfunction))
# print(inspect.getmembers(sys.modules[__name__], inspect.isclass))
# print(inspect.getmembers(sys.modules[__name__], inspect.ismethod))
#
# print(Field.__dict__)
# Field.set_instance_method(check_max)
#
# a = Field('a','v')
#
# print(a.check_max(1))
# print(a.check_max.__doc__)
#
#
# print(Field.__dict__)
# a = Field('a','b')
# b = a.check(51)
# print(b)
# print(a.__dict__)
# for name, class_ in inspect.getmembers(sys.modules[__name__], inspect.isclass):
#     class_().func()


# import sys
# import inspect
# import ast
# from efdir import fs
# from pprint import pprint
#
#
#
# def get_function_def_names(mod):
#    fp = inspect.getabsfile(mod)
#    code = fs.rfile(fp)
#    t = ast.parse(code)
#    g = ast.walk(t)
#    arr = list(g)
#    arr = list(filter(lambda r:type(r)==ast.FunctionDef,arr))
#    arr = list(map(lambda r:r.name,arr))
#    return(arr)
#
# mod = sympy.expr
# names = get_function_def_names(sympy.expr)
#
