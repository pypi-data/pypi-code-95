from qdata.baidu_index import (
    get_feed_index,
    get_news_index,
    get_search_index,
    get_live_search_index
)
import time


keywords_list = [['张艺兴', '汪峰'], ['百度']]
cookies = """BIDUPSID=A1687674F5C670CF4366653E6F345CA5; PSTM=1507613496; BD_UPN=12314753; __yjs_duid=1_6e5258f2dd8651d6b8a78296fccbeb7c1620185686013; BDUSS=w5MTNla0VmTkJCdlRxMnM3bEVEelpjc2ZRZkZ-TzBhTklPWWZnVXd5Y0tnaXhoRVFBQUFBJCQAAAAAAAAAAAEAAACHxsCatMvJ-rTL4rkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAr1BGEK9QRhTG; BDUSS_BFESS=w5MTNla0VmTkJCdlRxMnM3bEVEelpjc2ZRZkZ-TzBhTklPWWZnVXd5Y0tnaXhoRVFBQUFBJCQAAAAAAAAAAAEAAACHxsCatMvJ-rTL4rkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAr1BGEK9QRhTG; BAIDUID=E8BAAE642C79E8BB01836262C5BD81A1:FG=1; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; MCITY=-%3A; bdindexid=kf0so0lfd9o59mohqs1h09vr90; indexpro=htve70jb0hrfvstceem3kt9mg2; BD_HOME=1; H_PS_PSSID=34653_34439_34655_34004_34599_34585_34092_34106_26350_34627_34419_34555; sug=3; sugstore=0; ORIGIN=0; bdime=0; BA_HECTOR=a1210ka00l81a105ud1gk3qhu0q;"""


def test_get_feed_index():
    """获取资讯指数"""
    for index in get_feed_index(
        keywords_list=keywords_list,
        start_date='2018-01-01',
        end_date='2019-05-01',
        cookies=cookies
    ):
        print(index)


def test_get_news_index():
    """获取媒体指数"""
    for index in get_news_index(
        keywords_list=keywords_list,
        start_date='2018-01-01',
        end_date='2019-05-01',
        cookies=cookies
    ):
        print(index)


def test_get_search_index():
    """获取搜索指数"""
    for index in get_search_index(
        keywords_list=keywords_list,
        start_date='2018-01-01',
        end_date='2019-05-01',
        cookies=cookies
    ):
        print(index)


def test_get_live_search_index():
    """获取搜索指数实时数据"""
    for index in get_live_search_index(
        keywords_list=keywords_list,
        cookies=cookies,
        area=0
    ):
        print(index)

    for index in get_live_search_index(
        keywords_list=keywords_list,
        cookies=cookies,
        area=911
    ):
        print(index)


if __name__ == "__main__":
    test_get_feed_index()
    time.sleep(2)
    test_get_news_index()
    time.sleep(2)
    test_get_search_index()
    time.sleep(2)
    test_get_live_search_index()
