# 好强大的 pyautogui， 能根据图识别图,然后循环操作
# 可以参考： https://blog.csdn.net/yzy_1996/article/details/85244714
# 可以考虑 算手机分辨率，然后实现手机点击
import cv2
import aircv as ac
import pyautogui
import os, time
import jieba
from PIL import Image
# from appium import webadb
from pytesseract import image_to_string
from ADBService import ADBServiceClass

class AIServiceClass():

    def __init__(self):
        self.adbService = ADBServiceClass()

    def img_contain_img_get_pos_list(self, img1, img2): 
        ''' 
        查找img2在img1的位置（坐标从左上角开始）
        return 匹配到的所有的列表(第一个列表相识度最高)
        '''
        imsrc = ac.imread(img1) # 原始图像
        imsch = ac.imread(img2) # 带查找的部分
        match_result=ac.find_all_template(imsrc, imsch,0.80)
        #提取出中心点的横纵坐标
        points=[]
        for i in match_result:
            # [result点坐标，rectangle四个角坐标=>左上坐下右上右下，confidence匹配度=>0.8以上基本就是了]
            points.append((i['result']))
        return points
    
    def img_contain_img_click_pos(self, img1, img2, isWin, isMultiTouch, click_num=1):
        ''' 
        点击img2在img1的位置
        isWin: 电脑是分辨率，手机需要换算分辨率和屏幕大小
        isMultiTouch: 是否是多点触控（所以满足的点，都点击）
        click_num: 点击次数
        return {state:是否点击成功,msg:消息提示}
        '''
        resultData = {'state': False, 'msg':''}
        pos_list = self.img_contain_img_get_pos_list(img1, img2)
        if not pos_list or len(pos_list)==0:
            resultData['msg'] = '没有匹配到对应图'
        else:
            for item in pos_list[:]:
                if isWin:
                    pyautogui.moveTo(item[0],item[1])
                    pyautogui.click(clicks=click_num, interval=0.2)
                else:
                    for clickIndex in range(0, click_num):
                        self.adbService.Click(item[0],item[1])
                        time.sleep(0.2)
                if not isMultiTouch:
                    break
            resultData['state'] = True
        return resultData

    def img_contain_text_get_pos_list(self, text, img, isRemoveOutBox=True, isShowLog=False):
        '''
        instruction:
        基于tesseract识别出文字(不同语言有不同的文字识别库，此处用的是中文库 chi_sim，主要用于识别中文 )，
        返回文字在屏幕上的坐标点列表。

        usage:
        text = '带查找文字'
        img = '图片地址.png'
        isRemoveOutBox = '结束是否移除数据文件'

        return 匹配到的所有的列表(第一个列表相识度最高)
        '''
        outSuffix = '.box'
        outName='out'
        outFullName='%s%s'%(outName, outSuffix)

        if os.path.exists(img):
            strValue = image_to_string(img, lang='chi_sim')
            if isShowLog:
                print(strValue)
            os.system('tesseract %s %s -l chi_sim makebox'%(img, outName))
            print('输出坐标文件 : %s'%outFullName)
        else:
            print('%s is not exists'%img)

        pos_list = []
        if os.path.exists(outFullName):
            with open(outFullName,'r', encoding='UTF-8') as f:
                for line in f:
                    if line.split()[0] in text:
                        pos_list.append(line.split())

        if os.path.exists(outFullName) and isRemoveOutBox:
            os.remove(outFullName)

        return pos_list

    def img_contain_text_click_pos(self, text, img, isWin, click_num=1, isHorizontal=True, isRemoveImg=True, isRemoveOutBox=True, isShowLog=False):
        '''
        点击文字在图片中的位置
        基于tesseract识别出文字(不同语言有不同的文字识别库，此处用的是中文库 chi_sim，主要用于识别中文 )，
        return {state:是否点击成功,msg:消息提示}

        usage:
        text = '带查找文字'
        img = '图片地址.png'
        isWin: 电脑是分辨率，手机需要换算分辨率和屏幕大小
        click_num: 点击次数
        isRemoveImg = '结束是否移除Img'
        isRemoveOutBox = '结束是否移除数据文件'
        '''

        resultData = {'state': False, 'msg':''}
        pos_list = self.img_contain_text_get_pos_list(text, img, isRemoveOutBox)

        if not pos_list or len(pos_list) == 0:
            resultData['msg'] = '没有匹配到对应字'
        else:
            if isShowLog:
                print(pos_list)
            xCenterPointList, yCenterPointList, xCenterPointSum, yCenterPointSum, x, y = [], [], 0, 0, 0, 0
            for item in pos_list[:]:
                tempXCenterPoint = (int(item[1]) + int(item[3]))/2
                xCenterPointList.append(tempXCenterPoint)
                xCenterPointSum = xCenterPointSum + tempXCenterPoint

                tempYCenterPoint = (int(item[2]) + int(item[4]))/2
                yCenterPointList.append(tempYCenterPoint)
                yCenterPointSum = yCenterPointSum + tempYCenterPoint

            x = int(xCenterPointSum/2)
            imgInstance = Image.open(img)
            height = imgInstance.size[1]    # 获取屏幕高度

            if isHorizontal:
                # 水平，一般认为三个字的中间点Y轴是一样的，所以取一个字的Y轴就可以了
                y = int((height - int(pos_list[0][2])) + (height - int(pos_list[0][4])))/2
            else:
                print('纵向文字的高计算有问题，记录记录，后面修')
                y = int(yCenterPointSum/2)

            if isShowLog:
                print('X--> %s   Y--> %s'%(x, y))
            if isWin:
                pyautogui.moveTo(x, y)
                pyautogui.click(clicks=click_num, interval=0.2)
            else:
                for clickIndex in range(0, click_num):
                    self.adbService.Click(x, y)
                    time.sleep(0.2)
            resultData['state'] = True
        if  os.path.exists(img) and isRemoveImg:
            os.remove(img)
        return resultData

    def img_contain_text(self, img, text, lang='chi_sim', isShowContent=False):
        '''
        图片是否包含文字
        return bool
        '''
        resultStr = image_to_string(img, lang=lang)
        resultStr = resultStr.replace('\n', '').replace(' ', '')
        if isShowContent:
            print(resultStr)
        if type(text) == type([]):
            for item in text[:]:
                if item in resultStr:
                    return True
        else:
            if text in resultStr:
                return True
        return False

    def img_contain_text_jieba(self, img, text, lang='chi_sim', confidence=None, cut_all=False, isShowContent=False):
        '''
        图片是否包含某一句话（结巴）
        confidence 匹配度
        return 【传入匹配度，返回bool】【不传入匹配度，返回匹配度（0-1）】
        '''
        seg_list = jieba.cut(text)
        if not seg_list:
            return 0
        resultStr = image_to_string(img, lang=lang)
        resultStr = resultStr.replace('\n', '').replace(' ', '')
        if isShowContent:
            print(resultStr)
        used, sum = 1, 1
        for item in seg_list:
            if item[0] in resultStr:
                used += 1
            sum += 1
        confidenceT = used/sum
        if confidence:
            return confidenceT >= confidence
        else:
            return confidenceT

