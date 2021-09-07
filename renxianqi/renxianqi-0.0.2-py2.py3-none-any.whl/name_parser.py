# -*- coding: utf-8 -*-
# @Time : 2021/8/29 2:40 下午
# @Author : LeiXueWei
# @CDSN: 雷学委
# @XueWeiTag: CodingDemo
# @File : name_parser.py
# @Project : hello


def debug(data):
    print(str(data))


def parse_names_text(raw_data):
    if not raw_data:
        return None
    items = raw_data.split('\n')
    trim_items = set(x.strip() if x.strip() else '' for x in items)
    # return str(trim_items)
    debug("len=%s" % len(trim_items))
    debug("trim_items=%s" % str(trim_items))
    breakdowns = set()
    breakdown_tokens = [';', '；', ',', '，', '、', '丶']
    for x in trim_items:
        has_token = False
        for token in breakdown_tokens:
            if token in x:
                has_token = True
                print("token is %s" % token)
                names = x.split(token)
                print("names is %s" % names)
                breakdowns = breakdowns | set(names)
        if not has_token:
            breakdowns.add(x)
    fmt_names = list()
    for x in breakdowns:
        if x.strip() == "":
            continue
        fmt_names.append(x)
    fmt_names.sort()
    return fmt_names


if __name__ == '__main__':
    d = 'Dream丶Killer、宝山的博客、小生凡一'
    print(d.split('、'))
    print(parse_names_text(d))
