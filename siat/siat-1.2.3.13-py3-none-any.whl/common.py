# -*- coding: utf-8 -*-
"""
本模块功能：SIAT公共基础函数
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2019年7月16日
最新修订日期：2020年3月28日
作者：王德宏 (WANG Dehong, Peter)
作者单位：北京外国语大学国际商学院
作者邮件：wdehong2000@163.com
版权所有：王德宏
用途限制：仅限研究与教学使用，不可商用！商用需要额外授权。
特别声明：作者不对使用本工具进行证券投资导致的任何损益负责！
"""

#==============================================================================
#关闭所有警告
import warnings; warnings.filterwarnings('ignore')
#==============================================================================
#==============================================================================
#==============================================================================
def ticker_check(ticker, source="yahoo"):
    """
    检查证券代码，对于大陆证券代码、香港证券代码和东京证券代码进行修正。
    输入：证券代码ticker，数据来源source。
    上交所证券代码后缀为.SS或.SH或.ss或.sh，深交所证券代码为.SZ或.sz
    港交所证券代码后缀为.HK，截取数字代码后4位
    东京证交所证券代码后缀为.T，截取数字代码后4位
    source：yahoo或tushare
    返回：字母全部转为大写。若是大陆证券返回True否则返回False。
    若选择yahoo数据源，上交所证券代码转为.SS；
    若选择tushare数据源，上交所证券代码转为.SH
    """
    #测试用，完了需要注释掉
    #ticker="600519.sh"
    #source="yahoo"
    
    #将字母转为大写
    ticker1=ticker.upper()
    #截取字符串最后2/3位
    suffix2=ticker1[-2:]
    suffix3=ticker1[-3:]
    
    #判断是否大陆证券
    if suffix3 in ['.SH', '.SS', '.SZ']:
        prc=True
    else: prc=False

    #根据数据源的格式修正大陆证券代码
    if (source == "yahoo") and (suffix3 in ['.SH']):
        ticker1=ticker1.replace(suffix3, '.SS')        
    if (source == "tushare") and (suffix3 in ['.SS']):
        ticker1=ticker1.replace(suffix3, '.SH')  

    #若为港交所证券代码，进行预防性修正，截取数字代码后4位，加上后缀共7位
    if suffix3 in ['.HK']:
        ticker1=ticker1[-7:]     

    #若为东交所证券代码，进行预防性修正，截取数字代码后4位，加上后缀共6位
    if suffix2 in ['.T']:
        ticker1=ticker1[-6:]  
    
    #返回：是否大陆证券，基于数据源/交易所格式修正后的证券代码
    return prc, ticker1        

#测试各种情形
if __name__=='__main__':
    prc, ticker=ticker_check("600519.sh","yahoo")
    print(prc,ticker)
    print(ticker_check("600519.SH","yahoo"))    
    print(ticker_check("600519.ss","yahoo"))    
    print(ticker_check("600519.SH","tushare"))    
    print(ticker_check("600519.ss","tushare"))    
    print(ticker_check("000002.sz","tushare"))
    print(ticker_check("000002.sz","yahoo"))
    print(ticker_check("00700.Hk","yahoo"))
    print(ticker_check("99830.t","yahoo"))

#==============================================================================
def tickers_check(tickers, source="yahoo"):
    """
    检查证券代码列表，对于大陆证券代码、香港证券代码和东京证券代码进行修正。
    输入：证券代码列表tickers，数据来源source。
    上交所证券代码后缀为.SS或.SH或.ss或.sh，深交所证券代码为.SZ或.sz
    港交所证券代码后缀为.HK，截取数字代码后4位
    东京证交所证券代码后缀为.T，截取数字代码后4位
    source：yahoo或tushare
    返回：证券代码列表，字母全部转为大写。若是大陆证券返回True否则返回False。
    若选择yahoo数据源，上交所证券代码转为.SS；
    若选择tushare数据源，上交所证券代码转为.SH
    """
    #检查列表是否为空
    if tickers[0] is None:
        print("*** 错误#1(tickers_check)，空的证券代码列表:",tickers)
        return None         
    
    tickers_new=[]
    for t in tickers:
        _, t_new = ticker_check(t, source=source)
        tickers_new.append(t_new)
    
    #返回：基于数据源/交易所格式修正后的证券代码
    return tickers_new

