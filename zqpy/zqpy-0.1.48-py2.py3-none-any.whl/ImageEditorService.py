from PIL import Image, ImageDraw, ImageFont
import time, re

import numpy as np
import cv2
import os

class ImageEditorServiceClass():
    def ImageDrawText(self, text, sourceImg, targetImg, fontSize=28, fontPath=None, color='#000000', textPosTuple=None, textPosAnchor=None, textPosAnchorOff=None, sizeTuple=None):
        '''
        textPosAnchor + textPosAnchorOff适用于添加封面文字, textPosTuple适用于普通文字
        textPos 坐标在左上角开始,不填默认最中间
        textPosAnchor 坐标锚点，默认最中间 0/默认 中，1 左，2 上，3 右， 4 下
        textPosAnchorOff 偏移
        '''
        # 设置字体样式
        font = ImageFont.truetype(font=fontPath or 'C:/Windows/Fonts/simsun.ttc', size=fontSize)

        # 打开图片
        image = Image.open(sourceImg)
        draw = ImageDraw.Draw(image)
        width, height = image.size

        pos = (0,0)
        if textPosTuple:
            pos = textPosTuple
        else:
            if not textPosAnchor or textPosAnchor == 0:
                pos = ((width-fontSize*len(text))/2, (height-fontSize)/2)
            elif not textPosAnchor or textPosAnchor == 1:
                pos = (0, (height-fontSize)/2)
            elif not textPosAnchor or textPosAnchor == 2:
                pos = ((width-fontSize*len(text))/2, 0)
            elif not textPosAnchor or textPosAnchor == 3:
                pos = (width-fontSize*len(text), (height-fontSize)/2)
            elif not textPosAnchor or textPosAnchor == 4:
                pos = ((width-fontSize*len(text))/2, height-fontSize)
            if textPosAnchorOff:
                pos = (pos[0]+textPosAnchorOff[0], pos[1]+textPosAnchorOff[1])

        draw.text(pos, '%s' % text, color, font)
        # 生成图片
        # image.save(targetImg, 'png')
        image.save(targetImg)

        # 压缩图片
        if sizeTuple:
            sImg = Image.open(targetImg)
            # resize 是裁剪， thumbnail 不会裁剪，是等比缩放
            if sImg.size[0] < sizeTuple[0] and sImg.size[1] < sizeTuple[1]:
                dImg = sImg.resize(sizeTuple, Image.ANTIALIAS)
                dImg.save(targetImg)
            else:
                sImg.thumbnail(sizeTuple, Image.ANTIALIAS)
                sImg.save(targetImg)

    #切图
    def ImageCut(self, imgPath, saveDir, saveName, hCutNum, vCutNum=1):
        image = Image.open(imgPath)
        width, height = image.size
        item_width = int(width / hCutNum)
        item_height = int(height / vCutNum)
        box_list = []    
        # (left, upper, right, lower)
        if vCutNum and vCutNum != 1 :
            for j in range(vCutNum):
                for i in range(hCutNum):
                    box = (item_width * i, item_height * j, item_width * (i + 1), item_height * (j + 1))
                    box_list.append(box)
        else:
            for i in range(hCutNum):
                box = (i*item_width,0,(i+1)*item_width,height)
                box_list.append(box)

                
        image_list = [image.crop(box) for box in box_list]    
        #保存
        index = 1
        for image in image_list:
            image.save('%s%s'%(saveDir,fileName)+str(index) + suffixName)
            index += 1

    # 将原图转化为 灰度图，并将其像素值放入列表中，
    def ImageSuMiao(sourceImg, targetImg):
        # arr = np.asarray(Image.open(sourceImg))
        # L = np.asarray(Image.open(r'F:\python\Image-Freehand\tupian.jpg').convert('L')).astype('float')  # 取得图像灰度
        L = np.asarray(sourceImg.convert('L')).astype('float')


        depth = 10.  # (0-100)
        grad = np.gradient(L)  # 取图像灰度的梯度值
        grad_x, grad_y = grad  # 分别取横纵图像梯度值
        grad_x = grad_x * depth / 100.
        grad_y = grad_y * depth / 100.
        A = np.sqrt(grad_x ** 2 + grad_y ** 2 + 1.)
        uni_x = grad_x / A
        uni_y = grad_y / A
        uni_z = 1. / A

        el = np.pi / 2.2  # 光源的俯视角度，弧度值
        az = np.pi / 4  # 光源的方位角度，弧度值
        dx = np.cos(el) * np.cos(az)  # 光源对x轴的影响
        dy = np.cos(el) * np.sin(az)  # 光源对y轴的影响
        dz = np.sin(el)  # 光源对z轴的影响

        gd = 255 * (dx * uni_x + dy * uni_y + dz * uni_z)  # 光源归一化
        gd = gd.clip(0, 255)  # 避免数据越界，将生成的灰度值裁剪至0-255之间

        # gd = np.expand_dims(gd,axis =2)
        # gd = np.concatenate((gd,gd,gd),axis = -1)
        #
        # gd = np.hstack((arr,gd))
        im = Image.fromarray(gd.astype('uint8'))  # 重构图像
        im.save(targetImg)  # 保存图像
        return im

    def VideoSuMiao(video_path):
        vc = cv2.VideoCapture(video_path)
        c = 0
        if vc.isOpened():
            rval,frame = vc.read()
            height,width = frame.shape[0],frame.shape[1]
            print(height, width)
        else:
            rval = False
            height,width = 960,1200

        # jpg_list = [os.path.join('Pic_Directory/',i) for i in os.listdir('Pic_Directory') if i.endswith('.jpg')]

        fps = 24 # 视频帧率
        video_path1 = './text.mp4'
        video_writer = cv2.VideoWriter(video_path1,cv2.VideoWriter_fourcc(*'mp4v'),fps,(width*2,height))

        while rval:
            rval,frame = vc.read()# 读取视频帧
            img = convert_jpg(Image.fromarray(frame))
            frame_converted = np.array(img)

            # 转化为三通道
            image = np.expand_dims(frame_converted,axis = 2)
            result_arr = np.concatenate((image,image,image),axis = -1)
            result_arr = np.hstack((frame,result_arr))

            video_writer.write(result_arr)
            print('Sucessfully Conveted---------{}'.format(c))
            c = c + 1
            if c >= 60:
                break
        video_writer.release()
