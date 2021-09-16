# -*- coding: utf-8 -*-
"""
版权：王德宏，北京外国语大学国际商学院
功能：
1、获取证券价格，多种方法，解决网络超时问题
2、既可获取单一证券的价格，也可获取证券组合的价格
3、与爬虫过程有关的错误信息尽可能都在本过程中处理
版本：1.0，2021-1-31
"""

#==============================================================================
#关闭所有警告
import warnings; warnings.filterwarnings('ignore')
from siat.common import *
from siat.translate import *
#==============================================================================
#==============================================================================
#==============================================================================
def get_price(ticker,fromdate,todate,adj=False):
    """
    套壳函数get_prices，为保持兼容
    """
    df=get_prices(ticker,fromdate,todate,adj=adj)
    return df
#==============================================================================
if __name__=='__main__':
    ticker='AAPL'
    fromdate='2020-12-1'
    todate='2021-1-31'
    retry_count=3
    pause=1
    
    ticker='ABCD'
    
    ticker=['AAPL','MSFT']
    ticker=['AAPL','MSFT','ABCD']
    
    ticker=['600011.SS']
    fromdate='2020-1-1'
    todate='2020-6-30'    

def get_prices(ticker,fromdate,todate,adj=False,retry_count=3,pause=1):
    """
    功能：混合抓取雅虎财经证券价格，pandas_datareader + yfinance
    输出：指定收盘价格序列，最新日期的股价排列在前
    ticker: 股票代码。大陆股票代码加上后缀.SZ或.SS，港股代码去掉前导0加后缀.HK
    start: 样本开始日期，尽量远的日期，以便取得足够多的原始样本，yyyy-mm-dd
    end: 样本结束日期，既可以是今天日期，也可以是一个历史日期
    retry_count：网络失败时的重试次数
    pause：每次重试前的间隔秒数
    """
    print("  Searching price info, it may take time depending on network performance ...")
    
    #检查日期期间
    result,start,end=check_period(fromdate,todate)
    if not result:
        print("  Error(get_prices): invalid date period from",fromdate,'to',todate)
        return None     
    
    #抓取证券（列表）价格，不需要调整收盘价：若全为中国A股，首先尝试AkShare
    if not adj:
        try:
            print("  Trying to capture info from Sina Finance for",ticker)
            prices=get_prices_ak(ticker,start,end)
        except:
            pass
        else:
            if not (prices is None):
                num=len(prices)
                if num > 0:
                    print("  Successfully retrieved",num,"records for",ticker)
                else: 
                    print("  Error(get_prices): zero record found for",ticker)
                    return None
                prices['source']='新浪财经'
                prices['ticker']=str(ticker)
                prices['footnote']=''
                return prices
    
    #抓取证券（列表）价格，需要调整收盘价：yfinance优先，线程极易出错，先尝试关闭线程
    #if adj:
    if True:        
        try:
            print("  Trying to capture info from Yahoo Finance using non-threads for",ticker)
            prices=get_prices_yf(ticker,start,end,threads=False)
        except:
            pass
        else:
            if not (prices is None):
                prices['source']='雅虎财经'
                prices['ticker']=str(ticker)
                prices['footnote']=''

                num=len(prices)
                if num > 0:
                    print("  Successfully retrieved",num,"records for",ticker)
                else: 
                    print("  Error(get_prices): zero record found for",ticker)
                    return None
                return prices        

    #抓取证券（列表）价格，需要调整收盘价：yfinance优先，尝试打开线程
    #if adj:
    if True:
        try:
            print("  Trying to capture info from Yahoo Finance using threads for",ticker)
            prices=get_prices_yf(ticker,start,end,threads=True)
        except:
            pass
        else:
            if not (prices is None):
                prices['source']='雅虎财经'
                prices['ticker']=str(ticker)
                prices['footnote']=''

                num=len(prices)
                if num > 0:
                    print("  Successfully retrieved",num,"records for",ticker)
                else: 
                    print("  Error(get_prices): zero record found for",ticker)
                    return None
                return prices    

    #抓取证券（列表）价格，不考虑是否需要调整收盘价：pandas_datareader
    try:    
        print("  Trying to capture info from Yahoo Finance in traditional process for",ticker)
        prices=get_prices_yahoo(ticker,start,end,retry_count=retry_count,pause=pause)
    except:    
        print("  Error(get_prices): retrieving failed, please try again later")    
        return None    
    else:
        if prices is None:
            #返回无
            print("  Warning(get_prices): retrieving returned none for",ticker) 
            return None
        
        if len(prices) == 0:
            print("  Warning(get_prices): retrieved empty info for",ticker)
            return None
    
        prices['source']='雅虎财经'
        prices['ticker']=str(ticker)
        prices['footnote']=''
        num=len(prices)
        if num > 0:
            print("  Successfully retrieved",num,"records for",ticker)
        else:
            print("  Error(get_prices): zero record found for",ticker)
            return None            
        
        return prices
    
    

if __name__=='__main__':
    df1=get_prices('INTC','2020-10-1','2021-1-31')
    df2=get_prices(['INTC'],'2020-10-1','2021-1-31')
    df3=get_prices(['XYZ'],'2020-10-1','2021-1-31')
    df4=get_prices(['INTC','MSFT'],'2020-10-1','2021-1-31')
    df5=get_prices(['INTC','UVW'],'2020-10-1','2021-1-31')
    df6=get_prices(['0988.HK','000858.SZ'],'2020-10-1','2021-1-31')
    df7=get_prices(['INTL','MSFT','0988.HK','000858.SZ'],'2020-10-1','2021-1-31')
    
    
#==============================================================================
if __name__=='__main__':
    ticker='AAPL'
    fromdate='2020-12-1'
    todate='2021-1-31'
    retry_count=3
    pause=1
    
    ticker='ABCD'
    
    ticker=['AAPL','MSFT']
    ticker=['AAPL','MSFT','ABCD']