#测试各种情形
if __name__=='__main__':
    tickers=tickers_check(["600519.sh","000002.sz"],"yahoo")
    print(tickers)
#==============================================================================
def check_period(fromdate, todate):
    """
    功能：根据开始/结束日期检查日期与期间的合理性
    输入参数：
    fromdate：开始日期。格式：YYYY-MM-DD
    enddate：开始日期。格式：YYYY-MM-DD
    输出参数：
    validity：期间合理性。True-合理，False-不合理
    start：开始日期。格式：datetime类型
    end：结束日期。格式：datetime类型
    """
    import pandas as pd
    
    #测试开始日期的合理性
    try:
        start=pd.to_datetime(fromdate)
    except:
        print("*** 错误#1(check_period)，无效的日期:",fromdate)
        return None, None, None         
    
    #测试结束日期的合理性
    try:
        end=pd.to_datetime(todate)
    except:
        print("*** 错误#2(check_period)，无效的日期:",todate)
        return None, None, None          
    
    #测试日期期间的合理性
    if start > end:
        print("*** 错误#3(check_period)，无效的日期期间: 从",fromdate,"至",todate)
        return None, None, None     

    return True, start, end

if __name__ =="__main__":
    check_period('2020-1-1','2020-2-4')
    check_period('2020-1-1','2010-2-4')

#==============================================================================
def date_adjust(basedate, adjust=0):
    """
    功能：将给定日期向前或向后调整特定的天数
    输入：基础日期，需要调整的天数。
    basedate: 基础日期。
    adjust：需要调整的天数，负数表示向前调整，正数表示向后调整。
    输出：调整后的日期。
    """
    #检查基础日期的合理性
    import pandas as pd    
    try:
        bd=pd.to_datetime(basedate)
    except:
        print("*** 错误#1(date_adjust)，无效的日期:",basedate)
        return None

    #调整日期
    from datetime import timedelta
    nd = bd+timedelta(days=adjust)    
    
    #重新提取日期
    newdate=nd.date()   
    return str(newdate)
 
if __name__ =="__main__":
    basedate='2020-3-17' 
    adjust=-365    
    newdate = date_adjust(basedate, adjust)
    print(newdate)    

#==============================================================================
def decompose_portfolio(portfolio):
    """
    功能：将一个投资组合字典分解为股票代码列表和份额列表
    投资组合的结构：{'Market':('US','^GSPC'),'AAPL':0.5,'MSFT':0.3,'IBM':0.2}
    输入：投资组合
    输出：市场，市场指数，股票代码列表和份额列表
    """
    #仅为测试用
    #portfolio={'Market':('US','^GSPC'),'EDU':0.4,'TAL':0.3,'TEDU':0.2}
    
    #从字典中提取信息
    keylist=list(portfolio.keys())
    scope=portfolio[keylist[0]][0]
    mktidx=portfolio[keylist[0]][1]
    
    slist=[]
    plist=[]
    for key,value in portfolio.items():
        slist=slist+[key]
        plist=plist+[value]
    stocklist=slist[1:]    
    portionlist=plist[1:]

    return scope,mktidx,stocklist,portionlist    

if __name__=='__main__':
    portfolio1={'Market':('US','^GSPC'),'EDU':0.4,'TAL':0.3,'TEDU':0.2}
    scope,mktidx,tickerlist,sharelist=decompose_portfolio(portfolio1)
    _,_,tickerlist,sharelist=decompose_portfolio(portfolio1)


