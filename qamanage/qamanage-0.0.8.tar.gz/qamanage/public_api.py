import re
import subprocess
from airtest.core.api import *
from airtest.report.report import simple_report


# 此处需要传一个dev进来，怎样获取这个dev？  在airtest中有固定的方法，这个dev实际上是device()实例化出来的
def unlock_device(dev):
    dev.keyevent("224")    # 解决部分手机通过dev.adb.is_locked()这个方法识别不出来的的，直接先点亮
    try:
        if dev.adb.is_locked() is True:
            dev.keyevent("224")
            sleep(1)
        if dev.adb.is_locked() is True:
            dev.unlock()
            sleep(1)
        if dev.adb.is_locked() is True:
            dev.keyevent("HOME")
            sleep(1)
        if dev.adb.is_locked() is True:
            wake()
            sleep(1)
        if dev.adb.is_locked() is True:
            swipe((300, 1600), (300, 100))
            # 部分性能较差或者滑动有延迟的手机这里需要等待2秒才能进行判断是否解锁成功，否则在判断是否解锁成功的时候还在解锁中会导致判断解锁失败
            sleep(2)
        if dev.adb.is_locked() is True:
            print("无法解锁手机")
            return False
        else:
            print("手机已解锁")
            return True
    except:
        print("无法判断锁屏情况，直接执行解锁")
        #解锁手机
        dev.keyevent("224")
        sleep(1)
        dev.unlock()
        sleep(1)
        dev.keyevent("HMOE")
        return []


# 自动点击安卓授权弹框
def auto_click_popup(pocoa, timeout=30):
    '''
    在设定时间内查询如果有安卓授权则点同意，默认为30秒
    '''
    timer = time.time()
    while time.time() - timer < timeout:
        if pocoa("com.android.permissioncontroller:id/permission_allow_button").exists():
            time.sleep(1)
            pocoa("com.android.permissioncontroller:id/permission_allow_button").click()
            time.sleep(1)
        elif pocoa("com.android.packageinstaller:id/permission_allow_button").exists():
            time.sleep(1)
            pocoa("com.android.packageinstaller:id/permission_allow_button").click()
            time.sleep(1)
        elif pocoa("com.lbe.security.miui:id/permission_allow_button_1").exists():
            time.sleep(1)
            pocoa("com.lbe.security.miui:id/permission_allow_button_1").click()
            time.sleep(1)
        elif pocoa("com.android.systemui:id/notification_allow").exists():
            time.sleep(1)
            pocoa("com.android.systemui:id/notification_allow").click()
            time.sleep(1)
        else:
            break


# 在用这个方法之前需要配置好aapt环境，这里为解析apk包信息的方法
def analusis_apk(apk_path):
    package_info_re = re.compile(r"package: name='(.*)' versionCode='(.*)' versionName='(.*?)'.*", re.I)
    label_icon_re = re.compile(r"application: label='(.+)'.*icon='(.+)'", re.I)
    launchable_activity_re = re.compile(r"launchable-activity: name='(.+)'.*label.*", re.I)

    apk_info = {}

    cmd = 'aapt2 dump badging {}'.format(apk_path)

    command_process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    infos = command_process.stdout.readlines()

    for info in infos:
        info = info.decode('utf-8')
        if info.startswith('package:'):
            temp = package_info_re.search(info)
            apk_info['package_name'] = temp.group(1)
            apk_info['version_code'] = temp.group(2) or 0
            apk_info['version_name'] = temp.group(3)
        elif info.startswith('application:'):
            temp = label_icon_re.search(info)
            apk_info['label'] = temp.group(1)
            apk_info['icon'] = temp.group(2)
        elif info.startswith('launchable-activity:'):
            temp = launchable_activity_re.search(info)
            apk_info['default_activity'] = temp.group(1)
    # 获取包的信息可以通过这样来获取apk_info.get('package_name')
    return apk_info


# 获取文件夹内所有文件路径
def get_path(path):
    '''
    遍历指定路径文件夹的文件绝对路径并返回为list
    '''
    try:
        listdir = os.listdir(path)
        all_path = []
        for file in listdir:
            all_path.append(path + '\\' + file)
        return all_path
    except Exception as err:
        print(err)


# 指定路径导出报告
def input_report(report_name,report_path):
    '''
    传入报告名字和路径，输出报告
    '''
    reportname = time.strftime("%Y-%m-%H-%M-%S",time.localtime())  + "_" + rpname + ".html"
    path = rppath + reportname
    # path = "D:\\Program_Files\\AirTest_scripts\\波克捕鱼3D\\by3d_repot\\" + reportname
    simple_report(__file__,logpath=True,output=path)


# 将不规则文本数字转换为int数值
def getinum(tempnum):
    '''
    可将获取到的带有逗号、文本的金币数字转换成int数值，比如“1，100万”可转换成“11000000”
    '''
    tempnum = str(tempnum)
    if tempnum is not None:
        tempnum = tempnum.lower()
        if tempnum[-1] == "w" or tempnum[-1] == "万":
            tempmod = 10000
        else:
            tempmod = 1
        tempnum = re.sub("\D","",tempnum)
        tempnum = float(tempnum)
        tempnum = tempnum*tempmod
        tempnum = int(tempnum)
        return tempnum  
    else:
        return

# 将不规则文本数字转成纯数字的str文本
def getsnum(tempnum):    
    '''
    获取金币等其他货币转换成str
    '''
    tempnum = str(tempnum)
    if tempnum is not None:
        tempnum = tempnum.lower()
        tempnum = re.sub("\D","",tempnum)
        return tempnum  
    else:
        return


if __name__ == '__main__':
    print("Welcome to qamanage")