from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import *
from PyQt5.uic import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
#from downloader import *
import sys
import requests
import os
import datetime
import time
from colorama import *
from web import *
from PyQt5.Qt import PYQT_VERSION_STR
from PyQt5.QtCore import QT_VERSION_STR
import os
import subprocess
from pip_install import install,uninstall

init(autoreset=True)


Ui_MainWindow,_ = loadUiType('sources/downloader.ui')
Fast_link,_ = loadUiType('sources/fast_link.ui')
Python_script,_ = loadUiType('sources/python_script.ui')
py_inst,_ = loadUiType('sources/py.ui')
class moudle_installer(QtWidgets.QMainWindow,py_inst):
    def __init__(self):
        super(moudle_installer,self).__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.install)


    def install(self):
        text = ''
        for i in install(self.lineEdit.text()):
            text += i
        self.textBrowser.setText(text)



class PS(QtWidgets.QMainWindow,Python_script):
    un = pyqtSignal()
    def __init__(self):

        super(PS, self).__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.runs)
    def runs(self):
        self.un.emit()
    def run_script(self):
        try:
            s = self.textEdit.toPlainText()
            with open('test.py','w') as f:
                f.write(s)
            tex = ''

            for i in self.os_popen(f'{sys.executable} test.py'):
                tex += i
            if tex:
                self.textBrowser.setText(tex)
            else:
                self.textBrowser.setText('It is Empty!Is Exception happened?Please look of cmd or Idle output.')
        except BaseException as e:
            print(e,sys.executable)
    def os_popen(self,strt):
        try:
            self.textBrowser.setText('')
            re = os.popen(strt).readlines()
            return re
        except BaseException as e:
            print(e)
class Fast(QtWidgets.QMainWindow,Fast_link):
    a = pyqtSignal()
    b = pyqtSignal()
    def __init__(self):

        super(Fast, self).__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.start_PS)
        self.pushButton_2.clicked.connect(self.b.emit)
    def start_PS(self):
        self.a.emit()