#==============================================================================
def calc_monthly_date_range(start,end):
    """
    功能：返回两个日期之间各个月份的开始和结束日期
    输入：开始/结束日期
    输出：两个日期之间各个月份的开始和结束日期元组对列表
    """
    #测试用
    #start='2019-01-05'
    #end='2019-06-25'    
    
    import pandas as pd
    startdate=pd.to_datetime(start)
    enddate=pd.to_datetime(end)

    mdlist=[]
    #当月的结束日期
    syear=startdate.year
    smonth=startdate.month
    import calendar
    sdays=calendar.monthrange(syear,smonth)[1]
    from datetime import date
    slastday=pd.to_datetime(date(syear,smonth,sdays))

    if slastday > enddate: slastday=enddate
    
    #加入第一月的开始和结束日期
    import bisect
    bisect.insort(mdlist,(startdate,slastday))
    
    #加入结束月的开始和结束日期
    eyear=enddate.year
    emonth=enddate.month
    efirstday=pd.to_datetime(date(eyear,emonth,1))   
    if startdate < efirstday:
        bisect.insort(mdlist,(efirstday,enddate))
    
    #加入期间内各个月份的开始和结束日期
    from dateutil.relativedelta import relativedelta
    next=startdate+relativedelta(months=+1)
    while next < efirstday:
        nyear=next.year
        nmonth=next.month
        nextstart=pd.to_datetime(date(nyear,nmonth,1))
        ndays=calendar.monthrange(nyear,nmonth)[1]
        nextend=pd.to_datetime(date(nyear,nmonth,ndays))
        bisect.insort(mdlist,(nextstart,nextend))
        next=next+relativedelta(months=+1)
    
    return mdlist

if __name__=='__main__':
    mdp1=calc_monthly_date_range('2019-01-01','2019-06-30')
    mdp2=calc_monthly_date_range('2000-01-01','2000-06-30')   #闰年
    mdp3=calc_monthly_date_range('2018-09-01','2019-03-31')   #跨年
    
    for i in range(0,len(mdp1)):
        start=mdp1[i][0]
        end=mdp1[i][1]
        print("start =",start,"end =",end)


#==============================================================================
def calc_yearly_date_range(start,end):
    """
    功能：返回两个日期之间各个年度的开始和结束日期
    输入：开始/结束日期
    输出：两个日期之间各个年度的开始和结束日期元组对列表
    """
    #测试用
    #start='2013-01-01'
    #end='2019-08-08'    
    
    import pandas as pd
    startdate=pd.to_datetime(start)
    enddate=pd.to_datetime(end)

    mdlist=[]
    #当年的结束日期
    syear=startdate.year
    from datetime import date
    slastday=pd.to_datetime(date(syear,12,31))

    if slastday > enddate: slastday=enddate
    
    #加入第一年的开始和结束日期
    import bisect
    bisect.insort(mdlist,(startdate,slastday))
    
    #加入结束年的开始和结束日期
    eyear=enddate.year
    efirstday=pd.to_datetime(date(eyear,1,1))   
    if startdate < efirstday:
        bisect.insort(mdlist,(efirstday,enddate))
    
    #加入期间内各个年份的开始和结束日期
    from dateutil.relativedelta import relativedelta
    next=startdate+relativedelta(years=+1)
    while next < efirstday:
        nyear=next.year
        nextstart=pd.to_datetime(date(nyear,1,1))
        nextend=pd.to_datetime(date(nyear,12,31))
        bisect.insort(mdlist,(nextstart,nextend))
        next=next+relativedelta(years=+1)
    
    return mdlist

if __name__=='__main__':
    mdp1=calc_yearly_date_range('2013-01-05','2019-06-30')
    mdp2=calc_yearly_date_range('2000-01-01','2019-06-30')   #闰年
    mdp3=calc_yearly_date_range('2018-09-01','2019-03-31')   #跨年
    
    for i in range(0,len(mdp1)):
        start=mdp1[i][0]
        end=mdp1[i][1]
        print("start =",start,"end =",end)

#==============================================================================

def sample_selection(df,start,end):
    """
    功能：根据日期范围start/end选择数据集df的子样本，并返回子样本
    """
    flag,start2,end2=check_period(start,end)
    df_sub=df[df.index >= start2]
    df_sub=df_sub[df_sub.index <= end2]
    
    return df_sub
    