if __name__ == "__main__":
    import os
    ImageEditorService = ImageEditorServiceClass()
    # ImageEditorService.ImageDrawText('哈哈哈哈哈哈哈哈哈哈', './book.png', 'TestRes/1+Text.png', textPosAnchor=0)
    # os.system('start TestRes/1+Text.png')

    tartgetImg = r'book/cover/'
    dirPath = r'book/source/bg/'
    fileName = 'book'
    suffixName = '.png'
    desc = '当一个人真正投入爱情，那么她也就一定会变成笨蛋。因为爱情的悸动和占有欲，会焚烧人内心所有理智，令人变成蠢蛋。而这恰恰是恋爱最好的地方。若是你发现爱人在恋爱时一直都是表现的很理智很聪明，就要小心了。'
    spliteNum = 14
    maxNum = 98
    def cut_text(text,lenth):
        textArr = re.findall('.{'+str(lenth)+'}', text)
        textArr.append(text[(len(textArr)*lenth):])
        return textArr
    ImageEditorService.ImageDrawText('《%s》'%fileName, '%s%s%s'%(dirPath, fileName, suffixName), '%s%s%s'%(tartgetImg, fileName, suffixName), textPosAnchor=0, fontSize=20, color='#000000', sizeTuple=(1728,1024))
    
    ImageEditorService.ImageCut('%s%s%s'%(tartgetImg, fileName, suffixName), tartgetImg, fileName, 3, 2)
    # ImageEditorService.ImageCut('%s%s%s'%(tartgetImg, fileName, suffixName), tartgetImg, fileName, 3)
