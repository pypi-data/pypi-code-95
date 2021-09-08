import requests
import json
from os.path import join, dirname
import base64
from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple
'''
kcode业务模块
'''

RESULTS = {
    'expression': {
        '': 'N/A',
        'none': '不笑',
        'smile': '微笑',
        'laugh': '大笑'
    },
    'gender': {
        'male': '男',
        'female': '女'
    },
    'emotion': {
        '': 'N/A',
        'angry': '愤怒',
        'disgust': '厌恶',
        'fear': '恐惧',
        'happy': '高兴',
        'sad': '伤心',
        'surprise': '惊讶',
        'neutral': '无表情',
        'pouty': '撅嘴',
        'grimace': '扮鬼脸'
    },
    'face_shape': {
        'square': '方形',
        'triangle': '锥形',
        'oval': '椭圆形',
        'heart': '心形',
        'round': '圆形'
    }
}
AK = '2oLVPhoqoyqol0b65TO0iqsS'
SK = 'vA1q5h9jbxQG3QEIm7wWgdFoCSFQTkoE'


#获取百度vipfacedemo的token
def get_token():
    token = f'token?grant_type=client_credentials&client_id={AK}&client_secret={SK}'
    host = f'https://aip.baidubce.com/oauth/2.0/{token}'
    headers = {'Content-Type': 'application/json; charset=UTF-8'}
    content = requests.get(host, headers=headers)
    if (content):
        return json.loads(content.text).get('access_token')
    else:
        return None


def get_datas(path: str):
    '''
    根据输入的图片路径，获取图片后转为BASE64字符串编码。按照百度人脸
    参数path： 要打分的图片路径
    返回值：以字典形式组织的面部相关信息

    '''
    # filename = join(dirname(__file__), path)
    filename = path
    with open(filename, 'rb') as f:
        datas = base64.b64encode(f.read())

    request_url = "https://aip.baidubce.com/rest/2.0/face/v3/detect"
    # face_field:
    # age, 年龄
    # beauty, 打分（满分100）
    # expression, 表情 type: none:不笑；smile:微笑；laugh:大笑
    # face_shape, 脸型 type: square: 正方形 triangle:三角形 oval: 椭圆 heart: 心形 round: 圆形
    # gender, 性别 type: male:男性 female:女性
    # glasses,  是否带眼镜 type: none:无眼镜，common:普通眼镜，sun:墨镜
    # landmark, 4个关键点位置，左眼中心、右眼中心、鼻尖、嘴中心。
    # landmark72, 72个特征点位置
    # landmark150,150个特征点位置
    # race, 种族，文档无进一步说明
    # quality, 人脸质量信息
    # eye_status, 双眼状态（睁开/闭合） left_eye 左眼状态 越接近0闭合的可能性越大 right_eye	右眼状态 越接近0闭合的可能性越大
    # emotion, 情绪 type: angry:愤怒 disgust:厌恶 fear:恐惧 happy:高兴 sad:伤心 surprise:惊讶 neutral:无表情 pouty: 撅嘴 grimace:鬼脸
    # face_type 真实人脸/卡通人脸
    params = {
        "image": {datas},
        "image_type":
        "BASE64",
        "face_field":
        "age,beauty,expression,face_shape,gender,landmark,landmark150,emotion"
    }

    access_token = get_token()
    request_url = request_url + "?access_token=" + access_token
    headers = {'Content-Type': 'application/json'}
    resp = requests.post(request_url, headers=headers, data=params)

    face = json.loads(resp.text)

    result = {}
    # 如果服务器正确识别了图片，则从服务器的响应信息中提取有价值的内容
    if face.get('error_code') == 0:
        result['filename'] = filename
        datas = face.get('result')
        result['face_num'] = datas.get('face_num')
        datas = datas.get('face_list')[0]
        # 脸部区域
        result['location'] = dict(datas.get('location'))
        result['age'] = datas.get('age')
        result['beauty'] = datas.get('beauty')
        result['face_shape'] = datas.get('face_shape').get('type')
        result['gender'] = datas.get('gender').get('type')
        ls = datas.get('landmark')
        for i in range(len(ls)):
            x, y = ls[i]['x'], ls[i]['y']
            ls.pop(i)
            ls.insert(i, (x, y))
        # 左眼中心，右眼中心，鼻尖中心，嘴中心
        result['landmark'] = ls
        ls = datas.get('landmark72')
        for i in range(len(ls)):
            x, y = ls[i]['x'], ls[i]['y']
            ls.pop(i)
            ls.insert(i, (x, y))
        # 面部72特征点
        result['landmark72'] = ls
        vs = []
        for v in datas['landmark150'].values():
            vs.append((v['x'], v['y']))
        # 面部150特征点
        result['landmark150'] = vs
        result['emotion'] = datas.get('emotion')['type']
        result['expression'] = datas.get('expression')['type']
    return result