def get_prices_yahoo(ticker,start,end,retry_count=3,pause=1):
    """
    功能：抓取股价，使用pandas_datareader
    输出：指定收盘价格序列，最新日期的股价排列在前
    ticker: 股票代码。大陆股票代码加上后缀.SZ或.SS，港股代码去掉前导0加后缀.HK
    start: 样本开始日期，尽量远的日期，以便取得足够多的原始样本，yyyy-mm-dd
    end: 样本结束日期，既可以是今天日期，也可以是一个历史日期
    retry_count：网络失败时的重试次数
    pause：每次重试前的间隔秒数
    """
    
    #抓取雅虎股票价格
    from pandas_datareader import data as pdr
    
    #临时修正雅虎网站问题: 2021-7-14
    import yfinance as yfin
    yfin.pdr_override()
    
    try:
        #p=data.DataReader(ticker,'yahoo',start,end,retry_count=retry_count,pause=pause)
        p=pdr.get_data_yahoo(ticker,start=start,end=end)
    except:
        print("  #Error(get_prices_yahoo): data source unreachable, try later")
        return None    
    
    cols=list(p)
    if 'Adj Close' not in cols:
        p['Adj Close']=p['Close']
        
    return p

if __name__=='__main__':
    df1=get_prices_yahoo('AAPL','2020-12-1','2021-1-31')
    df2=get_prices_yahoo('ABCD','2020-12-1','2021-1-31')
    df3=get_prices_yahoo(['AAPL','MSFT'],'2020-12-1','2021-1-31')
    df4=get_prices_yahoo(['AAPL','EFGH','MSFT','ABCD'],'2020-12-1','2021-1-31')
    df5=get_prices_yahoo(['0700.HK','600519.SS'],'2020-12-1','2021-1-31')
    df6=get_prices_yahoo(['AAPL','MSFT','0700.HK','600519.SS'],'2020-12-1','2021-1-31')

#==============================================================================
def get_price_yf(ticker,start,end,threads=False):
    """
    套壳函数get_prices_yf，保持兼容
    """
    df=get_prices_yf(ticker,start,end,threads=threads)
    
    return df


if __name__=='__main__':
    start='2020-12-1'
    end='2021-1-31'
    
    ticker='AAPL'
    ticker=['AAPL','MSFT']
    ticker=['0700.HK','600519.SS']
    ticker=['AAPL','MSFT','0700.HK','600519.SS']
    
    threads=False


def get_prices_yf(ticker,start,end,threads=False):
    """
    功能：从雅虎财经抓取股价，使用yfinance(对非美股抓取速度快，但有时不太稳定)
    输入：股票代码或股票代码列表，开始日期，结束日期
    ticker: 股票代码或股票代码列表。大陆股票代码加上后缀.SZ或.SS，港股代码去掉前导0加后缀.HK
    start: 样本开始日期，尽量远的日期，以便取得足够多的原始样本，yyyy-mm-dd
    end: 样本结束日期，既可以是今天日期，也可以是一个历史日期
    
    输出：指定收盘价格序列，最新日期的股价排列在前
    特别注意：yfinance中的收盘价Close其实是Yahoo Finance中的调整收盘价Adj Close。
    """
   
    #抓取雅虎股票价格
    import yfinance as yf
    ticker1,islist=cvt_yftickerlist(ticker)
    if not islist:
        #下载单一股票的股价
        stock=yf.Ticker(ticker1)
        try:
            p=stock.history(start=start,end=end,threads=threads)
            #p=stock.history(start=start,end=end)
        except Exception as e:
            emsg=str(e)
            #print(emsg)
        
            #检查是否网络超时出错
            key1='WSAETIMEDOUT'
            if emsg.find(key1) != -1:
                print("  Error(get_prices_yf): data source unreachable, try later")
                return None
        
            #单个代码：是否未找到
            key2='Date'
            if emsg.find(key2):
                #单个ticker，未找到代码
                print("  #Error(get_prices_yf): ticker info inaccessible now for",ticker)  
                return None            
    else: 
        #下载股票列表的股价
        try:
            p=yf.download(ticker1,start=start,end=end,progress=False,threads=threads)
        except Exception as e:
            #检查是否网络超时出错
            key1='WSAETIMEDOUT'
            if emsg.find(key1) != -1:
                print("  Error(get_prices_yf): data source unreachable, try later")
                return None

    cols=list(p)
    if 'Adj Close' not in cols:
        p['Adj Close']=p['Close']  
  
    return p

if __name__=='__main__':
    df1=get_prices_yf('AAPL','2020-12-1','2021-1-31')
    df1b=get_prices_yf('EFGH','2020-12-1','2021-1-31')
    df2=get_prices_yf(['AAPL'],'2020-12-1','2021-1-31')
    df3=get_prices_yf(['AAPL','MSFT'],'2020-12-1','2021-1-31')
    df3b=get_prices_yf(['AAPL','MSFS'],'2020-12-1','2021-1-31')
    df4=get_prices_yf(['0700.HK','600519.SS'],'2020-12-1','2021-1-31')
    df5=get_prices_yf(['AAPL','MSFT','0700.HK','600519.SS'],'2020-12-1','2021-1-31')
    df6=get_prices_yf(['ABCD','EFGH','0700.HK','600519.SS'],'2020-12-1','2021-1-31')

#==============================================================================
if __name__=='__main__':
    ticker='600519.SS'
    fromdate='2020-12-1'
    todate='2021-1-31'
    adjust='none'
    
    ticker='000858.SZ'

