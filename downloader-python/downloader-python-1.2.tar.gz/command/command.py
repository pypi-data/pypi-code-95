import argparse
import time
import os
parser = argparse.ArgumentParser(description="your script description")            # description参数可以用于插入描述脚本用途的信息，可以为空
parser.add_argument('--time', '-time', action='store_true', help='verbose mode')   # 添加--verbose标签，标签别名可以为-v，这里action的意思是当读取的参数中出现--verbose/-v的时候


# 参数字典的verbose建对应的值为True，而help参数用于描述--verbose参数的用途或意义。
args = parser.parse_args()
if args.time:
    while True:
        print(time.ctime(),end='\n')


