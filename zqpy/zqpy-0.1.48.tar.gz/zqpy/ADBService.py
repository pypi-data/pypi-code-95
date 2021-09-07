import time
import os
import subprocess
from LogService import LogServiceClass
from RegexService import RegexServiceClass
from enum import IntEnum

class ADBServiceClass(object):
    __Log = LogServiceClass(tag="ADBServiceClass")
    LogD = __Log.LogD
    LogW = __Log.LogW
    LogE = __Log.LogE
    __regex = RegexServiceClass()

    sleep = 0
    deviceName = None
    def __init__(self, sleep = 0):
        self.ChangeSleep(sleep)

    def ChnageDevice(self, device):
        self.deviceName = device or None

    # 改变停顿时间
    def ChangeSleep(self, sleep = 0):
        self.sleep = sleep

    # 获取复制的值
    def GetCopyValue(self, device = None):
        self.ExecuteADB("adb shell am startservice ca.zgrs.clipper/.ClipboardService", device=device)
        readLine = self.ExecuteADB("adb shell am broadcast -a clipper.get", device=device)
        if len(readLine) < 2:
            return ""
        resultData = str(readLine[1], 'utf8')
        resultData = self.__regex.GetRegexDoubleQuotation(resultData)
        return resultData

    # ADB安装应用
    def Install(self, appPath, device = None):
        time.sleep(self.sleep)
        return self.ExecuteADB("adb install {}".format(appPath), device=device)

    # 杀掉某APP
    def KillApp(self, packageName, device = None):
        time.sleep(self.sleep)        
        return self.ExecuteADB('adb shell "am force-stop {}"'.format(packageName), device=device)     #退出后台但是不会清理数据
        # print('adb shell pm clear {}'.format(packageName.split('/')[0]))
        # return self.ExecuteADB('adb shell pm clear {}'.format(packageName.split('/')[0]), device=device)        

    # 显示某个应用的 某层
    def ShowApp(self, appPackage, appLayer, device = None):
        time.sleep(self.sleep)
        return self.ExecuteADB("adb shell am start -n {}/{}".format(appPackage,appLayer), device=device)
    def ShowAppByList(self, dataList):
        if dataList and len(dataList) >= 2:
            return self.ShowApp(dataList[0], dataList[1])
        else:
            self.LogW("不存在 dataList，或者位数不够")

    # 查看当前所在的页面 属于的package 和 活动层，方便打开用
    def GetAppCurr(self, device = None):        
        time.sleep(self.sleep)
        readLine = self.ExecuteADB('adb shell dumpsys window windows | findstr "Current"', device=device,shell=True,stdout=subprocess.PIPE)
        print(readLine)
        return readLine

    # ADB点击
    def Click(self, x, y, device = None):
        time.sleep(self.sleep)
        return self.ExecuteADB("adb shell input tap {} {}".format(x,y), device=device)
    def ClickByList(self, dataList):
        if dataList and len(dataList) >= 2:
            return self.Click(dataList[0],dataList[1])
        else:
            self.LogW("不存在 dataList，或者位数不够")

    # ADB按住滑动
    def DragAndDrop(self, x1, y1, x2, y2, device = None):
        time.sleep(self.sleep)
        return self.ExecuteADB("adb shell input draganddrop {} {} {} {}".format(x1, y1, x2, y2), device=device)
    def DragAndDropByList(self, dataList):
        if dataList and len(dataList) >= 4:
            return self.DragAndDrop(dataList[0], dataList[1], dataList[2], dataList[3])
        else:
            self.LogW("不存在 dataList，或者位数不够")

    # ADB滑动
    def Swipe(self, x1, y1, x2, y2, device = None):
        time.sleep(self.sleep)
        return self.ExecuteADB("adb shell input swipe {} {} {} {}".format(x1, y1, x2, y2), device=device)
    def SwipeByList(self, dataList):
        if dataList and len(dataList) >= 4:
            return self.Swipe(dataList[0], dataList[1], dataList[2], dataList[3])
        else:
            self.LogW("不存在 dataList，或者位数不够")

    # 输入键
    def InputKeyEvent(self, content = "", device = None):
        time.sleep(self.sleep)        
        return self.ExecuteADB("adb shell input keyevent '{}'".format(content), device=device)

    # 输入内容，不支持中文  模拟器以 /mnt开头 + /sdcard手机最高目录名字
    def InputText(self, content = "", device = None):
        time.sleep(self.sleep)        
        return self.ExecuteADB("adb shell input text '{}'".format(content), device=device)
        # return self.ExecuteADB("adb shell am broadcast -a ADB_INPUT_TEXT --es msg '{}'".format(content))

    # 输入内容，支持中文  必须满足 1.安装了ADBKeyboard.apk  2.adb 1.0.32以上
    def InputTextByApp(self, content = "", device = None):
        time.sleep(self.sleep)        
        return self.ExecuteADB("adb shell am broadcast -a ADB_INPUT_TEXT --es msg '{}'".format(content), device=device)

    # 电脑文件复制到手机上，手机测不支持中文
    def PushFile(self, pcPath, androidPath, device = None):
        time.sleep(self.sleep)
        return self.ExecuteADB("adb push {} {}".format(pcPath, androidPath), device=device,stdout = subprocess.DEVNULL) # 小文件可以用subprocess.PIPE，大文件用它要崩，一直卡

    # 手机文件复制到电脑上，手机测不支持中文
    def PullFile(self, androidPath, pcPath, device = None):
        time.sleep(self.sleep)
        return self.ExecuteADB("adb pull {} {}".format(androidPath, pcPath), device=device)
    # 手机截屏
    def Screenshot(self, targetPath='', device = None):
        """
        手机截图
        :param targetPath: 目标路径
        :return:
        """
        format_time = int(time.time())
        self.ExecuteADB('adb shell screencap -p /sdcard/%s.png'%format_time, device=device)
        time.sleep(1)
        outPath = targetPath
        if targetPath == '':
            outPath = os.path.dirname(__file__)
        self.PullFile('/sdcard/%s.png' % (format_time,), outPath)
        self.RemoveFile('/sdcard/%s.png' % (format_time,))
        time.sleep(1)
        return outPath if ('.jpg' in outPath or '.png' in outPath) else ('%s%s.png' % (outPath, format_time,))
    # 移除手机文件
    def RemoveFile(self, path):
        """
        从手机端删除文件
        :return:
        """
        self.ExecuteADB('adb shell rm %s'%path)
    # 获取设备信息列表
    def Devices(self, device = None):
        time.sleep(self.sleep)
        devices = []
        readLine = self.ExecuteADB("adb devices", device=device) 
        for item in readLine:
            item = item.decode('utf-8')
            items = item.split('\t')
            if len(items) == 2:
                newItems = []
                for itemTemp in items:
                    itemTemp = itemTemp.strip().replace("-","_b_")
                    itemTemp = itemTemp.replace(".","_c_")
                    itemTemp = itemTemp.replace(":","_d_")
                    if itemTemp.split('_')[0].isdigit():
                        itemTemp = "_a_" + itemTemp
                    newItems.append(itemTemp)
                devices.append(newItems)
        return devices
    # 打开Uri
    def OpenUri(self, uri, device=None):
        time.sleep(self.sleep)
        return self.ExecuteADB('adb shell am start -a android.intent.action.VIEW -d '%uri, device=device)

    def ExecuteADB(self, adbCommand, device = None, shell = True, stdout = subprocess.PIPE):
        deviceTemp = device or self.deviceName
        if deviceTemp:
            deviceTemp = deviceTemp.replace("_a_","")
            deviceTemp = deviceTemp.replace("_b_","-")
            deviceTemp = deviceTemp.replace("_c_",".")
            deviceTemp = deviceTemp.replace("_d_",":")
            adbCommand = adbCommand.replace("adb ", "adb -s {} ".format(deviceTemp))
        popen = subprocess.Popen(adbCommand,shell=shell,stdout=stdout)
        popen.wait()
        if stdout == subprocess.PIPE:
            readLine = popen.stdout.readlines()
            return readLine
        else:
            return True