def get_price_ak(ticker,fromdate,todate,adjust='none'):
    """
    功能：从akshare获得中国国内的股票和指数历史行情，只能处理单个股票或指数
    ticker：雅虎格式，沪市股票为.SS，深市为.SZ，其他的不处理，直接返回None
    fromdate：格式为YYYY-m-d，需要改造为YYYYMMDD
    todate：格式为YYYY-m-d，需要改造为YYYYMMDD
    adjust：不考虑复权为'none'，后复权为'hfq'，前复权为'qfq'
    返回结果：雅虎格式，日期升序，列明首字母大写等
    """
    #变换代码格式
    ticker1=ticker.upper()
    last3=ticker1[-3:]
    headcode=ticker1[:-3]
    if last3 == '.SS':
        ticker2='sh'+headcode
    if last3 == '.SZ':
        ticker2='sz'+headcode
    if last3 not in ['.SS','.SZ']:
        return None

    #变换日期格式
    result,start,end=check_period(fromdate,todate)
    if not result:
        print("  Error(get_price_ak): invalid date period from",fromdate,'to',todate)
        return None   
    start1=start.strftime('%Y%m%d')
    end1=end.strftime('%Y%m%d')
    
    adjustlist=['none','hfq','qfq']
    if adjust not in adjustlist:
        print("  Error(get_price_ak): adjust only supports",adjustlist)
        return None          

    import akshare as ak
    df=None
    #不考虑复权情形
    if adjust == 'none':
        try:
            #抓取指数行情，实际上亦可抓取股票行情
            df = ak.stock_zh_index_daily(symbol=ticker2)    
        except:
            try:
                #股票的历史行情数据（不考虑复权）
                df=ak.stock_zh_a_cdr_daily(ticker2,start1,end1)
            except:
                return None
    
    #考虑复权情形
    if adjust != 'none':
        try:
            #股票的历史行情数据（考虑复权）
            df=ak.stock_zh_a_daily(ticker2,start1,end1,adjust=adjust)
        except:
            return None
    
    if df is None:
        return None
    else:
        df['Date']=df.index
        #去掉可能出现的时区信息，必须使用datetime中的tz_localize
        import datetime as dt
        df['Date']=df['Date'].dt.tz_localize(None)
        #设置新的索引
        df.set_index(['Date'],inplace=True)
        df.rename(columns={'open':'Open','high':'High','low':'Low','close':'Close','volume':'Volume'},inplace=True)
        df['Adj Close']=df['Close']

    df1=df[df.index >= start]
    df2=df1[df1.index <= end]

    return df2

if __name__=='__main__':
    dfx=get_price_ak('600519.SS','2020-12-1','2021-2-5',adjust='none')
    dfy=get_price_ak('600519.SS','2020-12-1','2021-2-5',adjust='hfq')
    df399001=get_price_ak('399001.SZ','2020-12-1','2021-2-5')
    df000688=get_price_ak('000688.SS','2020-12-1','2021-2-5')
    dfz=get_price_ak('AAPL','2020-12-1','2021-2-5')

#==============================================================================
if __name__=='__main__':
    ticker=['600519.SS','000858.SZ']
    fromdate='2020-12-1'
    todate='2021-1-31'
    adjust='none'    

def get_prices_ak(ticker,fromdate,todate,adjust='none'):
    """
    功能：获取中国国内股票或指数的历史行情，多个股票
    """
    #检查是否为多个股票:单个股票代码
    if isinstance(ticker,str):
        df=get_price_ak(ticker,fromdate,todate,adjust=adjust)
        return df
    
    #检查是否为多个股票:空的列表
    if isinstance(ticker,list) and len(ticker) == 0:
        pass
        return None        
    
    #检查是否为多个股票:列表中只有一个代码
    if isinstance(ticker,list) and len(ticker) == 1:
        ticker1=ticker[0]
        df=get_price_ak(ticker1,fromdate,todate,adjust=adjust)
        return df       
    
    #检查是否均为中国国内的股票或指数
    cncode=True
    for t in ticker:
        last3=t[-3:]
        if last3 not in ['.SS','.SZ']:
            cncode=False
            return None
    
    import pandas as pd
    #处理列表中的第一个股票
    i=0
    df=None
    while df is None:
        t=ticker[i]
        df=get_price_ak(t,fromdate,todate,adjust=adjust)
        if not (df is None):
            columns=create_tuple_for_columns(df,t)
            df.columns=pd.MultiIndex.from_tuples(columns)
        else:
            i=i+1
    if (i+1) == len(ticker):
        #已经到达股票代码列表末尾
        return df
        
    #处理列表中的其余股票
    for t in ticker[(i+1):]:
        dft=get_price_ak(t,fromdate,todate,adjust=adjust)
        if not (dft is None):
            columns=create_tuple_for_columns(dft,t)
            dft.columns=pd.MultiIndex.from_tuples(columns)
        
        df=pd.merge(df,dft,how='inner',left_index=True,right_index=True)
     
    return df

if __name__=='__main__':
    dfm=get_prices_ak(['600519.SS','000858.SZ'],'2020-12-1','2021-1-31')
    dfm2=get_prices_ak(['600519.SS','AAPL'],'2020-12-1','2021-1-31')
    
#==============================================================================  
def create_tuple_for_columns(df_a, multi_level_col):
    """
    Create a columns tuple that can be pandas MultiIndex to create multi level column

    :param df_a: pandas dataframe containing the columns that must form the first level of the multi index
    :param multi_level_col: name of second level column
    :return: tuple containing (first_level_cols,second_level_col)
    """
    temp_columns = []
    for item in df_a.columns:
        temp_columns.append((item, multi_level_col))
    
    return temp_columns    
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
def get_price_portfolio(tickerlist,sharelist,fromdate,todate,adj=False):
    """
    套壳函数get_prices_portfolio
    """
    df=get_prices_portfolio(tickerlist,sharelist,fromdate,todate,adj=adj)
    return df

if __name__=='__main__':
    tickerlist=['INTC','MSFT']
    sharelist=[0.6,0.4]
    fromdate='2020-11-1'
    todate='2021-1-31'

