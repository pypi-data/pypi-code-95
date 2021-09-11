#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AppZoo.
# @File         : gooey_gui
# @Time         : 2021/9/9 上午9:47
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  : gooey_gui: https://blog.csdn.net/weixin_42481553/article/details/113313439
# https://www.cnblogs.com/brt2/p/13232367.html

from pprint import pprint
from meutils.pipe import *
from paddleocr import PaddleOCR
from gooey import Gooey, GooeyParser


ocr = PaddleOCR(use_angle_cls=True, lang="ch", use_gpu=False, show_log=False)


@Gooey(
    program_name='东北证券 - 工具箱',
    language='chinese',
    clear_before_run=True,
    image_dir=get_module_path('.', __file__),
    progress_regex=r"^progress: (?P<current>\d+)/(?P<total>\d+)$",
    progress_expr="current / total * 100",
)
def main():
    from PIL import Image, ImageGrab

    try:
        im = ImageGrab.grabclipboard()
        im.save("test.png")
    except:
        pass

    parser = GooeyParser(description="OCR")
    parser.add_argument('pic', metavar='图片', default='test.png',
                        widget="FileChooser")  # 文件选择框

    # parser.add_argument('Date', widget="DateChooser")  # 日期选择框
    args = parser.parse_args()  # 接收界面传递的参数

    print('\n')
    print(args)

    pprint(ocr.ocr(args.pic, cls=True))


if __name__ == '__main__':
    main()
