#coding:gbk
import os

def open_url_exe():
    message = input("open：")
    if message == '':
        print("要打开的为空！")
    else:
        os.system(f"start {message}")