def get_prices_portfolio(tickerlist,sharelist,fromdate,todate,adj=False):
    """
    功能：抓取投资组合的每日价值
    输入：股票代码列表，份额列表，开始日期，结束日期
    tickerlist: 股票代码列表
    sharelist：持有份额列表，与股票代码列表一一对应
    fromdate: 样本开始日期。格式：'YYYY-MM-DD'
    todate: 样本结束日期。既可以是今天日期，也可以是一个历史日期    
    
    输出：投资组合的价格序列，按照日期升序排列
    """
    
    #检查股票列表个数与份额列表个数是否一致
    if len(tickerlist) != len(sharelist):
        print("  Error(get_prices_portfolio): numbers of stocks and shares mismatch.")
        return None        
    
    #抓取股票价格
    p=get_prices(tickerlist,fromdate,todate,adj=adj)
    if p is None: return None
    
    #结果非空时，检查整列为空的证券代码
    nancollist=[] 
    collist=list(p)
    for c in collist:
        if p[c].isnull().all():
            nancollist=nancollist+[c]
    #查找错误的ticker
    wrongtickers=[]
    for w in tickerlist:
        nancolstr=str(nancollist)
        if nancolstr.find(w.upper()) != -1:    #找到
            wrongtickers=wrongtickers+[w]
        
    if len(wrongtickers) > 0:
        print("  Warning(get_prices_portfolio): price info not found for",wrongtickers)
        print("  Warning(get_prices_portfolio): dropping all the rows related to",wrongtickers)
        p.dropna(axis=1,how="all",inplace=True)   # 丢弃全为缺失值的那些列
        
        #删除投资组合中相关的权重
        for w in wrongtickers:
            pos=tickerlist.index(w)
            del sharelist[pos]

    if len(sharelist) > 1:    
        import pandas as pd
        #计算投资者的开盘价
        op=p['Open']
        #计算投资组合的价值
        oprice=pd.DataFrame(op.dot(sharelist))
        oprice.rename(columns={0: 'Open'}, inplace=True)    

        #计算投资者的收盘价
        cp=p['Close']
        #计算投资组合的价值
        cprice=pd.DataFrame(cp.dot(sharelist))
        cprice.rename(columns={0: 'Close'}, inplace=True) 
    
        #计算投资者的调整收盘价
        acp=p['Adj Close']
        #计算投资组合的价值
        acprice=pd.DataFrame(acp.dot(sharelist))
        acprice.rename(columns={0: 'Adj Close'}, inplace=True) 

        #合成开盘价、收盘价和调整收盘价
        ocprice=pd.merge(oprice,cprice,how='inner',left_index=True,right_index=True)
        prices=pd.merge(ocprice,acprice,how='inner',left_index=True,right_index=True)
    else:
        prices=p
    
    #提取日期和星期几
    prices['Date']=prices.index.strftime("%Y-%m-%d")
    prices['Weekday']=prices.index.weekday+1

    prices['Portfolio']=str(tickerlist)
    prices['Shares']=str(sharelist)
    prices['Adjustment']=prices.apply(lambda x: \
          False if x['Close']==x['Adj Close'] else True, axis=1)

    stockdf=prices[['Portfolio','Shares','Date','Weekday', \
                    'Open','Close','Adj Close','Adjustment']]  

    return stockdf      

if __name__=='__main__':
    tickerlist=['INTC','MSFT']
    sharelist=[0.6,0.4]
    fromdate='2020-11-1'
    todate='2021-1-31'
    dfp=get_prices_portfolio(tickerlist,sharelist,fromdate,todate)

#==============================================================================
#==============================================================================
if __name__=='__main__':
    ticker='AAPL'

    ticker=['AAPL','MSFT','0700.HK','600519.SS']

def cvt_yftickerlist(ticker):
    """
    功能：转换pandas_datareader的tickerlist为yfinance的格式
    输入参数：单一股票代码或pandas_datareader的股票代码列表

    输出参数：yfinance格式的股票代码列表
    """
    #如果不是股票代码列表，直接返回股票代码
    if not isinstance(ticker,list): return ticker,False
    
    #如果是股票代码列表，但只有一个元素
    if len(ticker)==1: return ticker[0],False
    
    #如果是股票代码列表，有两个及以上元素
    yftickerlist=ticker[0]
    for t in ticker[1:]:
        yftickerlist=yftickerlist+' '+t.upper()
    
    return yftickerlist,True


if __name__=='__main__':
    cvt_yftickerlist('AAPL')
    cvt_yftickerlist(['AAPL'])
    cvt_yftickerlist(['AAPL','MSFT'])
    cvt_yftickerlist(['AAPL','MSFT','0700.hk'])
    
#==============================================================================
if __name__=='__main__':
    url='https://finance.yahoo.com'