def showimg(filename: str) -> None:
    '''
    使用PIL显示图像
    显示时使用的是系统默认的看图程序
    '''
    pic = Image.open(filename)
    #w,h = pic.size
    pic.show()


def drawrect(filename: str,
             left,
             top,
             width,
             height,
             rotation=0,
             color='green') -> Image:
    '''
    在指定图像上，根据指定位置、大小和角度，绘制一个绿色的矩形，标识人脸所在区域
    '''
    pic = Image.open(filename)
    w, h = pic.size

    temp = Image.new(mode='RGBA', size=(w, h), color=0)
    pen = ImageDraw.Draw(temp)
    # xy(left,top, right, bottom)
    pen.rectangle(xy=(left, top, left + width, top + height),
                  fill=None,
                  outline=color,
                  width=2)
    # 按逆时针旋转角度(要将百度得到的角度取反)
    # center指定旋转中心位置。如果不指定默认为图像的中心，即以(w/2,h/2)为中心旋转
    # 现在的旋转中心是脸部区域框的左上角，即(left,top)
    rect = temp.rotate(-rotation, center=(left, top))
    #如果需要保持修改后的内容，为了不破坏原始图像，可以将原始图像复制一份
    #在复制品result上进行修改后保存
    #如果仅修改不保存，可以在原图上直接进行，程序退出后所有修改都消失
    #result = pic.copy()
    result = pic
    #paste第三个参数的说明：
    #如果执行两个参数的paste命令：result.paste(rect, (0, 0))，虽然rect是一个RGBA透明底色的图像，
    #但执行粘贴时，透明像素将被粘贴为实心像素，因此透明部分将变为黑色（某些操作系统上的白色）粘贴进去。
    #大多数时候，这不是你想要的，而是需要透明的像素出现。
    #为了达到这个目的，需要把第三个参数传递给paste()函数。即result.paste(rect, (0, 0),遮罩mask)
    #遮罩是一个图像(Image)对象，其中的alpha值是重要的，但其绿色，红色和蓝色值将被忽略。
    #如果给出遮罩，则paste()仅更新由mask覆盖的区域。
    #即如果使用RGBA图像作为遮罩，paste仅粘贴RGBA图像不透明部分，但不粘贴透明背景。
    result.paste(rect, (0, 0), rect)
    return result


def face_detect(datas, color='green', tag=None) -> Image:
    if len(datas) > 0:
        filename = datas['filename']
        location = datas['location']
        left = location['left']
        top = location['top']
        width = location['width']
        height = location['height']
        rotation = location['rotation']
        result = drawrect(filename, left, top, width, height, rotation, color)
        if tag == 'key':
            ww, hh = result.size
            r = min(ww, hh) // 200
            if r < 1: r = 1
            pen = ImageDraw.Draw(result)
            for x, y in datas['landmark']:
                pen.ellipse([x - r, y - r, x + r, y + r], fill=color)
        elif tag == 'all':
            ww, hh = result.size
            r = min(ww, hh) // 300
            if r < 1: r = 1
            pen = ImageDraw.Draw(result)
            for x, y in datas['landmark150']:
                pen.ellipse([x - r, y - r, x + r, y + r], fill=color)
        return result
    else:
        raise RuntimeError


def drawmarks(filename: str, points: List[Tuple], point=False) -> Image:
    '''
    将人脸识别返回的人脸上特征点在图像上绘制出
    用point函数绘制的点较小，在图像上不容易看到，如果绘制的点不多
    可以采用ellipse函数绘制实心圆来表示点。
    '''
    pic = Image.open(filename)
    pen = ImageDraw.Draw(pic)
    if point:
        pen.point(points, fill='green')
    else:
        for x, y in points:
            pen.ellipse([x - 1, y - 1, x + 1, y + 1], fill='green')
    return pic


def get_score(datas: List, result=None, color='green') -> Image:
    filename = datas['filename']
    pic = Image.open(filename)
    w, h = pic.size
    pen = ImageDraw.Draw(pic)
    #size = min(w, h) // 20
    i = int(h * 0.1)
    j = int(w * 0.1)
    size = min(60, (int(h * 0.8 / 6)) // 10 * 10)
    fnt = ImageFont.truetype('msyh.ttc', size=size)

    info = []
    info.append({'年纪': str(datas.get('age', 'N/A'))})
    info.append({'性别': RESULTS.get('gender').get(datas.get('gender'))})
    info.append({'颜值': str(datas.get('beauty', 'N/A'))})
    info.append({'脸型': RESULTS.get('face_shape').get(datas.get('face_shape'))})
    info.append({'表情': RESULTS.get('expression').get(datas.get('expression'))})
    info.append({'情绪': RESULTS.get('emotion').get(datas.get('emotion'))})

    for x in range(6):
        for k, v in info[x].items():
            pen.text((i, j), k + ":" + v, font=fnt, fill=color)
        j += size + 5
    result = pic
    result.show()