if __name__=='__main__':
    portfolio={'Market':('US','^GSPC'),'AAPL':1.0}
    market,mktidx,tickerlist,sharelist=decompose_portfolio(portfolio)
    start='2020-1-1'; end='2020-3-31'
    pfdf=get_portfolio_prices(tickerlist,sharelist,start,end)
    start2='2020-1-10'; end2='2020-3-18'
    df_sub=sample_selection(pfdf,start2,end2)    
    
#==============================================================================
def init_ts():
    """
    功能：初始化tushare pro，登录后才能下载数据
    """
    import tushare as ts
    #设置token
    token='49f134b05e668d288be43264639ac77821ab9938ff40d6013c0ed24f'
    pro=ts.pro_api(token)
    
    return pro
#==============================================================================
def convert_date_ts(y4m2d2):
    """
    功能：日期格式转换，YYYY-MM-DD-->YYYYMMDD，用于tushare
    输入：日期，格式：YYYY-MM-DD
    输出：日期，格式：YYYYMMDD
    """
    import pandas as pd
    try: date1=pd.to_datetime(y4m2d2)
    except:
        print("Error #1(convert_date_tushare): invalid date:",y4m2d2)
        return None 
    else:
        date2=date1.strftime('%Y')+date1.strftime('%m')+date1.strftime('%d')
    return date2

if __name__ == '__main__':
    convert_date_ts("2019/11/1")
#==============================================================================
def gen_yearlist(start_year,end_year):
    """
    功能：产生从start_year到end_year的一个年度列表
    输入参数：
    start_year: 开始年份，字符串
    end_year：截止年份
    输出参数：
    年份字符串列表    
    """
    #仅为测试使用，完成后应注释掉
    #start_year='2010'
    #end_year='2019'    
    
    import numpy as np
    start=int(start_year)
    end=int(end_year)
    num=end-start+1    
    ylist=np.linspace(start,end,num=num,endpoint=True)
    
    yearlist=[]
    for y in ylist:
        yy='%d' %y
        yearlist=yearlist+[yy]
    #print(yearlist)
    
    return yearlist

if __name__=='__main__':
    yearlist=gen_yearlist('2013','2019')
#==============================================================================
def print_progress_bar(current,startnum,endnum):
    """
    功能：打印进度数值，每个10%打印一次，不换行
    """
    for i in [9,8,7,6,5,4,3,2,1]:
        if current == int((endnum - startnum)/10*i)+1: 
            print(str(i)+'0%',end=' '); break
        elif current == int((endnum - startnum)/100*i)+1: 
            print(str(i)+'%',end=' '); break
    if current == 2: print('0%',end=' ')

if __name__ =="__main__":
    startnum=2
    endnum=999
    L=range(2,999)
    for c in L: print_progress_bar(c,startnum,endnum)

#==============================================================================
def save_to_excel(df,filedir,excelfile,sheetname="Sheet1"):
    """
    函数功能：将df保存到Excel文件。
    如果目录不存在提示出错；如果Excel文件不存在则创建之文件并保存到指定的sheet；
    如果Excel文件存在但sheet不存在则增加sheet并保存df内容，原有sheet内容不变；
    如果Excel文件和sheet都存在则追加df内容到已有sheet的末尾
    输入参数：
    df: 数据框
    filedir: 目录
    excelfile: Excel文件名，不带目录，后缀为.xls或.xlsx
    sheetname：Excel文件中的sheet名
    输出：
    保存df到Excel文件
    无返回数据
    
    注意：如果df中含有以文本表示的数字，写入到Excel会被自动转换为数字类型保存。
    从Excel中读出后为数字类型，因此将会与df的类型不一致
    """

    #检查目录是否存在
    import os
    try:
        os.chdir(filedir)
    except:
        print("Error #1(save_to_excel): folder does not exist")        
        print("Information:",filedir)  
        return
                
    #取得df字段列表
    dflist=df.columns
    #合成完整的带目录的文件名
    filename=filedir+'/'+excelfile
    
    import pandas as pd
    try:
        file1=pd.ExcelFile(excelfile)
    except:
        #不存在excelfile文件，直接写入
        df.to_excel(filename,sheet_name=sheetname, \
                       header=True,encoding='utf-8')
        print("***Results saved in",filename,"@ sheet",sheetname)
        return
    else:
        #已存在excelfile文件，先将所有sheet的内容读出到dict中        
        dict=pd.read_excel(file1, None)
    file1.close()
    
    #获得所有sheet名字
    sheetlist=list(dict.keys())
    
    #检查新的sheet名字是否已存在
    try:
        pos=sheetlist.index(sheetname)
    except:
        #不存在重复
        dup=False
    else:
        #存在重复，合并内容
        dup=True
        #合并之前可能需要对df中以字符串表示的数字字段进行强制类型转换.astype('int')
        df1=dict[sheetlist[pos]][dflist]
        dfnew=pd.concat([df1,df],axis=0,ignore_index=True)        
        dict[sheetlist[pos]]=dfnew
    
    #将原有内容写回excelfile    
    result=pd.ExcelWriter(filename)
    for s in sheetlist:
        df1=dict[s][dflist]
        df1.to_excel(result,s,header=True,index=True,encoding='utf-8')
    #写入新内容
    if not dup: #sheetname未重复
        df.to_excel(result,sheetname,header=True,index=True,encoding='utf-8')
    try:
        result.save()
        result.close()
    except:
        print("Error #2(save_to_excel): writing file permission denied")
        print("Information:",filename)  
        return
    print("***Results saved in",filename,"@ sheet",sheetname)
    return       
