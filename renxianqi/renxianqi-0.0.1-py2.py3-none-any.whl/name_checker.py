# -*- coding: utf-8 -*-
# @Time : 2021/8/29 10:30 上午
# @Author : LeiXueWei
# @CSDN/Zhihu: 雷学委
# @XueWeiTag: CodingDemo
# @File : name_listing.py
# @Project : hello


from tkinter import *
import time

from itertools import chain
from pypinyin import pinyin, Style

from name_parser import parse_names_text

TITLE = '[人贤齐]活动出席人数检查小工具'
BG_COLOR = 'skyblue'
LOG_LINE_NUM = 0
SHOW_DEBUG = True


def debug(log):
    if SHOW_DEBUG:
        print(str(log))


def text2pinyin(text):
    return ''.join(chain.from_iterable(pinyin(text, style=Style.FIRST_LETTER)))


def current_time():
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    return current_time


class LXW_NAME_LISTING_GUI():
    def __init__(self, root):
        self.root = root
        self.log_line_no = 0

    def setup_root_win(self):
        # 窗口标题，大小，颜色设置。
        self.root.title(TITLE)
        self.root.geometry('605x600')
        self.root.configure(bg=BG_COLOR)
        # self.root.resizable(0, 0)  # 阻止Python GUI的大小调整
        # 组件标签
        self.data_label = Label(self.root, width=10, background="tomato", text="预期全部人员")
        self.banner_label = Label(self.root, width=2, height=25, background="black", text="")
        self.result_label = Label(self.root, width=10, background="tomato", text="实际出席人数")
        # 处理数据按钮
        self.process_btn = Button(self.root, text="开始校验", fg="red", bg="blue", width=10,
                                  command=self.compare_data)
        self.log_label = Label(self.root, width=10, background="tomato", text="缺席人员")
        # 文本展示框
        self.all_member_text = Text(self.root, width=40, height=25)
        self.attended_text = Text(self.root, width=40, height=25)
        self.log_text = Text(self.root, width=85, height=9)
        # 布局
        self.data_label.grid(row=0, column=0, sticky=W)
        self.banner_label.grid(row=0, column=1, rowspan=2, sticky=W)
        self.result_label.grid(row=0, column=2, sticky=W)
        self.all_member_text.grid(row=1, column=0, sticky=W)
        self.attended_text.grid(row=1, column=2, sticky=W)
        self.process_btn.grid(row=2, column=0, sticky=W)
        self.log_label.grid(row=3, column=0, columnspan=3, sticky=W)
        self.log_text.grid(row=4, column=0, columnspan=3, sticky=W)

    def compare_data(self):
        all_data = self.all_member_text.get(1.0, END).strip()
        attended_data = self.attended_text.get(1.0, END).strip()
        debug("all_data=%s " % all_data)
        debug("attended_data=%s " % attended_data)
        if not attended_data or not all_data:
            self.log_on_text("[LEI_XUE_WEI:ERROR] Empty data!")
            return
        try:
            all_names = parse_names_text(all_data)
            all_attended = parse_names_text(attended_data)
            diff = set(all_names).difference(set(all_attended))
            diff_len = len(diff)
            diff_msg = '缺少：' + str(diff_len) + '\n' + '\n'.join(diff)
            self.log_text.delete(1.0, END)
            self.log_text.insert(1.0, diff_msg)
            self.log_on_text("[LEI_XUE_WEI:INFO] handle_data_source success")
        except Exception as e:
            debug(e)
            self.log_text.delete(1.0, END)
            self.log_text.insert(1.0, "名单解析失败！")

    def log_on_text(self, message):
        message_in = "\n" + str(current_time()) + " " + str(message) + "\n"
        if self.log_line_no < 10:
            self.log_line_no = self.log_line_no + 1
            self.log_text.insert(END, message_in)
        else:
            self.log_text.delete(1.0, 2.0)
            self.log_text.insert(END, message_in)


def app_start():
    root = Tk()
    leixuewei_ui = LXW_NAME_LISTING_GUI(root)
    leixuewei_ui.setup_root_win()
    # 进入事件循环，保持窗口运行
    root.mainloop()


if __name__ == "__main__":
    # 启动程序
    app_start()