def test_website(url='https://finance.yahoo.com'):
    """
    功能：测试网站的联通性和反应时间
    优点：真实
    缺点：运行过程非常慢
    """
    print("  Testing internet connection to",url,"...")
    import pycurl
    from io import BytesIO

    #进行网络测试
    c = pycurl.Curl()
    buffer = BytesIO()  # 创建缓存对象
    c.setopt(c.WRITEDATA, buffer)  # 设置资源数据写入到缓存对象
    c.setopt(c.URL, url)  # 指定请求的URL
    c.setopt(c.MAXREDIRS, 3)  # 指定HTTP重定向的最大数
    
    test_result=True
    test_msg=""
    try:
        c.perform()  # 测试目标网站
    except Exception as e:
        c.close()
        
        #print(e)
        print("  #Error(test_website2):",e)
              
        test_result=False
        test_msg="UNREACHABLE"        
        
        return test_result,test_msg
        
    #获得网络测试结果阐述
    http_code = c.getinfo(pycurl.HTTP_CODE)  # 返回的HTTP状态码
    dns_resolve = c.getinfo(pycurl.NAMELOOKUP_TIME)  # DNS解析所消耗的时间
    http_conn_time = c.getinfo(pycurl.CONNECT_TIME)  # 建立连接所消耗的时间
    http_pre_trans = c.getinfo(pycurl.PRETRANSFER_TIME)  # 从建立连接到准备传输所消耗的时间
    http_start_trans = c.getinfo(pycurl.STARTTRANSFER_TIME)  # 从建立连接到传输开始消耗的时间
    http_total_time = c.getinfo(pycurl.TOTAL_TIME)  # 传输结束所消耗的总时间
    http_size_download = c.getinfo(pycurl.SIZE_DOWNLOAD)  # 下载数据包大小
    http_size_upload = c.getinfo(pycurl.SIZE_UPLOAD)  # 上传数据包大小
    http_header_size = c.getinfo(pycurl.HEADER_SIZE)  # HTTP头部大小
    http_speed_downlaod = c.getinfo(pycurl.SPEED_DOWNLOAD)  # 平均下载速度
    http_speed_upload = c.getinfo(pycurl.SPEED_UPLOAD)  # 平均上传速度
    http_redirect_time = c.getinfo(pycurl.REDIRECT_TIME)  # 重定向所消耗的时间
    
    """
    print('HTTP响应状态： %d' % http_code)
    print('DNS解析时间：%.2f ms' % (dns_resolve * 1000))
    print('建立连接时间： %.2f ms' % (http_conn_time * 1000))
    print('准备传输时间： %.2f ms' % (http_pre_trans * 1000))
    print("传输开始时间： %.2f ms" % (http_start_trans * 1000))
    print("传输结束时间： %.2f ms" % (http_total_time * 1000))
    print("重定向时间： %.2f ms" % (http_redirect_time * 1000))
    print("上传数据包大小： %d bytes/s" % http_size_upload)
    print("下载数据包大小： %d bytes/s" % http_size_download)
    print("HTTP头大小： %d bytes/s" % http_header_size)
    print("平均上传速度： %d k/s" % (http_speed_upload / 1024))
    print("平均下载速度： %d k/s" % (http_speed_downlaod / 1024))
    """
    c.close()
    
    if http_speed_downlaod >= 100*1024: test_msg="FAST"
    if http_speed_downlaod < 100*1024: test_msg="GOOD"
    if http_speed_downlaod < 50*1024: test_msg="GOOD"
    if http_speed_downlaod < 10*1024: test_msg="VERY SLOW"
    if http_speed_downlaod < 1*1024: test_msg="UNSTABLE"
    
    return test_result,test_msg

if __name__=='__main__':
    test_website()
    
#==============================================================================
def calc_daily_return(pricedf):
    """
    功能：基于从雅虎财经抓取的单个证券价格数据集计算其日收益率
    输入：从雅虎财经抓取的单个证券价格数据集pricedf，基于收盘价或调整收盘价进行计算
    输出：证券日收益率序列，按照日期升序排列。
    """
    import numpy as np    
    #计算算术日收益率：基于收盘价
    pricedf["Daily Ret"]=pricedf['Close'].pct_change()
    pricedf["Daily Ret%"]=pricedf["Daily Ret"]*100.0
    
    #计算算术日收益率：基于调整收盘价
    pricedf["Daily Adj Ret"]=pricedf['Adj Close'].pct_change()
    pricedf["Daily Adj Ret%"]=pricedf["Daily Adj Ret"]*100.0
    
    #计算对数日收益率
    pricedf["log(Daily Ret)"]=np.log(pricedf["Daily Ret"]+1)
    pricedf["log(Daily Adj Ret)"]=np.log(pricedf["Daily Adj Ret"]+1)
    
    return pricedf 
    

if __name__ =="__main__":
    ticker='AAPL'
    fromdate='2018-1-1'
    todate='2020-3-16'
    pricedf=get_price(ticker, fromdate, todate)
    drdf=calc_daily_return(pricedf)    
    

#==============================================================================
def calc_rolling_return(drdf, period="Weekly"):
    """
    功能：基于单个证券的日收益率数据集, 计算其滚动期间收益率
    输入：
    单个证券的日收益率数据集drdf。
    期间类型period，默认为每周。
    输出：期间滚动收益率序列，按照日期升序排列。
    """
    #检查period类型
    periodlist = ["Weekly","Monthly","Quarterly","Annual"]
    if not (period in periodlist):
        print("*** 错误#1(calc_rolling_return)，仅支持期间类型：",periodlist)
        return None

    #换算期间对应的实际交易天数
    perioddays=[5,21,63,252]
    rollingnum=perioddays[periodlist.index(period)]    
    
    #计算滚动收益率：基于收盘价
    retname1=period+" Ret"
    retname2=period+" Ret%"
    import numpy as np
    drdf[retname1]=np.exp(drdf["log(Daily Ret)"].rolling(rollingnum).sum())-1.0
    drdf[retname2]=drdf[retname1]*100.0
    
    #计算滚动收益率：基于调整收盘价
    retname3=period+" Adj Ret"
    retname4=period+" Adj Ret%"
    drdf[retname3]=np.exp(drdf["log(Daily Adj Ret)"].rolling(rollingnum).sum())-1.0
    drdf[retname4]=drdf[retname3]*100.0
    
    return drdf

if __name__ =="__main__":
    ticker='000002.SZ'
    period="Weekly"
    prdf=calc_rolling_return(drdf, period) 
    prdf=calc_rolling_return(drdf, "Monthly")
    prdf=calc_rolling_return(drdf, "Quarterly")
    prdf=calc_rolling_return(drdf, "Annual")

#==============================================================================
def calc_expanding_return(drdf,basedate):
    """
    功能：基于日收益率数据集，从起始日期开始到结束日期的扩展窗口收益率序列。
    输入：
    日收益率数据集drdf。
    输出：期间累计收益率序列，按照日期升序排列。
    """
    
    #计算累计收益率：基于收盘价
    retname1="Exp Ret"
    retname2="Exp Ret%"
    import numpy as np
    drdf[retname1]=np.exp(drdf[drdf.index >= basedate]["log(Daily Ret)"].expanding(min_periods=1).sum())-1.0
    drdf[retname2]=drdf[retname1]*100.0  
    
    #计算累计收益率：基于调整收盘价
    retname3="Exp Adj Ret"
    retname4="Exp Adj Ret%"
    drdf[retname3]=np.exp(drdf[drdf.index >= basedate]["log(Daily Adj Ret)"].expanding(min_periods=1).sum())-1.0
    drdf[retname4]=drdf[retname3]*100.0  
    
    return drdf

