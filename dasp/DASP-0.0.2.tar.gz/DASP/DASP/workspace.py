# -*- coding: utf-8 -*-
# @Time    : 2021/9/16 15:13
# @Author  : wangzhimin！
# @FileName: workspace.py
# @Blog    ：https://blog.csdn.net/qq_42197919?spm=1001.2101.3001.5343

class Employee:
    '所有员工的基类'
    empCount = 0

    def __init__(self, name, salary):
        self.name = name
        self.salary = salary
        Employee.empCount += 1

    def displayCount(self):

        return 1

    def displayEmployee(self):
        return 2

def aaa():
    return "aaa"
