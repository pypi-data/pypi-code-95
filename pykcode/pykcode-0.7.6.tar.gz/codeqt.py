'''20210908
'''
import os
import sys
from collections import defaultdict
import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc
import PyQt5.QtGui as qtg
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import numpy as np
import ctypes
# 修正setWindowIcon显示在任务栏的问题
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")
# 修正ui在不同分辨率屏幕上的尺寸问题
qtc.QCoreApplication.setAttribute(qtc.Qt.AA_EnableHighDpiScaling)
app = qtw.QApplication(sys.argv)
LOOP_STARTED = False

# 窗口显示栈，当前显示窗口为栈的第一个窗口
WINDOW_STACK = []
# 广播机制，里面的数据结构是
# {"msgid1":{"message":"tom","handlers":[func1,func2]},
#  "msgid2":{"message":"[1,2,3,4,5]","handlers":[func3,func4]}}
MESSAGE_HANDLERS = {}


class EchoMode:
    Normal = qtw.QLineEdit.Normal
    NoEcho = qtw.QLineEdit.NoEcho
    Password = qtw.QLineEdit.Password
    EchoOnInput = qtw.QLineEdit.PasswordEchoOnEdit


class MsgButton:
    Ok = qtw.QMessageBox.Ok
    Yes = qtw.QMessageBox.Yes
    No = qtw.QMessageBox.No
    Abort = qtw.QMessageBox.Abort
    Retry = qtw.QMessageBox.Retry
    Ignore = qtw.QMessageBox.Ignore
    Close = qtw.QMessageBox.Close
    Cancel = qtw.QMessageBox.Cancel
    Open = qtw.QMessageBox.Open
    Save = qtw.QMessageBox.Save


class MsgMode:
    I = qtw.QMessageBox.information, '信息', MsgButton.Ok
    Q = qtw.QMessageBox.question, '询问', MsgButton.Yes | MsgButton.No
    W = qtw.QMessageBox.warning, '警告', MsgButton.Yes | MsgButton.No
    C = qtw.QMessageBox.critical, '错误', MsgButton.Abort


class CodeQTSingals(qtc.QObject):
    changeWindow = qtc.pyqtSignal(qtw.QMainWindow)
    messageSingal = qtc.pyqtSignal(dict)
    int_signal = qtc.pyqtSignal(int)
    float_signal = qtc.pyqtSignal(float)
    str_signal = qtc.pyqtSignal(str)
    list_signal = qtc.pyqtSignal(list)
    dict_signal = qtc.pyqtSignal(dict)
    empty_signal = qtc.pyqtSignal()
    ndarray_signal = qtc.pyqtSignal(np.ndarray)
    #20210908新增
    bool_signale = qtc.pyqtSignal(bool)


###############################################
#
# 2021年8月20日新增UIWidget
# 自定义QWidget用来“膨胀”自定义组件视图
# 为QWidget组件
#
###############################################


class UIWidget(qtw.QWidget):
    def __init__(self, widget_ui, objname="Form"):
        super().__init__(parent=None)
        # 根据objname的不同
        # 动态的执行代码为self.ui赋值
        exec(f"self.ui=widget_ui.Ui_{objname}()")
        self.ui.setupUi(self)

    def get_widget(self, obj_name):
        '''
        根据组件的objectName获取对应的组件对象
        '''
        if hasattr(self.ui, obj_name):
            return getattr(self.ui, obj_name)
        else:
            raise SystemExit(f"没有objectName为{obj_name}的组件")

    def set_image(self, obj_name, path):
        if hasattr(self.ui, obj_name):
            obj = getattr(self.ui, obj_name)
            obj.setStyleSheet(f"border-image:url({path})")

    def get_text(self, id):
        wi = self.get_widget(id)
        if wi and hasattr(wi, "text"):
            return wi.text()
        else:
            raise SystemExit("无法获取该组件文本内容")

    def set_text(self, obj_name, text):
        w = self.get_widget(obj_name)
        if hasattr(w, 'setText'):
            w.setText(text)
        else:
            raise SystemExit('该组件无法设置文本')