if __name__ =="__main__":
    ticker='000002.SZ'
    basedate="2019-1-1"
    erdf=calc_expanding_return(prdf,basedate)  

#==============================================================================
def rolling_price_volatility(df, period="Weekly"):
    """
    功能：基于单个证券价格的期间调整标准差, 计算其滚动期间价格风险
    输入：
    单个证券的日价格数据集df。
    期间类型period，默认为每周。
    输出：期间滚动价格风险序列，按照日期升序排列。
    """
    #检查period类型
    periodlist = ["Weekly","Monthly","Quarterly","Annual"]
    if not (period in periodlist):
        print("*** 错误#1(calc_rolling_volatility)，仅支持期间类型：",periodlist)
        return None

    #换算期间对应的实际交易天数
    perioddays=[5,21,63,252]
    rollingnum=perioddays[periodlist.index(period)]    
    
    #计算滚动期间的调整标准差价格风险：基于收盘价
    retname1=period+" Price Volatility"
    import numpy as np
    df[retname1]=df["Close"].rolling(rollingnum).apply(lambda x: np.std(x,ddof=1)/np.mean(x)*np.sqrt(len(x)))
    
    #计算滚动期间的调整标准差价格风险：基于调整收盘价
    retname3=period+" Adj Price Volatility"
    df[retname3]=df["Adj Close"].rolling(rollingnum).apply(lambda x: np.std(x,ddof=1)/np.mean(x)*np.sqrt(len(x)))
    
    return df

if __name__ =="__main__":
    period="Weekly"
    df=get_price('000002.SZ','2018-1-1','2020-3-16')
    vdf=rolling_price_volatility(df, period) 

#==============================================================================
def expanding_price_volatility(df,basedate):
    """
    功能：基于日价格数据集，从起始日期开始到结束日期调整价格风险的扩展窗口序列。
    输入：
    日价格数据集df。
    输出：期间扩展调整价格风险序列，按照日期升序排列。
    """
    
    #计算扩展窗口调整价格风险：基于收盘价
    retname1="Exp Price Volatility"
    import numpy as np
    df[retname1]=df[df.index >= basedate]["Close"].expanding(min_periods=1).apply(lambda x: np.std(x,ddof=1)/np.mean(x)*np.sqrt(len(x)))
    
    #计算扩展窗口调整价格风险：基于调整收盘价
    retname3="Exp Adj Price Volatility"
    df[retname3]=df[df.index >= basedate]["Adj Close"].expanding(min_periods=1).apply(lambda x: np.std(x,ddof=1)/np.mean(x)*np.sqrt(len(x)))
    
    return df

if __name__ =="__main__":
    df=get_price('000002.SZ','2018-1-1','2020-3-16')    
    evdf=expanding_price_volatility(df)  


#==============================================================================
def rolling_ret_volatility(df, period="Weekly"):
    """
    功能：基于单个证券的期间收益率, 计算其滚动收益率波动风险
    输入：
    单个证券的期间收益率数据集df。
    期间类型period，默认为每周。
    输出：滚动收益率波动风险序列，按照日期升序排列。
    """
    #检查period类型
    periodlist = ["Weekly","Monthly","Quarterly","Annual"]
    if not (period in periodlist):
        print("*** 错误#1(rolling_ret_volatility)，仅支持期间类型：",periodlist)
        return None

    #换算期间对应的实际交易天数
    perioddays=[5,21,63,252]
    rollingnum=perioddays[periodlist.index(period)]    
    
    #计算滚动标准差：基于普通收益率
    periodret=period+" Ret"
    retname1=period+" Ret Volatility"
    retname2=retname1+'%'
    import numpy as np
    df[retname1]=df[periodret].rolling(rollingnum).apply(lambda x: np.std(x,ddof=1))
    df[retname2]=df[retname1]*100.0
    
    #计算滚动标准差：基于调整收益率
    periodadjret=period+" Adj Ret"
    retname3=period+" Adj Ret Volatility"
    retname4=retname3+'%'
    df[retname3]=df[periodadjret].rolling(rollingnum).apply(lambda x: np.std(x,ddof=1))
    df[retname4]=df[retname3]*100.0
    
    return df

if __name__ =="__main__":
    period="Weekly"
    pricedf=get_price('000002.SZ','2018-1-1','2020-3-16')
    retdf=calc_daily_return(pricedf)
    vdf=rolling_ret_volatility(retdf, period) 

#==============================================================================
def expanding_ret_volatility(df,basedate):
    """
    功能：基于日收益率数据集，从起始日期basedate开始的收益率波动风险扩展窗口序列。
    输入：
    日收益率数据集df。
    输出：扩展调整收益率波动风险序列，按照日期升序排列。
    """
    
    #计算扩展窗口调整收益率波动风险：基于普通收益率
    retname1="Exp Ret Volatility"
    retname2="Exp Ret Volatility%"
    import numpy as np
    df[retname1]=df[df.index >= basedate]["Daily Ret"].expanding(min_periods=1).apply(lambda x: np.std(x,ddof=1)*np.sqrt(len(x)))
    df[retname2]=df[retname1]*100.0
    
    #计算扩展窗口调整收益率风险：基于调整收益率
    retname3="Exp Adj Ret Volatility"
    retname4="Exp Adj Ret Volatility%"
    df[retname3]=df[df.index >= basedate]["Daily Adj Ret"].expanding(min_periods=1).apply(lambda x: np.std(x,ddof=1)*np.sqrt(len(x)))
    df[retname4]=df[retname3]*100.0
    
    return df

if __name__ =="__main__":
    basedate='2019-1-1'
    pricedf=get_price('000002.SZ','2018-1-1','2020-3-16')    
    retdf=calc_daily_return(pricedf)
    evdf=expanding_ret_volatility(retdf,'2019-1-1')  

