from lxml import etree
import datetime
from datetime import timedelta
import requests
from . import db_pb2
from google.protobuf.json_format import MessageToDict
import os
from . import head
from .pare_xml import parse_xml_folder
import time


# 保存弹幕文件，最后合并文件，防止反爬导致全部崩溃
def save_xml(name, elem_list, oid):
    tree = etree.Element("i")
    chatterer = etree.SubElement(tree, "chatserver")
    chatterer.text = 'chat.bilibili.com'
    chatid = etree.SubElement(tree, 'chatid')
    chatid.text = str(oid)
    mission = etree.SubElement(tree, 'mission')
    mission.text = '0'
    maxlimit = etree.SubElement(tree, 'maxlimit')
    maxlimit.text = str(len(elem_list))
    real_name = etree.SubElement(tree, 'real_name')
    real_name.text = '0'
    source = etree.SubElement(tree, 'source')
    source.text = '0'
    for elem in elem_list:
        try:
            progress = elem['progress'] / 1000
            mode = elem['mode']
            fontsize = elem['fontsize']
            color = elem['color']
            ctime = elem['ctime']
            midHash = elem['midHash']
            row_id = elem['id']
            text = '{},{},{},{},{},{},{},{}'.format(progress, mode, fontsize, color, ctime, '0',
                                                    midHash, row_id)
            d = etree.SubElement(tree, 'd', p=text)
            d.text = elem['content']
        except KeyError:
            pass
    root = etree.ElementTree(tree)
    root.write('./%d/%s.xml' % (oid, name), pretty_print=True, xml_declaration=True, encoding="utf-8")


def gen_dates(b_date, days):
    day = timedelta(days=1)
    for i in range(days):
        yield b_date + day * i


def before_remove(data_list, msg):
    if msg in data_list:
        i = data_list.index(msg)
        if i != 0:
            if i == 1:
                data_list.pop(0)
                return data_list
            else:
                del data_list[0:i]
                return data_list
        return data_list
    return data_list


def after_remove(data_list, msg):
    if msg in data_list:
        i = data_list.index(msg)
        if i != len(data_list) - 1:
            if i == len(data_list) - 2:
                data_list.pop(len(data_list) - 1)
                return data_list
            else:
                del data_list[i + 1:len(data_list)]
                return data_list
        return data_list
    return data_list


def get_date_list(start_date, end_date):
    global start
    if start_date is not None:
        start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    if end_date is None:
        end = datetime.datetime.now()
    else:
        end = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    data = []
    for d in gen_dates(start, ((end - start).days + 1)):
        data.append(d.strftime("%Y-%m-%d"))
    return data


# 获取指定日期内的所有月份，包含指定日期月份
def get_month_list(start_date, end_date):
    dates = get_date_list(start_date, end_date)
    months = []
    for i in dates:
        if i[:7] not in months:
            months.append(i[:7])
    return months


def get_date_range(oid: int, month_range, start_day, end_day, second, proxy=None):
    for month in month_range:
        url = 'https://api.bilibili.com/x/v2/dm/history/index?type=1&oid={}&month={}'.format(oid, month)
        date_list = requests.get(url=url, proxies=proxy, headers=head.headers, cookies=head.cookie()).json()
        date_range = date_list['data']
        time.sleep(second)
        date_range = before_remove(date_range, start_day)
        date_range = after_remove(date_range, end_day)
        get_danmaku(oid, date_range, second, proxy)


def get_danmaku(oid: int, date_range, second, proxy=None):
    for date in date_range:
        url = 'https://api.bilibili.com/x/v2/dm/web/history/seg.so?type=1&oid={}&date={}'.format(oid, date)
        response = requests.get(url=url, headers=head.headers, proxies=proxy, cookies=head.cookie()).content
        danmaku_seg = db_pb2.DmSegMobileReply()
        danmaku_seg.ParseFromString(response)
        elems = MessageToDict(danmaku_seg)
        if 'elems' in elems:
            elem_list = elems['elems']
            save_xml(date, elem_list, oid)
        print('{}的弹幕获取成功'.format(date))
        time.sleep(second)


def main(start_day, end_day, oid, second, proxy=None):
    if not os.path.exists(str(oid)):
        os.mkdir(str(oid))
    month_range = get_month_list(start_day, end_day)
    print('开始获取弹幕')
    try:
        get_date_range(oid, month_range, start_day, end_day, second, proxy)
        print('开始合并弹幕')
        parse_xml_folder(str(oid))
        print('弹幕下载成功')
    except Exception as wrong:
        print('出现错误，很大概率被B站反爬，请查看erosion.log文件')
        with open('erosion.log', 'w', encoding='utf-8') as f:
            f.write(str(wrong))
        parse_xml_folder(str(oid))