if __name__ == '__main__':
    # # GUI点击 clicks 点击次数
    # pyautogui.click(x=1596 ,y=1063,clicks=1, interval=2)
    # # GUI滚动鼠标
    # pyautogui.scroll(-300, x=100, y=100)
    # # 鼠标移动
    # pyautogui.moveTo(50,50)
    # # 截屏

    aiService = AIServiceClass()

    # adb = AdbTools()
    # screenshotPath = adb.screenshot('TestRes/screenshot.png')
    # print(screenshotPath)
    # print(aiService.img_contain_img_click_pos('TestRes/screenshot.png', 'TestRes/screenshotPathItem.png', False, False, 1))   #True
    # print(aiService.img_contain_img_click_pos('TestRes/1.png','TestRes/test.png', True, False, 1))   #True
    print(aiService.img_contain_img_click_pos('TestRes/Screenshot_DouYin.png','TestRes/Screenshot_DouYin_item.png', False, False, 1))   #False

    # print('-----------------------TestRes/Screenshot_DouYin.jpg-------------------------')
    # print(image_to_string('TestRes/Screenshot_DouYin.jpg', lang='chi_sim'))   #True
    # print('-----------------------TestRes/Screenshot_DouYin.png-------------------------')
    # print(image_to_string('TestRes/Screenshot_DouYin.png', lang='chi_sim'))   #True
    # print(aiService.img_contain_text('TestRes/Screenshot_DouYin.png', '儿童'))   #True
    print(aiService.img_contain_text_jieba('TestRes/Screenshot_DouYin.png', '为呵护未成年人健康成长,抖音推出'))     #True
    print(aiService.img_contain_text_jieba('TestRes/Screenshot_DouYin.png', '为呵护未成年人健康成长,抖音推出XXXX'))     #True

    # print("文字识别有问题，还很慢")
    # print(aiService.img_contain_text_click_pos('打开的编辑器', 'TestRes/AAA.png', True, 1, isRemoveImg=False, isShowLog=True))   #False