#==============================================================================
def lpsd(ds):
    """
    功能：基于给定数据序列计算其下偏标准差。
    输入：
    数据序列ds。
    输出：序列的下偏标准差。
    """
    import numpy as np
    #若序列长度为0则直接返回数值型空值
    if len(ds) == 0: return np.NaN
    
    #求均值
    import numpy as np
    miu=np.mean(ds)
    
    #计算根号内的下偏平方和
    sum=0; ctr=0
    for s in list(ds):
        if s < miu:
            sum=sum+pow((s-miu),2)
            ctr=ctr+1
    
    #下偏标准差
    if ctr > 1:
        result=np.sqrt(sum/(ctr-1))
    elif ctr == 1: result=np.NaN
    else: result=np.NaN
        
    return result
    
if __name__ =="__main__":
    df=get_price("000002.SZ","2020-1-1","2020-3-16")
    print(lpsd(df['Close']))

#==============================================================================
def rolling_ret_lpsd(df, period="Weekly"):
    """
    功能：基于单个证券期间收益率, 计算其滚动收益率损失风险。
    输入：
    单个证券的期间收益率数据集df。
    期间类型period，默认为每周。
    输出：滚动收益率的下偏标准差序列，按照日期升序排列。
    """
    #检查period类型
    periodlist = ["Weekly","Monthly","Quarterly","Annual"]
    if not (period in periodlist):
        print("*** 错误#1(rolling_ret_lpsd)，仅支持期间类型：",periodlist)
        return None

    #换算期间对应的实际交易天数
    perioddays=[5,21,63,252]
    rollingnum=perioddays[periodlist.index(period)]    
    
    #计算滚动下偏标准差：基于普通收益率
    periodret=period+" Ret"
    retname1=period+" Ret LPSD"
    retname2=retname1+'%'
    #import numpy as np
    df[retname1]=df[periodret].rolling(rollingnum).apply(lambda x: lpsd(x))
    df[retname2]=df[retname1]*100.0
    
    #计算滚动下偏标准差：基于调整收益率
    periodadjret=period+" Adj Ret"
    retname3=period+" Adj Ret LPSD"
    retname4=retname3+'%'
    df[retname3]=df[periodadjret].rolling(rollingnum).apply(lambda x: lpsd(x))
    df[retname4]=df[retname3]*100.0
    
    return df

if __name__ =="__main__":
    period="Weekly"
    pricedf=get_price('000002.SZ','2018-1-1','2020-3-16')
    retdf=calc_daily_return(pricedf)
    vdf=rolling_ret_lpsd(retdf, period) 

#==============================================================================
def expanding_ret_lpsd(df,basedate):
    """
    功能：基于日收益率数据集，从起始日期basedate开始的收益率损失风险扩展窗口序列。
    输入：
    日收益率数据集df。
    输出：扩展调整收益率波动风险序列，按照日期升序排列。
    """
    
    #计算扩展窗口调整收益率下偏标准差：基于普通收益率
    retname1="Exp Ret LPSD"
    retname2=retname1+'%'
    import numpy as np
    df[retname1]=df[df.index >= basedate]["Daily Ret"].expanding(min_periods=1).apply(lambda x: lpsd(x)*np.sqrt(len(x)))
    df[retname2]=df[retname1]*100.0
    
    #计算扩展窗口调整下偏标准差：基于调整收益率
    retname3="Exp Adj Ret LPSD"
    retname4=retname3+'%'
    df[retname3]=df[df.index >= basedate]["Daily Adj Ret"].expanding(min_periods=1).apply(lambda x: lpsd(x)*np.sqrt(len(x)))
    df[retname4]=df[retname3]*100.0
    
    return df

if __name__ =="__main__":
    basedate='2019-1-1'
    pricedf=get_price('000002.SZ','2018-1-1','2020-3-16')    
    retdf=calc_daily_return(pricedf)
    evdf=expanding_ret_lpsd(retdf,'2019-1-1')  
#==============================================================================
if __name__ =="__main__":
    portfolio={'Market':('US','^GSPC'),'AAPL':1}
    fromdate='2020-1-1'
    todate='2020-6-30'
    adj=False

