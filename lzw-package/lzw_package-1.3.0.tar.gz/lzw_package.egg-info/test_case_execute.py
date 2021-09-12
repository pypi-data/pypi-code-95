import time
import tkinter as tk
import threading

window = tk.Tk()
window.title('神兵测试用例执行器v1.0.0')

scn_w, scn_h = window.maxsize()
size_xy = '%dx%d+%d+%d' % (360, 480, (scn_w-360)/2, (scn_h-480)/2)
window.geometry(size_xy)

l1 = tk.Label(window, text="所属项目ID：")
l1.grid(row=0, column=0, padx=5, pady=15)

e1 = tk.Entry(window, show=None, width=34)
e1.grid(row=0, column=1, padx=5, pady=5)

l2 = tk.Label(window, text="测试计划ID：")
l2.grid(row=1, column=0, padx=5, pady=5)

e2 = tk.Entry(window, show=None, width=34)
e2.grid(row=1, column=1, padx=5, pady=5)

l3 = tk.Label(window, text="登录Token：")
l3.grid(row=2, column=0, padx=5, pady=5)

e3 = tk.Entry(window, show=None, width=34)
e3.grid(row=2, column=1, padx=5, pady=5)

flag = False


def my_cklick():
    global flag
    if flag:
        b1.configure(text="开始")
        flag = False
        print(flag)
    else:
        var1 = e1.get().strip()
        var2 = e2.get().strip()
        var3 = e3.get().strip()
        if var1 and var2 and var3:
            if var1.isdigit() and var2.isdigit():
                print(var1, var2, var3)
            else:
                b2.configure(text="提示：ID只能为数字！")
                return
        else:
            b2.configure(text="提示：3个必填项！")
            return
        # -------------
        b1.configure(text="结束")
        flag = True
        print(flag)
        thread = threading.Thread(target=my_print)
        thread.start()


def my_print():
    global flag
    t.delete(0.0, 'end')
    print("开始执行")
    b2.configure(text="提示：开始执行中！")
    while flag:
        t.insert('end', "正在上传中......\n请不要关闭工具/浏览器！\n" , 'tag2')
        print("执行记录-------"+str(flag))
        time.sleep(0.5)
        t.see('end')
    print("结束执行")
    b2.configure(text="提示：已结束执行！")


b1 = tk.Button(window, text="开始", width=10, command=my_cklick)
b1.grid(row=3, column=0, sticky='W', padx=5, pady=5)
b2 = tk.Label(window, text="")
b2.grid(row=3, column=1, sticky='W', padx=5, pady=5)

t = tk.Text(window, height=22, width=48)
t.tag_add('tag', 'end')
t.tag_config('tag', foreground='red')
t.tag_add('tag2', 'end')
t.tag_config('tag2', foreground='green')

s = tk.Scrollbar(command=t.yview)
t.configure(yscrollcommand=s.set)
s.grid(row=4, column=2, pady=5, sticky='ns')
t.grid(row=4, column=0, pady=5, columnspan=2)

l5 = tk.Label(window, text="如有问题，请联系：EX-LINZEWU001")
l5.configure(font=('微软雅黑', '8'))
l5.grid(row=5, columnspan=2, sticky='W')

t.insert('end', '提示：\n', 'tag')
t.insert('end', '1、请打开chrome浏览器\n')
t.insert('end', '2、登录神兵后按下F12\n')
t.insert('end', '3、抓取：projectId、testCasePlanId、ws_auto\n')
t.insert('end', '4、填写到对应的文本框\n')
t.insert('end', '-' * 40)

window.mainloop()
