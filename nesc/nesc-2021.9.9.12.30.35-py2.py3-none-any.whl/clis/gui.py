#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AppZoo.
# @File         : gooey_gui
# @Time         : 2021/9/9 上午9:47
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  : gooey_gui: https://blog.csdn.net/weixin_42481553/article/details/113313439


from gooey import Gooey, GooeyParser


@Gooey(program_name='答辩', ) # language='chinese'
def main():
    parser = GooeyParser(description="东北证券")
    parser.add_argument('文件名', widget="FileChooser")  # 文件选择框
    parser.add_argument('Date', widget="DateChooser")  # 日期选择框
    args = parser.parse_args()  # 接收界面传递的参数
    print(args)


if __name__ == '__main__':
    main()
