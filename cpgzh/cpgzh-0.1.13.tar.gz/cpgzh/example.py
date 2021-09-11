import datetime

import pgzrun
from pgzero.rect import Rect
from pgzero.screen import Screen
from pgzero.constants import mouse
from pgzero.keyboard import keys

from cpgzh import Actor
from cpgzh import Master
from cpgzh import Font
from cpgzh import Pen

font = Font()
font1 = Font()
font2 = Font()
font1.color = 'red'
font2.color = 'blue'
font2.bold = True
font2.angle = 180

screen: Screen
WIDTH = 800
HEIGHT = 800
rect = Rect(0, 0, WIDTH, HEIGHT)
jisi = Actor('大祭司_人偶-待机-000.png', center=(400, 400))
monv = Actor('恶魔女_人偶-待机-000.png', center=(800, 400))
monv.images = [f'恶魔女_人偶-待机-{i:0>3}.png' for i in range(30)]

master = Master()
pen = Pen()


def flushImages():
    '刷新造型列表'
    now = datetime.datetime.now()
    print(f'{now.time()} 刷新造型列表')
    jisi.images = [f'大祭司_人偶-待机-{i:0>3}.png' for i in range(30)]


def update():
    '更新数据'
    jisi.run_tasks()  # 执行计划任务
    monv.run_tasks()
    if jisi.collide_pixel(monv):
        print(f'碰撞点坐标：{jisi.collide_pixel(monv)}')


def draw():
    '绘制角色'
    screen.clear()
    screen.draw.filled_rect(rect, 'white')
    jisi.draw()
    monv.draw()
    if 'text' in dir(master.data):  # 如果data中有text属性
        screen.draw.text(
            str(master.data.text),
            pos=(100, 100),
            color='red',
            fontsize=40,
        )
    # 绘制一个点
    pen.dot((300, 50), 50, '#ffff00')
    # 绘制一条线
    pen.line((250, 50), (350, 50), '#00ffff', 20)
    # 绘制圆或者圆环
    pen.circle((100, 200), 100, '#ff0000', 20)
    # 绘制椭圆或者椭圆环
    pen.ellipse((300, 200), 200, 100, '#00ff00', 20)
    # 绘制方块或者方块环
    pen.rect((500, 200), 200, 200, '#0000ff', 10, 30)
    # font样式写字
    pen.text('haha', topleft=(200, 400))
    # font1样式写字
    pen.text('haha', font=font1, center=(200, 450))
    # font2样式写字
    pen.text('haha', font=font2, center=(200, 500))


def on_mouse_down(pos, button):
    '当鼠标按下'
    print(button)
    if button == mouse.LEFT:  # 按下左键刷新造型列表
        jisi.images = jisi.images = [jisi.image]
    else:  # 按下右键停止切换造型并延迟开启
        yesOrNo = master.yes_no('是否切换造型？')
        if yesOrNo:
            jisi.create_delay_tasks(flushImages, 5, 3)  # 延迟5s重置造型列表，循环3次


def on_mouse_move(pos):
    '当鼠标移动时'
    monv.x, monv.y = pos


def on_key_down(key):
    '当键盘按下'
    # 设置全屏化
    if key == keys.A:
        master.set_fullscreen()
    # 设置窗口化
    elif key == keys.B:
        master.set_windowed()
    # 切换全屏和窗口化
    elif key == keys.C:
        master.toggle_fullscreen()
    # 隐藏鼠标
    elif key == keys.D:
        master.hide_mouse()
    # 显示鼠标
    elif key == keys.E:
        master.show_mouse()
    # 输入文本
    elif key == keys.F:
        text = master.input('请输入一个名字:')
        print(text)
    # 选择文件
    elif key == keys.G:
        text = master.select_file('请选择一个文件：')
        print(text)
    # 保存文件
    elif key == keys.H:
        text = master.select_file_save('请选择存档保存位置：')
        print(text)
    # 选择文件夹
    elif key == keys.I:
        text = master.select_dir('请选择一个文件夹:')
        print(text)
    # 是否选择框
    elif key == keys.J:
        text = master.yes_no('是否选择女装？')
        print(text)
    # 保存master的数据
    elif key == keys.K:
        master.save_data()
    # 手动加载存储的数据
    elif key == keys.L:
        #master.data.text = 'test'
        master.data_path = '测试.dat'
        master.load_data()
    # 删除保存的数据
    elif key == keys.M:
        master.del_data()
    # 设置动画的帧率
    elif key == keys.N:
        fps = master.input('请输入动画切换的速度(每s切换多少次)：')
        jisi.animate_fps = int(fps)
    # 切换造型是否切换
    elif key == keys.O:
        jisi.toggle_animate()
    # 提示信息
    elif key == keys.P:
        master.msg('提示：\n你已经换好女装了')
    # 警告信息
    elif key == keys.Q:
        master.warning('警告:\n今天的女装不太完美')
    # 错误信息
    elif key == keys.R:
        master.error('错误：\n你还没换好女装')
    # 游戏开始
    elif key == keys.S:
        print(master.data.start())
    # 获取游戏运行时常
    elif key == keys.T:
        print(master.data.get_time())


pgzrun.go()