def get_portfolio_prices(portfolio,fromdate,todate,adj=False):
    """
    功能：抓取投资组合portfolio的每日价值和FF3各个因子
    输入：投资组合portfolio，开始日期，结束日期
    fromdate: 样本开始日期。格式：'YYYY-MM-DD'
    todate: 样本结束日期。既可以是今天日期，也可以是一个历史日期    
    
    输出：投资组合的价格序列，按照日期升序排列
    """
    
    #解构投资组合
    _,mktidx,tickerlist,sharelist=decompose_portfolio(portfolio)
    
    #检查股票列表个数与份额列表个数是否一致
    if len(tickerlist) != len(sharelist):
        print("#Error(get_portfolio_prices): numbers of stocks and shares mismatch.")
        return None        
    
    #从雅虎财经抓取股票价格
    p=get_prices(tickerlist,fromdate,todate,adj=adj)
    if p is None:
        print("#Error(get_portfolio_prices): information inaccessible for",tickerlist)
        return None  

    import pandas as pd
    if len(sharelist) > 0:    
        #计算投资组合的开盘价
        op=p['Open']
        #计算投资组合的价值
        try:
            oprice=pd.DataFrame(op.dot(sharelist))
        except:
            print("#Error(get_portfolio_prices): failed to get info for some ticker(s)")
            return None
        oprice.rename(columns={0: 'Open'}, inplace=True)    

        #计算投资组合的收盘价
        cp=p['Close']
        #计算投资组合的价值
        cprice=pd.DataFrame(cp.dot(sharelist))
        cprice.rename(columns={0: 'Close'}, inplace=True) 
        
        #计算投资组合的调整收盘价
        acp=p['Adj Close']
        #计算投资组合的价值
        acprice=pd.DataFrame(acp.dot(sharelist))
        acprice.rename(columns={0: 'Adj Close'}, inplace=True) 
    
        #计算投资组合的交易量
        vol=p['Volume']
        #计算投资组合的价值
        pfvol=pd.DataFrame(vol.dot(sharelist))
        pfvol.rename(columns={0: 'Volume'}, inplace=True) 
    
        #计算投资组合的交易金额
        for t in tickerlist:
            p['Amount',t]=p['Close',t]*p['Volume',t]
        amt=p['Amount']
        #计算投资组合的价值
        pfamt=pd.DataFrame(amt.dot(sharelist))
        pfamt.rename(columns={0: 'Amount'}, inplace=True) 

        #合成开盘价、收盘价、调整收盘价、交易量和交易金额
        pf1=pd.merge(oprice,cprice,how='inner',left_index=True,right_index=True)    
        pf2=pd.merge(pf1,acprice,how='inner',left_index=True,right_index=True)
        pf3=pd.merge(pf2,pfvol,how='inner',left_index=True,right_index=True)
        pf4=pd.merge(pf3,pfamt,how='inner',left_index=True,right_index=True)
    """
    else:
        p['Amount']=p['Close']*p['Volume']
        pf4=p
    """
    pf4['Ret%']=pf4['Close'].pct_change()*100.0

    #获得期间的市场收益率：假设无风险收益率非常小，可以忽略
    m=get_prices(mktidx,fromdate,todate)
    m['Mkt-RF']=m['Close'].pct_change()*100.0
    m['RF']=0.0
    rf_df=m[['Mkt-RF','RF']]
    
    #合并pf4与rf_df
    prices=pd.merge(pf4,rf_df,how='left',left_index=True,right_index=True)

    #提取日期和星期几
    prices['Date']=prices.index.strftime("%Y-%m-%d")
    prices['Weekday']=prices.index.weekday+1

    prices['Portfolio']=str(tickerlist)
    prices['Shares']=str(sharelist)
    
    prices['Adjustment']=adj
    try:
        prices['Adjustment']=prices.apply(lambda x: \
          False if x['Close']==x['Adj Close'] else True, axis=1)
    except: pass
    
    pfdf=prices[['Portfolio','Shares','Date','Weekday', \
                 'Open','Close','Adj Close','Adjustment', \
                'Volume','Amount','Ret%','Mkt-RF','RF']]  

    return pfdf      


#==============================================================================
if __name__ =="__main__":
    ticker='AAPL'  

def recent_stock_split(ticker):
    """
    功能：显示股票最近一年的分拆历史
    输入：单一股票代码
    输出：最近一年的分拆历史
    """   
    #获取今日日期
    import datetime
    today = datetime.date.today()
    fromdate = date_adjust(today,-365)
    
    import yfinance as yf
    stock = yf.Ticker(ticker)
    try:
        div=stock.splits
    except:
        print("#Error(recent_stock_split): no split info found for",ticker)
        return None    
    if len(div)==0:
        print("#Warning(recent_stock_split): no split info found for",ticker)
        return None      
    
    #过滤期间
    div2=div[div.index >= fromdate]
    if len(div2)==0:
        print("#Warning(stock_split): no split info from",fromdate,'to',today)
        return None          
    
    #对齐打印
    import pandas as pd    
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    
    divdf=pd.DataFrame(div2)
    divdf['Index Date']=divdf.index
    datefmt=lambda x : x.strftime('%Y-%m-%d')
    divdf['Split Date']= divdf['Index Date'].apply(datefmt)
    
    #增加星期
    from datetime import datetime
    weekdayfmt=lambda x : x.isoweekday()
    divdf['Weekdayiso']= divdf['Index Date'].apply(weekdayfmt)
    wdlist=['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    wdfmt=lambda x : wdlist[x-1]
    divdf['Weekday']= divdf['Weekdayiso'].apply(wdfmt)
    
    #增加序号
    divdf['Seq']=divdf['Split Date'].rank(ascending=1)
    divdf['Seq']=divdf['Seq'].astype('int')
    
    divdf['Splitint']=divdf['Stock Splits'].astype('int')
    splitfmt=lambda x: "1:"+str(x)
    divdf['Splits']=divdf['Splitint'].apply(splitfmt)
    
    divprt=divdf[['Seq','Split Date','Weekday','Splits']]
    
    print("\n=== 近期股票分拆历史 ===")
    print("股票:",ticker,'\b,',ticker)
    print("期间:",fromdate,"to",today)
    divprt.columns=['序号','日期','星期','分拆比例']
    print(divprt.to_string(index=False))   
    
    import datetime
    today = datetime.date.today()
    print("数据来源: 雅虎财经,",today)
    
    return divdf
    
    
if __name__ =="__main__":
    df=recent_stock_split('AAPL')

#==============================================================================
if __name__ =="__main__":
    ticker='AAPL'

def get_last_close(ticker):
    """
    功能：从雅虎财经抓取股票股价或指数价格或投资组合价值，使用pandas_datareader
    输入：股票代码或股票代码列表，开始日期，结束日期
    ticker: 股票代码或者股票代码列表。
    大陆股票代码加上后缀.SZ或.SS，港股代码去掉前导0加后缀.HK
    输出：最新的收盘价和日期
    """
    #获取今日日期
    import datetime
    today = datetime.date.today()
    fromdate = date_adjust(today,-30)
    
    #抓取雅虎股票价格
    from pandas_datareader import data
    try:
        price=data.DataReader(ticker,'yahoo',fromdate,today)
    except:
        print("\n  #Error(get_last_close): failed in retrieving prices!")        
        return None,None            
    if price is None:
        print("\n  #Error(get_last_close): retrieved none info!")
        return None,None  
    if len(price)==0:
        print("\n  #Error(get_last_close): retrieved empty info!")
        return None,None         
    price['date']=price.index
    datecvt=lambda x:x.strftime("%Y-%m-%d")
    price['date']=price['date'].apply(datecvt)
    price.sort_values("date",inplace=True)

    #提取最新的日期和收盘价
    lasttradedate=list(price['date'])[-1]
    lasttradeclose=round(list(price['Close'])[-1],2)

    return lasttradedate,lasttradeclose

if __name__ =="__main__":
    get_last_close('AAPL')

#==============================================================================

#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
