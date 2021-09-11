#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AppZoo.
# @File         : gooey_gui
# @Time         : 2021/9/9 上午9:47
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  : gooey_gui: https://blog.csdn.net/weixin_42481553/article/details/113313439

from meutils.pipe import *
from gooey import Gooey, GooeyParser

from LAC import LAC

lac = LAC(mode='lac')


@Gooey(program_name='东北证券-工具箱', language='chinese')  # language='chinese'
def main():
    parser = GooeyParser(description="金融分词")

    parser.add_argument('text', metavar='文本', default='东北证券是一家牛逼的公司', widget="TextField")  # 文件选择框

    # parser.add_argument('文件名', widget="FileChooser")  # 文件选择框
    # parser.add_argument('Date', widget="DateChooser")  # 日期选择框
    args = parser.parse_args()  # 接收界面传递的参数
    print('\n')

    print(lac.run(args.text))

    print(args.__dict__)
    print(time.ctime())


if __name__ == '__main__':
    main()
