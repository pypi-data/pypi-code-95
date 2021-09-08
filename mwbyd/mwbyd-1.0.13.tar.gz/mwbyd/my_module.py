#my_module.py
# my_module模块

#这样在另外一个文件中用from my_module import *就这能导入列表中规定的两个名字
__all__=['money','read1']

print('from the my_module.py')

money=1000

def read1():
    print('my_module->read1->money',money)

def read2():
    print('my_module->read2 calling read1')
    read1()

def change():
    global money
    money=0