class window(QtWidgets.QMainWindow,Ui_MainWindow):
    signal = pyqtSignal()
    fast_link = pyqtSignal()
    def __init__(self):


        self.log(f'[{time.ctime()}][main/Info] loading')

        super(window,self).__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.download)
        self.te = ''
        self.progressBar.setValue(0)
        self.pushButton_2.clicked.connect(self.fwa)
        self.pushButton_3.clicked.connect(self.fast)
        self.wdw = ''



        self.setWindowIcon(QIcon('sources/icon.bmp'))
        self.log(f'[{time.ctime()}][main/Info] icon loaded')

        try:
            self.load()
            self.log(f'[{time.ctime()}][main/Info] load settings.properties sucsess')
        except BaseException as e:


            self.log(f'[{time.ctime()}][main/Error] error in initlazing:{e}',Fore.RED)

            self.log(r'*\**:( Downloader Crashed! ):**/*',Fore.RED)
            sys.exit(self.show())

        self.timer = QTimer()
        self.timer.timeout.connect(self.write)
        self.timer.start(500)
        self.log(f'[{time.ctime()}][main/Info] timer initlazing sucsess')
        self.log(
            f'[{time.ctime()}][main/Info] backend library:PyQt5 version {PYQT_VERSION_STR} build on Qt {QT_VERSION_STR}')
    def fast(self):
        self.log(
            f'[{time.ctime()}][main/Info] fast link started')
        self.fast_link.emit()
    def log(self,text,color=Fore.RESET):
        print(color+text)
        try:
            self.wdw += '\n' + text
            self.textBrowser_2.setText(self.wdw)
        except BaseException:
            self.wdw = ''
            self.wdw += text + '\n'
            self.tab_4 = QtWidgets.QWidget()
            self.tab_4.setObjectName("tab_4")
            self.textBrowser_2 = QtWidgets.QTextBrowser(self.tab_4)
            self.textBrowser_2.setGeometry(QtCore.QRect(5, 1, 761, 221))
            self.textBrowser_2.setObjectName("textBrowser_2")
            self.textBrowser_2.setText(self.wdw)

    def opencmd(self):
        os.system('cmd')
    def fwa(self):

        self.close()
    def print(self):
        self.log(f'[{time.ctime()}][main/Info] stopping!')

    def load(self):

        a = open('properties/settings.properties')

        dic = eval(a.read())
        if dic[0]:
            self.checkBox.toggle()
        if dic[1]:
            self.checkBox_2.toggle()
        if dic[2]:
            self.checkBox_3.toggle()
        self.lineEdit.setText(dic[3])
        self.lineEdit_2.setText(dic[4])
    def closeEvent(self,event):
        result = QtWidgets.QMessageBox.question(self,'close','Close?',QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if result == QtWidgets.QMessageBox.Yes:
            self.print()
            event.accept()

        else:
            event.ignore()
    def write(self):

        a = open('properties/settings.properties','w')
        dic = [None,None,None,None,None]
        if self.checkBox.isChecked():
            dic[0] = True
        else:
            dic[0] = False

        if self.checkBox_2.isChecked():
            dic[1] = True
        else:
            dic[1] = False

        if self.checkBox_3.isChecked():
            dic[2] = True
        else:
            dic[2] = False
        dic[3] = self.lineEdit.text()
        dic[4] = self.lineEdit_2.text()

        a.write(str(dic))


    def download(self):
        self.log(f'[{time.ctime()}][main/Info] Downloading')
        self.u(0)
        a = datetime.datetime.now()
        self.u(1)
        self.te = ''
        self.u(3)
        self.textBrowser.setText(self.te)
        self.u(4)
        self.update('initlazing')
        self.u(5)

        try:
            self.u(10)
            self.update('getting')
            self.u(20)
            if not self.checkBox.isChecked():
                if self.lineEdit_3.text() == '':
                    header = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 Edg/92.0.902.78'}
                else:
                    header = header = {'user-agent':self.lineEdit_3.text()}

                r = requests.get(self.lineEdit.text(),headers = header)
            else:
                r = requests.get(self.lineEdit.text())
            self.u(30)
            con = r.content
            self.u(40)
            text = self.lineEdit.text().split('/')
            self.u(50)
            self.update('downloading')
            self.u(60)
            aaaaa = self.lineEdit_2.text()+text[-1].replace('/','')\
            .replace(r'\\', '')\
            .replace(':', '')\
            .replace('*', '')\
            .replace('?', '')\
            .replace('"','') \
            .replace('<', '') \
            .replace('>', '') \
            .replace('|', '') \

            aaa = str(time.time())
            with open(aaaaa,'ab+') as f:
                self.u(70)
                self.update('writing')
                self.u(80)
                f.write(con)
                self.u(90)
            self.u(101)
            b = datetime.datetime.now()
            x = b-a
            x = x.total_seconds()
            if not self.checkBox_2.isChecked():
                print(f'[{time.ctime()}][main/Info] Download from {self.lineEdit.text()} sucsess')
                size = float(os.path.getsize(aaaaa))
                if size >= 1024 and size <= 1024*1024:
                    self.update(f'sucsess in {x}s({size/1024}KB,{size/1024/x}KB/s)')
                elif size >= 1024*1024 and size <= 1024*1024*1024:
                    self.update(f'sucsess in {x}s({size/1024/1024}MB,{size/1024/1024/x}MB/s)')
                elif size >= 1024*1024*1024 and size <= 1024*1024*1024*1024:
                    self.update(f'sucsess in {x}s({size/1024/1024/1024}GB,{size/1024/1024/1024/x}GB/s)')
                elif size >= 1024*1024*1024*1024:
                    self.update(f'sucsess in {x}s({size/1024/1024/1024/1024}TB,{size/1024/1024/1024/1024/x}TB/s)')
                else:
                    self.update(f'sucsess in {x}s({size}B,{size/x}B/s)')
            else:
                self.update(f'sucsess in {x}s')
                self.log(f'[{time.ctime()}][main/Info] Download from {self.lineEdit.text()} sucsess')

        except BaseException as e:
            self.u(0)
            if not self.checkBox_3.isChecked():
                self.update(f'error:{e}')
            else:
                self.update(f'failed')


            self.log(f'[{time.ctime()}][main/Warn] error in download:{e},ignored',Fore.YELLOW)







    def update(self,t):
        self.te += t + '\n'
        self.textBrowser.setText(self.te)
    def u(self,v):
        a = self.progressBar.value()
        if v > a:
            for i in range(a,v):
                self.progressBar.setValue(i)
                time.sleep(0.001)
        else:

            self.progressBar.setValue(v)
if __name__ == '__main__':


    app = QtWidgets.QApplication(sys.argv)
    d = moudle_installer()
    a = PS()
    a.un.connect(a.run_script)
    fast = Fast()
    fast.a.connect(a.show)
    fast.b.connect(d.show)

    window = window()
    window.show()
    window.fast_link.connect(fast.show)

    sys.exit(app.exec_())
else:
    print(f'[{time.ctime()}][main/Info] now varbile "__name__"={__name__},run in web mode')
    run('1.0.8')