#==============================================================================
def set_df_period(df,df_min,df_max):
    """
    功能： 去掉df中日期范围以外的记录
    """
    df1=df[df.index >= df_min]
    df2=df1[df1.index <= df_max]
    return df2

if __name__=='__main__':
    import siat.security_prices as ssp
    df=ssp.get_price('AAPL','2020-1-1','2020-1-31')    
    df_min,df_max=get_df_period(df)    
    df2=set_df_period(df,df_min,df_max)

#==============================================================================
def sigstars(p_value):
    """
    功能：将p_value转换成显著性的星星
    """
    if p_value >= 0.1: 
        stars="   "
        return stars
    if 0.1 > p_value >= 0.05:
        stars="*  "
        return stars
    if 0.05 > p_value >= 0.01:
        stars="** "
        return stars
    if 0.01 > p_value:
        stars="***"
        return stars

#==============================================================================

def regparms(results):
    """
    功能：将sm.OLS回归结果生成数据框，包括变量名称、系数数值、t值、p值和显著性星星
    """
    import pandas as pd
    #取系数
    params=results.params
    df_params=pd.DataFrame(params)
    df_params.columns=['coef']
    
    #取t值
    tvalues=results.tvalues
    df_tvalues=pd.DataFrame(tvalues)
    df_tvalues.columns=['t_values']

    #取p值
    pvalues=results.pvalues
    df_pvalues=pd.DataFrame(pvalues)
    df_pvalues.columns=['p_values']            

    #生成星星
    df_pvalues['sig']=df_pvalues['p_values'].apply(lambda x:sigstars(x))
    
    #合成
    parms1=pd.merge(df_params,df_tvalues, \
                    how='inner',left_index=True,right_index=True)
    parms2=pd.merge(parms1,df_pvalues, \
                    how='inner',left_index=True,right_index=True)

    return parms2
#==============================================================================
if __name__=='__main__':
    txt='QDII-指数'

def strlen(txt):
    """
    功能：计算中英文混合字符串的实际长度
    """
    lenTxt = len(txt) 
    lenTxt_utf8 = len(txt.encode('utf-8')) 
    size = int((lenTxt_utf8 - lenTxt)/2 + lenTxt)    

    return size

#==============================================================================

def sort_pinyin(hanzi_list): 
    """
    功能：对列表中的中文字符串按照拼音升序排序
    """
    from pypinyin import lazy_pinyin       
    hanzi_list_pinyin=[]
    hanzi_list_pinyin_alias_dict={}
    
    for single_str in hanzi_list:
        py_r = lazy_pinyin(single_str)
        # print("整理下")
        single_str_py=''
        for py_list in py_r:
            single_str_py=single_str_py+py_list
        hanzi_list_pinyin.append(single_str_py)
        hanzi_list_pinyin_alias_dict[single_str_py]=single_str
    
    hanzi_list_pinyin.sort()
    sorted_hanzi_list=[]
    
    for single_str_py in hanzi_list_pinyin:
        sorted_hanzi_list.append(hanzi_list_pinyin_alias_dict[single_str_py])
    
    return sorted_hanzi_list