class ABDKeyEnum(IntEnum):
    KEYCODE_UNKNOWN = 0,
    KEYCODE_MENU = 1, 
    KEYCODE_SOFT_RIGHT = 2, 
    KEYCODE_HOME = 3, 
    KEYCODE_BACK = 4, 
    KEYCODE_CALL = 5, 
    KEYCODE_ENDCALL = 6, 
    KEYCODE_0 = 7, 
    KEYCODE_1 = 8, 
    KEYCODE_2 = 9, 
    KEYCODE_3 = 10,
    KEYCODE_4 = 11,
    KEYCODE_5 = 12,
    KEYCODE_6 = 13,
    KEYCODE_7 = 14,
    KEYCODE_8 = 15,
    KEYCODE_9 = 16,
    KEYCODE_STAR = 17,
    KEYCODE_POUND = 18,
    KEYCODE_DPAD_UP = 19,
    KEYCODE_DPAD_DOWN = 20,
    KEYCODE_DPAD_LEFT = 21,
    KEYCODE_DPAD_RIGHT = 22,
    KEYCODE_DPAD_CENTER = 23,
    KEYCODE_VOLUME_UP = 24,
    KEYCODE_VOLUME_DOWN = 25,
    KEYCODE_POWER = 26,
    KEYCODE_CAMERA = 27,
    KEYCODE_CLEAR = 28,
    KEYCODE_A = 29,
    KEYCODE_B = 30,
    KEYCODE_C = 31,
    KEYCODE_D = 32,
    KEYCODE_E = 33,
    KEYCODE_F = 34,
    KEYCODE_G = 35,
    KEYCODE_H = 36,
    KEYCODE_I = 37,
    KEYCODE_J = 38,
    KEYCODE_K = 39,
    KEYCODE_L = 40,
    KEYCODE_M = 41,
    KEYCODE_N = 42,
    KEYCODE_O = 43,
    KEYCODE_P = 44,
    KEYCODE_Q = 45,
    KEYCODE_R = 46,
    KEYCODE_S = 47,
    KEYCODE_T = 48,
    KEYCODE_U = 49,
    KEYCODE_V = 50,
    KEYCODE_W = 51,
    KEYCODE_X = 52,
    KEYCODE_Y = 53,
    KEYCODE_Z = 54,
    KEYCODE_COMMA = 55,
    KEYCODE_PERIOD = 56,
    KEYCODE_ALT_LEFT = 57,
    KEYCODE_ALT_RIGHT = 58,
    KEYCODE_SHIFT_LEFT = 59,
    KEYCODE_SHIFT_RIGHT = 60,
    KEYCODE_TAB = 61,
    KEYCODE_SPACE = 62,
    KEYCODE_SYM = 63,
    KEYCODE_EXPLORER = 64,
    KEYCODE_ENVELOPE = 65,
    KEYCODE_ENTER = 66,
    KEYCODE_DEL = 67,
    KEYCODE_GRAVE = 68,
    KEYCODE_MINUS = 69,
    KEYCODE_EQUALS = 70,
    KEYCODE_LEFT_BRACKET = 71,
    KEYCODE_RIGHT_BRACKET = 72,
    KEYCODE_BACKSLASH = 73,
    KEYCODE_SEMICOLON = 74,
    KEYCODE_APOSTROPHE = 75,
    KEYCODE_SLASH = 76,
    KEYCODE_AT = 77,
    KEYCODE_NUM = 78,
    KEYCODE_HEADSETHOOK = 79,
    KEYCODE_FOCUS = 80,
    KEYCODE_PLUS = 81,
    KEYCODE_MENU_2 = 82,
    KEYCODE_NOTIFICATION = 83,
    KEYCODE_SEARCH = 84,
    TAG_LAST_KEYCODE = 85,
    # 话筒静音键
    KEYCODE_MUTE = 91,
    # 向上翻页键
    KEYCODE_PAGE_UP = 92,
    # 向下翻页键
    KEYCODE_PAGE_DOWN = 93,
    # ESC键
    KEYCODE_ESCAPE = 111,
    # 删除键
    KEYCODE_FORWARD_DEL = 112,
    # 大写锁定键
    KEYCODE_CAPS_LOCK = 115,
    # 滚动锁定键
    KEYCODE_SCROLL_LOCK = 116,
    # Break/Pause键
    KEYCODE_BREAK = 121,
    # 光标移动到开始键
    KEYCODE_MOVE_HOME = 122,
    # 光标移动到末尾键
    KEYCODE_MOVE_END = 123,
    # 插入键
    KEYCODE_INSERT = 124,
    # 小键盘锁
    KEYCODE_NUM_LOCK = 143,
    # 扬声器静音键
    KEYCODE_VOLUME_MUTE = 164,
    # 放大键
    KEYCODE_ZOOM_IN = 168,
    # 缩小键
    KEYCODE_ZOOM_OUT = 169,