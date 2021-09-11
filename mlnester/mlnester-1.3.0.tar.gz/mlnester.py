"""这是"nester4.py"模块，提供了一个名为print_lol()的函数，这个函数可以打印包含多个列表的列表,并使用缩进区分不同嵌套深度的列表"""
def print_lol(the_list, indent=False, level=0):
        """这个函数取一个位置参数名为"the_list",这可以是任意列表，它所有的数据项会递归地输出在屏幕上"""    
        for each_item in the_list:
                if isinstance(each_item, list):
                        print_lol(each_item, indent, level+1)
                else:
                        if indent:
                                for num in range(level):
                                        print("\t", end='')
                        print(each_item)