#==============================================================================
def get_start_date(end_date,pastyears=1):
    """
    输入参数：一个日期，年数
    输出参数：几年前的日期
    start_date, end_date是datetime类型
    """

    import pandas as pd
    try:
        end_date=pd.to_datetime(end_date)
    except:
        print("#Error(): invalid date,",end_date)
        return None
    
    from datetime import datetime,timedelta
    start_date=datetime(end_date.year-pastyears,end_date.month,end_date.day)
    start_date=start_date-timedelta(days=1)
    # 日期-1是为了保证计算收益率时得到足够的样本数量
    return start_date
    
#==============================================================================
def get_ip():
    """
    功能：获得本机计算机名和IP地址    
    """
    #内网地址
    import socket
    hostname = socket.gethostname()
    internal_ip = socket.gethostbyname(hostname)
    
    #公网地址

    return hostname,internal_ip

if __name__=='__main__':
    get_ip()
#==============================================================================
def check_date(adate):
    """
    功能：检查一个日期是否为有效日期
    输入参数：一个日期
    输出：合理日期为True，其他为False
    """
    #仅为测试使用，测试完毕需要注释掉
    #adate='2019-6-31'

    result=True
    import pandas as pd
    try:    
        bdate=pd.to_datetime(adate)
    except:
        print("Error #1(check_date): Date invalid")
        print("Variable(s):",adate)
        result=False
        
    return result

if __name__ =="__main__":
    print(check_date('2019-6-31'))


#==============================================================================
def check_start_end_dates(start,end):
    """
    功能：检查一个期间的开始/结束日期是否合理
    输入参数：开始和结束日期
    输出：合理为True，其他为False
    """
    #仅为测试使用，测试完毕需要注释掉
    #adate='2019-6-31'

    if not check_date(start):
        print("Error #1(check_start_end_dates): invalid start date")
        print("Variable(s):",start)
        return False

    if not check_date(end):
        print("Error #2(check_start_end_dates): invalid end date")
        print("Variable(s):",end)
        return False       
    
    if start > end:
        print("Error #3(check_start_end_dates): irrational start/end dates")
        print("Variable(s): from",start,"to",end)
        return False
        
    return True

if __name__ =="__main__":
    print(check_start_end_dates('2019-1-1','2019-8-18'))

#==============================================================================
if __name__=='__main__':
    txt="上市公司/家"        
        
def hzlen(txt):
    """
    功能：计算含有汉字的字符串的长度
    """
    #strlen=int((len(txt.encode('utf-8')) - len(txt)) / 2 + len(txt))
    #strlen=int((len(txt.encode('gb18030')) - len(txt)) / 2 + len(txt))
    
    import unicodedata
    #Unicode字符有不同的类别
    txtlist=list(unicodedata.category(c) for c in txt)
    strlen=0
    for t in txtlist:
        #类别Lo表示一个非拉丁文字
        if t == 'Lo':
            strlen=strlen+2
        else:
            strlen=strlen+1
    
    return strlen

#==============================================================================
def int10_to_date(int10):
    """
    功能：将10位数字的时间戳转换为日期。
    输入：10位数字的时间戳int10。
    返回：日期字符串。
    """
    import time
    tupTime = time.localtime(int10)
    y4m2d2 = time.strftime("%Y-%m-%d", tupTime)    
    return y4m2d2

if __name__ =="__main__":
    int10=9876543210
    print(int10_to_date(int10))    
#==============================================================================
def equalwidth(string,maxlen=20):
    """
    输入：字符串，中英文混合
    输出：设定等宽度，自动补齐
    """
    reallen=hzlen(string)
    if maxlen < reallen:
        maxlen = reallen
    return string+'.'*(maxlen-reallen)+'：'

if __name__ =="__main__":
    equalwidth("中文1英文abc",maxlen=20)
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