class Window(qtw.QMainWindow):
    def __init__(self, myui):
        super().__init__(parent=None)
        if hasattr(myui, 'Ui_Form'):
            self.ui = myui.Ui_Form()
        else:
            self.ui = myui
        # 引用QApplication对象
        self.app = app
        # 自定义Widget，防止出现重名
        self.mywidgets = {}
        # 添加在QMainWindow上的事件及该事件对应的处理函数
        self.mysignals = defaultdict(list)
        # 委托给QMainWindow进行事件和处理的QMainWindow上的其它组件
        self.watchedwidgets = defaultdict(dict)
        # Ui_Form执行setupUi，完成ui布局文件控件的创建和引用
        self.setup_ui()
        # back到跳转过来的window
        # self.back_to_window = None
        # 各种自定义信号
        self.codeqt_signals = CodeQTSingals()
        self.media_player = QMediaPlayer(self)
        self.media_player.stateChanged.connect(self.do_mediaplayer_statechanged)
        # 2021年8月21日03:40新增
        self.show_exec_flag = False
        # 2021年8月21日03:40新增
        # 看一下start_thread是否执行完毕
        self.is_thread_runnging = False

        self.tasks = []

    # 2021年8月21日4点19分新增方法
    # 在一个线程中执行func函数
    def start_thread(self, func, *args, **kwargs):
        this = self

        class MyThread(qtc.QThread):
            def __init__(self) -> None:
                super().__init__()

            def run(self) -> None:
                this.is_thread_runnging = True
                func(*args, **kwargs)
                this.is_thread_runnging = False

        # self.thread = MyThread()
        t = MyThread()
        self.tasks.append(t)
        t.start()
        # self.thread.start()

    def do_mediaplayer_statechanged(self, state):
        if state == QMediaPlayer.PlayingState:
            # print('player is playing')
            pass
        if state == QMediaPlayer.PausedState:
            # print('player is pausing')
            pass
        if state == QMediaPlayer.StoppedState:
            # print('player is stopped')
            # 当QMediaPlayer播放完当前的mp3文件后
            # 或继续锁定该mp3文件
            # 通过指定一个空的QMediaContent用来替换掉先前的MP3文件(例如word.mp3)
            # 然后就可以对word.mp3文件进行读写操作了
            self.media_player.setMedia(QMediaContent())

    def eventFilter(self, a0, e) -> bool:
        '''QWidget方法，进行重载
        参数说明：
        a0: 执行过installEventFilter，也就是委托Window代理事件的组件对象
        e: e是在a0上发生的事件对象(QEvent)
        重载eventFilter并不会处理a0上发生的所有事件，只处理通过watch_widget为a0"注册"的事件类型

        '''
        if a0 in self.watchedwidgets:
            if e.type() in self.watchedwidgets[a0]:
                func = self.watchedwidgets[a0][e.type()]
                func(e)

        return super().eventFilter(a0, e)

    def watch_widget(self, widget, event_type, func):
        ''' 由Window对象代理widget的事件处理
        参数说明：
        widget: 组件对象
        event_type: 事件的类型，例如QEvent.MouseMove,QEvent.MouseButtonDblClick
        func: 当widget上发生了event型事件时，触发func函数
        installEventFilter函数会将参数widget上发生的所有事件均委托给Window来处理
        通过Window的watchedwidgets，Window只会处理在widget上发生的event_type事件
        当然，可以为一个widget注册多个事件
        '''
        widget.installEventFilter(self)
        self.watchedwidgets[widget][event_type] = func

    def event(self, e):
        if e.type() in self.mysignals.keys():
            for func in self.mysignals[e.type()]:
                func(e)
        return super().event(e)

    # 注册在窗体上发生的事件和处理函数
    def window_event(self, e, func):
        self.mysignals[e].append(func)

    # 注销在窗体上发生的事件和处理函数
    def remove_window_event(self, e, func):
        self.mysignals[e].remove(func)

    # 注册在窗体上发生的事件和处理函数
    def window_siganl(self, signal, func):
        self.mysignals[signal].append(func)

    # 注销在窗体上发生的事件和处理函数
    def remove_window_siganl(self, signal, func):
        self.mysignals[signal].remove(func)

    # 等待子类改写
    def setup(self):
        pass

    def get_text(self, id):
        wi = self.get_widget(id)
        if wi and hasattr(wi, "text"):
            return wi.text()
        else:
            raise SystemExit("无法获取该组件文本内容")

    def setup_ui(self):
        '''
        ui布局文件控件的创建和引用
        '''
        self.ui.setupUi(self)

    def broadcast(self, msgid, messages):
        '''
        参考Android的BroadcastReceiver机制
        broadcast函数用来广播一个msgid新消息
        并且将该消息通知到关注该信息的所有函数（目前函数是排队执行）
        '''
        if msgid not in MESSAGE_HANDLERS:
            MESSAGE_HANDLERS[msgid] = {"message": {}, "handlers": []}
        msg = MESSAGE_HANDLERS.get(msgid)
        msg["message"] = messages
        funcs = msg.get("handlers")
        for func in funcs:
            func(messages)

        # print(MESSAGE_HANDLERS)

    def receiver(self, msgid, func):
        '''
        参考Android的BroadcastReceiver机制
        receiver函数用来注册一个关注msgid消息的函数
        '''
        if msgid not in MESSAGE_HANDLERS:
            MESSAGE_HANDLERS[msgid] = {"message": {}, "handlers": []}
        msg = MESSAGE_HANDLERS.get(msgid)
        funcs = msg.get("handlers")
        funcs.append(func)
        # print(MESSAGE_HANDLERS)

    def set_label_background(self, obj_name, colorname):
        wi = self.get_widget(obj_name)
        wi.setStyleSheet(f"background-color:{colorname};")

    def on_value_changed_do(self, widgt, func):
        if isinstance(widgt, qtw.QWidget):
            widgt.valueChanged.connect(func)

    def remove_click_label(self, obj_name):
        '''使用QLabel组件的默认mousePressEvent函数
        来处理id为obj_name的QLabel组件点击事件。
        '''
        wi = self.get_widget(obj_name)
        wi.mousePressEvent = lambda event: qtw.QLabel.mousePressEvent(
            self.get_widget(obj_name), event)

    def on_click_label(self, obj_name, func, *args, **kwargs):
        # print(obj_name, '--------------->', func)
        '''
        QLabel的鼠标点击处理方式与QPushButton不同
        QLabel通过内置mousePressEvent函数来处理鼠标单击事件
        所以单独设置一个on_click_label函数来处理对QLabel对象的点击
        func函数为用户自定义的真正事件处理函数
        myfunc用来调用默认实现
        '''
        def myfunc(event):

            func(*args, **kwargs)  # 执行自定义函数功能
            # 执行完自定义函数后，调用QLabel默认函数处理后续QLabel默认功能
            return qtw.QLabel.mousePressEvent(self.get_widget(obj_name), event)

        wi = self.get_widget(obj_name)

        wi.mousePressEvent = myfunc

    def remove_click_button(self, widget):
        # 如果传入的是QPushButton组件对象
        if isinstance(widget, qtw.QWidget):
            widget.clicked.disconnect()
        # 如果传入的是QPushButton组件的ID
        elif isinstance(widget, str):
            self.remove_click_button(self.get_widget(widget))

    def on_click_button(self, widgt, func):
        '''
        将func作为单击QPushButton时产生的clicked信号的槽函数
        来处理单击事件
        '''
        # 如果传入的是QPushButton组件对象，则直接为对象绑定clicked信号的槽函数
        if isinstance(widgt, qtw.QWidget):
            widgt.clicked.connect(func)
        # 如果传入的是QPushButton组件的ID，则获取ID对应的组建后再绑定clicked的槽函数
        elif isinstance(widgt, str):
            self.on_click_button(self.get_widget(widgt), func)

    def msg_box(self, msg, type=MsgMode.I, buttons=None):
        '''
        利用QMessageBox弹出提示框
        QMessageBox相关常量被封装到了MsgMode类中
        '''
        func = type[0]
        title = type[1]
        if buttons is None:
            buttons = type[2]
        return func(self, title, msg, buttons)

    def play_media(self, filename, vol=100):
        abs_path = os.path.abspath(filename)
        url = qtc.QUrl.fromLocalFile(abs_path)
        c = QMediaContent(url)
        self.media_player.setMedia(c)
        self.media_player.play()
        self.media_player.setVolume(vol)

    def set_echomode(self, obj_name, mode):
        '''
        设置QLineEdit的内容显示形式
        '''
        wi = self.get_widget(obj_name)
        if isinstance(wi, qtw.QLineEdit):
            wi.setEchoMode(mode)

    def get_widget(self, obj_name):
        '''
        根据组件的objectName获取对应的组件对象
        '''
        if hasattr(self.ui, obj_name):
            return getattr(self.ui, obj_name)
        else:
            raise SystemExit(f"没有objectName为{obj_name}的组件")

    def set_canvas(self, x0, y0, w, h, bg='black', fg='white', size=5):
        win = self

        class Canvas(qtw.QWidget):
            def __init__(self, parent) -> None:
                super().__init__(parent=parent)
                self.lastpoint = qtc.QPoint()
                self.endpoint = qtc.QPoint()
                self.bg = bg
                self.fg = fg
                self.size = size
                self.pix = qtg.QPixmap(w, h)
                if hasattr(qtc.Qt, bg):
                    self.pix.fill(getattr(qtc.Qt, bg))

            def set_objname(self, objname):
                self.setObjectName(objname)
                win.mywidgets[objname] = self
                setattr(win.ui, objname, self)

            def get_image(self):
                return self.pix

            def clear(self):
                self.pix.fill(getattr(qtc.Qt, bg))
                self.lastpoint = qtc.QPoint()
                self.endpoint = qtc.QPoint()
                self.update()

            def paintEvent(self, e):
                painter = qtg.QPainter(self.pix)
                pen = qtg.QPen()
                pen.setWidth(self.size)
                pen.setColor(getattr(qtc.Qt, fg))
                painter.setPen(pen)
                p = qtg.QPainter(self)
                if self.lastpoint != self.endpoint:
                    painter.drawLine(self.lastpoint, self.endpoint)
                    self.lastpoint = self.endpoint
                p.drawPixmap(0, 0, self.pix)

            def mousePressEvent(self, e) -> None:
                self.lastpoint = e.pos()
                self.endpoint = self.lastpoint

            def mouseMoveEvent(self, e) -> None:
                self.endpoint = e.pos()
                self.update()

            def mouseReleaseEvent(self, e) -> None:
                self.endpoint = e.pos()
                self.update()

        canvas = Canvas(self)
        canvas.setGeometry(qtc.QRect(x0, y0, w, h))
        return canvas

    def draw_text(self,
                  x,
                  y,
                  content,
                  font="微软雅黑",
                  size=14,
                  color="black",
                  width=100,
                  height=100,
                  angle=0):
        '''
        20210901新增方法，可以在窗口书写文字
        '''
        class My_Inner_Widget(qtw.QWidget):
            def __init__(self, parent) -> None:
                super().__init__(parent=parent)
                self.font = qtg.QFont(font, size)

            def paintEvent(self, a0: qtg.QPaintEvent):
                p = qtg.QPainter(self)
                if type(color) == "str":
                    p.setPen(qtg.QColor(color))
                else:
                    r, g, b = color
                    p.setPen(qtg.QColor(r, g, b))
                p.rotate(angle)
                p.setFont(self.font)
                p.drawText(a0.rect(), qtc.Qt.AlignLeft, content)

        mywidget = My_Inner_Widget(self)
        mywidget.setGeometry(qtc.QRect(x, y, width, height))
        return mywidget

    def draw_image(self, imagename, x0, y0, w=0, h=0, angle=0):
        '''
        创建自定义控件Widget，通过重写其paintEvent
        该自定义Widget外形是在paintEvent中绘制的图像
        20210901新增参数角度angle，默认值0
        '''
        class MyImage(qtw.QWidget):
            def __init__(self, parent) -> None:
                super().__init__(parent=parent)
                self.change_x = 0
                self.change_y = 0
                self.img = qtg.QPixmap(imagename)
                # 使用qtg.QTransform对象来旋转图片
                transform = qtg.QTransform().rotate(angle)
                self.img = self.img.transformed(transform,
                                                qtc.Qt.SmoothTransformation)

                if w and h:
                    self.imgw = w
                    self.imgh = h
                else:
                    self.imgw = self.img.width()
                    self.imgh = self.img.height()

                self.img.scaled(self.imgw, self.imgh)

                self.dir_x = 1  # 向右
                self.dir_y = 1  # 向下

            def move(self, x=10, y=10):
                self.move_x(x)
                self.move_y(y)

            def move_x(self, dist_x=10):

                i = dist_x / abs(dist_x)
                if self.dir_x == i and self.change_x == 0:
                    # 初始方向与要前进的方向一致
                    self.change_x = dist_x
                if self.dir_x == -i and self.change_x == 0:
                    # 初始方向与要前进的方向不一致
                    self.change_x = abs(dist_x)
                    self.dir_x = -1
                    self.flip()
                pos_x = self.x() + self.dir_x * self.change_x
                self.setGeometry(
                    qtc.QRect(pos_x, self.y(), self.width(), self.height()))

            def move_y(self, dist_y=10):
                i = dist_y / abs(dist_y)
                if self.dir_y == i and self.change_y == 0:
                    # 初始方向与要前进的方向一致
                    self.change_y = dist_y
                if self.dir_y == -i and self.change_y == 0:
                    # 初始方向与要前进的方向不一致
                    self.change_y = abs(dist_y)
                    self.dir_y = -1
                pos_y = self.y() + self.dir_y * self.change_y
                self.setGeometry(
                    qtc.QRect(self.x(), pos_y, self.width(), self.height()))

            def turnover_x(self):
                self.dir_x *= -1

            def turnover_y(self):
                self.dir_y *= -1

            def flip(self):
                transform = qtg.QTransform().rotate(180, qtc.Qt.YAxis)
                self.img = self.img.transformed(transform,
                                                qtc.Qt.SmoothTransformation)
                self.repaint()

            def paintEvent(self, a0: qtg.QPaintEvent):
                p = qtg.QPainter(self)
                p.drawPixmap(0, 0, self.imgw, self.imgh, self.img)

        mywidget = MyImage(self)
        mywidget.setGeometry(qtc.QRect(x0, y0, mywidget.imgw, mywidget.imgh))
        return mywidget

    def set_piximage(self, objname, imgname, angle=0):
        '''20210902新增方法，为组件添加pixmap前景图
        图像会根据控件的大小被缩放
        '''
        img = qtg.QPixmap(imgname)
        # 使用qtg.QTransform对象来旋转图片
        transform = qtg.QTransform().rotate(angle)
        img = img.transformed(transform, qtc.Qt.SmoothTransformation)
        mywidget = self.get_widget(objname)
        if hasattr(mywidget, "setScaledContents"):
            mywidget.setScaledContents(True)
        mywidget.setPixmap(img)

    def add_widget(self, WidgetClazz, objname, x0, y0, w, h):
        '''
        动态添加Widget
        '''
        if objname not in self.mywidgets.keys():
            mywidget = WidgetClazz(self)
            mywidget.setObjectName(objname)
            mywidget.setGeometry(qtc.QRect(x0, y0, w, h))
            self.mywidgets[objname] = mywidget
            setattr(self.ui, objname, mywidget)
        else:
            raise SystemExit('重复的objname')

    def set_title(self, title):
        '''
        设置QMainWindow的窗口标题
        '''
        self.setWindowTitle(title)

    def set_icon(self, path):
        '''
        设置QMainWindow的窗口图标和任务栏图标
        '''
        self.setWindowIcon(qtg.QIcon(path))

    def set_text(self, obj_name, text):
        w = self.get_widget(obj_name)
        if hasattr(w, 'setText'):
            w.setText(text)
        else:
            raise SystemExit('该组件无法设置文本')

    def is_loop_statred():
        return LOOP_STARTED

    def change_window(self, w):
        self.codeqt_signals.changeWindow.connect(w.show)
        self.codeqt_signals.changeWindow.emit(self)
        self.hide()
        # 2021年8月21日03:40新增
        self.show_exec_flag = False
        ##########################
        self.codeqt_signals.changeWindow.disconnect(w.show)

    def back_window(self):
        '''
        类似Android的back功能键
        如果当前窗口是从A窗口跳转过来的，则该函数会跳转会B窗口
        '''
        if WINDOW_STACK[0] == self:
            # 2021年8月21日03:40新增
            self.show_exec_flag = False
            ##########################
            WINDOW_STACK.pop(0).hide()
            WINDOW_STACK[0].show()

    # def to_window(self, w, flag=True):
    #     w.show()
    #     w.back_to_window = self
    #     if flag:
    #         self.hide()

    # # 返回到跳转过来的窗口
    # def back(self):
    #     if self.back_to_window:
    #         self.to_window(self.back_to_window)
    #         self.back_to_window = None

    def remove_label_image(self, obj_name):
        if hasattr(self.ui, obj_name):
            obj = getattr(self.ui, obj_name)
            if type(obj) == qtw.QLabel:
                img = qtg.QPixmap("")
                obj.setPixmap(img)
                obj.setScaledContents(True)
            else:
                raise SystemExit("只能去除QLabel的图片")

    def show(self) -> None:
        '''
        让窗口显示
        '''
        self.setup()
        # 只要show函数获得执行，就意味着self将被显示出来
        # 凡是当前显示窗口就是WINDOW_STACK最上方的窗口
        WINDOW_STACK.insert(0, self)
        # 2021年8月21日03:40新增
        self.show_exec_flag = True
        return super().show()

    ##################
    # 2021年8月21日03:38新增
    # 判定窗口是否执行了show()指令
    #
    ##################

    def is_show(self):
        return self.show_exec_flag

    def set_image(self, obj_name, path):
        if hasattr(self.ui, obj_name):
            obj = getattr(self.ui, obj_name)
            obj.setStyleSheet(f"border-image:url({path})")

    def set_image_with_border(self,
                              obj_name,
                              path,
                              width=1,
                              color="red",
                              rad=0):
        if hasattr(self.ui, obj_name):
            obj = getattr(self.ui, obj_name)
            pix = qtg.QPixmap(path)
            obj.setPixmap(pix)
            obj.setScaledContents(True)
            if isinstance(color, str):
                obj.setStyleSheet(
                    f"background-color:white; padding:6px;border-radius:{rad}; border-width:{int(width)}px;border-style:solid;border-color:{color};"
                )
            else:
                r, g, b = color
                obj.setStyleSheet(
                    f"background-color:white; padding:6px;border-radius:{rad}; border-width:{int(width)}px;border-style: solid;border-color: rgb({r},{g},{b});"
                )


def get_image_size(pathname):
    '''获得图形的尺寸信息：宽度，高度
    '''
    img = qtg.QImage(pathname)
    return img.size().width(), img.size().height()


def run():
    global LOOP_STARTED
    if not LOOP_STARTED:
        LOOP_STARTED = True
        sys.exit(app.exec())
