# -*- coding: utf-8 -*-
"""
本模块功能：中国基金市场
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2020年10月17日
最新修订日期：2020年10月21日
作者：王德宏 (WANG Dehong, Peter)
作者单位：北京外国语大学国际商学院
版权所有：王德宏
用途限制：仅限研究与教学使用，不可商用！商用需要额外授权。
特别声明：作者不对使用本工具进行证券投资导致的任何损益负责！
"""

#==============================================================================
#关闭所有警告
import warnings; warnings.filterwarnings('ignore')
from siat.common import *
from siat.translate import *
from siat.grafix import *
from siat.bond_base import *
#==============================================================================
#==============================================================================
#==============================================================================

if __name__=='__main__':
    fund_type='全部类型'

def pof_list_china(fund_type='全部类型',printout=True):
    """
    功能：抓取公募基金列表，按照基金类型列表，按照基金名称拼音排序
    """
    print("Searching for publicly offering fund (POF) information in China ...")
    import akshare as ak
    
    #基金基本信息：基金代码，基金简称，基金类型
    df = ak.fund_em_fund_name()
    df.sort_values(by=['拼音全称'],na_position='first',inplace=True)
    df.drop_duplicates(subset=['基金代码','基金类型'], keep='first',inplace=True)    
    
    #获取基金类型列表，并去掉重复项
    typelist=list(set(list(df['基金类型'])))
    #判断类型是否支持
    if fund_type not in typelist+['全部类型']:
        print("  #Error(fund_list_china): unsupported fund type:",fund_type)
        print("  Supported fund_type:",typelist+['全部类型'])
        return None

    #摘取选定的基金类型
    if fund_type != '全部类型':
        df2=df[df['基金类型']==fund_type]
    else:
        df2=df
    df3=df2[['基金简称','基金代码','基金类型']]
    df3.reset_index(drop=True,inplace=True) 
    
    #打印种类数量信息    
    if printout:
        num=len(df3)
        if fund_type != '全部类型':
            print(texttranslate("共找到")+str(num)+texttranslate("支基金, 类型为")+fund_type)
            return df3
        
        print("\n",texttranslate("======= 中国公募基金种类概况 ======="))
        print(texttranslate("公募基金总数："),"{:,}".format(num))
        print(texttranslate("其中包括："))
        
        #typelist.sort(reverse=False)
        typelist=['股票型','股票指数','股票-FOF','债券型','债券指数','定开债券', \
                  '混合型','混合-FOF','货币型','ETF-场内','QDII','QDII-指数', \
                  'QDII-ETF','理财型']
        maxlen=0
        for t in typelist:
            tlen=strlen(t)
            if tlen > maxlen: maxlen=tlen
        maxlen=maxlen+1
        
        for t in typelist:
            tlen=strlen(t)
            n=len(df[df['基金类型']==t])
            prefix=' '*4+t+' '*(maxlen-tlen)+':'
            print(prefix,"{:,}".format(n),"\b,",round(n/num*100,2),'\b%')

        import datetime
        today = datetime.date.today()
        print(texttranslate("数据来源：东方财富/天天基金,"),today)
        
    return df3

if __name__=='__main__':
    df=pof_list_china()

#==============================================================================
if __name__=='__main__':
    info_type='单位净值'
    fund_type='债券型'

def oef_rank_china(info_type='单位净值',fund_type='全部类型',rank=10):
    """
    功能：中国开放式基金排名，单位净值，累计净值，手续费
    """
    typelist=['单位净值','累计净值','手续费']
    if info_type not in typelist:
        print("  #Error(oef_rank_china): unsupported info type",info_type)
        print("  Supported info type:",typelist)
        return None
    
    print("Searching for open-ended fund (OEF) information in China ...")
    import akshare as ak   
    
    #获取开放式基金实时信息
    df1 = ak.fund_em_open_fund_daily()
    collist=list(df1)
    nvname1=collist[2]
    nvdate=nvname1[:10]
    nvname2=collist[3]
    #修改列名
    df1.rename(columns={nvname1:'单位净值',nvname2:'累计净值'}, inplace=True) 
    #df1a=df1.drop(df1[df1['单位净值']==''].index)
    #df1b=df1a.drop(df1a[df1a['累计净值']==''].index)
    df1c=df1[['基金代码','基金简称','单位净值','累计净值','申购状态','赎回状态','手续费']]
    
    
    #获取所有公募基金类型信息
    df2 = ak.fund_em_fund_name()
    df2a=df2[['基金代码','基金类型']]
    
    #合成基金类型信息
    import pandas as pd
    df = pd.merge(df1c,df2a,on = ['基金代码'],how='left')
    #过滤基金类型
    if fund_type != '全部类型':
        fundtypelist=list(set(list(df['基金类型'])))
        found=False
        for ft in fundtypelist:
            if fund_type in ft: 
                found=True
                break
        if not found:
            print("  #Error(oef_rank_china): unsupported fund type",fund_type)
            print("  Supported fund type:",fundtypelist)
            return None
        fund_filter=lambda x: fund_type in x
        df['基金类型s']=df['基金类型'].apply(fund_filter)
        df=df[df['基金类型s']==True]    

    
    if info_type == '单位净值':
        df.sort_values(by=['单位净值'],ascending=False,inplace=True)
        dfprint=df[['基金简称','基金代码','基金类型','单位净值','累计净值','手续费']]
        print(texttranslate("\n===== 中国开放式基金排名：单位净值 ====="))
    
    if info_type == '累计净值':
        df.sort_values(by=['累计净值'],ascending=False,inplace=True)
        dfprint=df[['基金简称','基金代码','基金类型','累计净值','单位净值','手续费']]
        print(texttranslate("\n===== 中国开放式基金排名：累计净值 ====="))      
    
    if info_type == '手续费':
        df.sort_values(by=['手续费'],ascending=False,inplace=True)
        dfprint=df[['基金简称','基金代码','基金类型','手续费']]
        print(texttranslate("\n===== 中国开放式基金排名：手续费 ====="))          
        
    #设置打印对齐
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    
    dfprint.dropna(inplace=True)
    dfprint.reset_index(drop=True,inplace=True)
    if rank >= 0:
        dfprint10=dfprint.head(rank)
    else:
        dfprint10=dfprint.tail(-rank)
    #print(dfprint10.to_string(index=False))
    print(dfprint10)
    print(texttranslate("共找到披露净值信息的开放式基金数量:"),len(dfprint),'\b. ',end='')
    print(texttranslate("基金类型:"),fund_type)
    
    print(texttranslate("净值日期:"),nvdate,'\b. ',end='')
    import datetime
    today = datetime.date.today()
    print(texttranslate("数据来源：东方财富/天天基金,"),today)        
    
    return df

if __name__=='__main__':
     df=oef_rank_china(info_type='单位净值')
     df=oef_rank_china(info_type='累计净值')
     df=oef_rank_china(info_type='手续费')

#==============================================================================
if __name__=='__main__':
    fund='000592'
    fromdate='2020-7-1'
    todate='2020-9-30'
    trend_type='收益率'
    power=5
    twinx=False
    zeroline=False

def oef_trend_china(fund,fromdate,todate,trend_type='净值',power=0):
    """
    功能：开放式基金业绩趋势，单位净值，累计净值，近三个月收益率，同类排名，总排名
    """
    #检查走势类型
    trendlist=["净值","收益率","排名"]
    if trend_type not in trendlist:
        print("  #Error(oef_trend_china): unsupported trend type:",trend_type)
        print("  Supported trend types:",trendlist)
        return None
    
    #检查日期
    result,start,end=check_period(fromdate,todate)
    if not result:
        print("  #Error(oef_trend_china): invalid date period:",fromdate,todate)
        return None
    """
    #转换日期格式
    import datetime
    startdate=datetime.datetime.strftime(start,"%Y-%m-%d")
    enddate=str(datetime.datetime.strftime(end,"%Y-%m-%d"))
    """
    print("Searching for open-ended fund (OEF) trend info in China ...")
    import akshare as ak   

    #开放式基金-历史数据
    import datetime; today = datetime.date.today()
    source=texttranslate("数据来源：东方财富/天天基金")

    
    #绘制单位/累计净值对比图
    if trend_type == '净值':
        df1 = ak.fund_em_open_fund_info(fund=fund, indicator="单位净值走势")
        df1.rename(columns={'x':'date','y':'单位净值'}, inplace=True)
        df1['日期']=df1['date']
        df1.set_index(['date'],inplace=True) 
        
        df2 = ak.fund_em_open_fund_info(fund=fund, indicator="累计净值走势")
        df2.rename(columns={'x':'date','y':'累计净值'}, inplace=True)
        df2.set_index(['date'],inplace=True)       
        
        #合并
        import pandas as pd
        df = pd.merge(df1,df2,left_index=True,right_index=True,how='inner')
        dfp=df[(df['日期'] >= start)]
        dfp=dfp[(dfp['日期'] <= end)]
        if len(dfp) == 0:
            print("  #Error(oef_trend_china): no info found for",fund,"in the period:",fromdate,todate)
            return
        
        #绘制双线图
        ticker1=fund; colname1='单位净值';label1=texttranslate('单位净值')
        ticker2=fund; colname2='累计净值';label2=texttranslate('累计净值')
        #ylabeltxt='人民币元'
        ylabeltxt=texttranslate('净值')
        titletxt=texttranslate("开放式基金的净值趋势：")+codetranslate(fund)
        
        footnote=source+', '+str(today)
        plot_line2(dfp,ticker1,colname1,label1, \
               dfp,ticker2,colname2,label2, \
               ylabeltxt,titletxt,footnote,power=power)
        return df
    
    #绘制累计收益率单线图
    if trend_type == '收益率':
        df = ak.fund_em_open_fund_info(fund=fund, indicator="累计收益率走势")
        df.rename(columns={'x':'date','y':'累计收益率'}, inplace=True)
        df['日期']=df['date']
        df.set_index(['date'],inplace=True) 
        dfp=df[(df['日期'] >= start)]
        dfp=dfp[(dfp['日期'] <= end)]  
        if len(dfp) == 0:
            print("  #Error(oef_trend_china): no info found for",fund,"in the period:",fromdate,todate)
            return        
    
        colname='累计收益率'; collabel=texttranslate('累计收益率%')
        ylabeltxt=texttranslate('收益率%')
        titletxt=texttranslate("开放式基金的累计收益率趋势：")+codetranslate(fund)
        footnote=source+', '+str(today)
        plot_line(dfp,colname,collabel,ylabeltxt,titletxt,footnote,power=power)    
        return df
    
    #绘制同类排名图：近三个月收益率
    if trend_type == '排名':
        df1 = ak.fund_em_open_fund_info(fund=fund, indicator="同类排名走势")
        df1.rename(columns={'x':'date','y':'同类排名','sc':'总排名'}, inplace=True)
        df1['日期']=df1['date']
        df1.set_index(['date'],inplace=True) 
        
        df2 = ak.fund_em_open_fund_info(fund=fund, indicator="同类排名百分比")
        df2.rename(columns={'x':'date','y':'同类排名百分比'}, inplace=True)
        df2.set_index(['date'],inplace=True)       
        
        #合并
        import pandas as pd
        df = pd.merge(df1,df2,left_index=True,right_index=True,how='inner')
        dfp=df[(df['日期'] >= start)]
        dfp=dfp[(dfp['日期'] <= end)]
        if len(dfp) == 0:
            print("  #Error(oef_trend_china): no info found for",fund,"in the period:",fromdate,todate)
            return        

        #绘制双线图：同类排名
        ticker1=fund; colname1='同类排名';label1=texttranslate('同类排名')
        ticker2=fund; colname2='同类排名百分比';label2=texttranslate('同类排名百分比')
        ylabeltxt=''
        titletxt=texttranslate("开放式基金的近三个月收益率排名趋势：")+codetranslate(fund)
        footnote=source+', '+str(today)
        plot_line2(dfp,ticker1,colname1,label1, \
               dfp,ticker2,colname2,label2, \
               ylabeltxt,titletxt,footnote,power=power,twinx=True)
        
        #    
        ticker2=fund; colname2='总排名';label2=texttranslate('开放式基金总排名')    
        plot_line2(dfp,ticker1,colname1,label1, \
               dfp,ticker2,colname2,label2, \
               ylabeltxt,titletxt,footnote,power=power,twinx=True)            
        
        return df
    
#==============================================================================
if __name__=='__main__':
    pass

def mmf_rank_china(rank=10):
    """
    功能：中国货币型基金排名，7日年化收益率%
    """
    
    print("Searching for money market fund (OEF) information in China ...")
    import akshare as ak   
    
    #获取货币型基金实时信息
    df = ak.fund_em_money_fund_daily()
    collist=list(df)
    nvname=collist[6]
    nvdate=nvname[:10]
    #修改列名
    df.rename(columns={nvname:'7日年化%'}, inplace=True) 
    #dfa=df.drop(df[df['7日年化%']==''].index)
    dfb=df[['基金代码','基金简称','7日年化%','成立日期','基金经理','手续费']]
    
    dfb.sort_values(by=['7日年化%'],ascending=False,inplace=True)
    dfprint=dfb[['基金简称','基金代码','7日年化%','基金经理','手续费']]
    print(texttranslate("\n======= 中国货币型基金排名：7日年化收益率 ======="))
        
    #设置打印对齐
    import pandas as pd
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    
    dfprint.dropna(inplace=True)
    dfprint.reset_index(drop=True,inplace=True)
    if rank >=0:
        dfprint10=dfprint.head(rank)
    else:
        dfprint10=dfprint.tail(-rank)
    #print(dfprint10.to_string(index=False))
    print(dfprint10)
    print(texttranslate("共找到披露收益率信息的货币型基金数量:"),len(dfprint))
    
    print(texttranslate("收益率日期:"),nvdate,'\b. ',end='')    
    import datetime
    today = datetime.date.today()
    print(texttranslate("数据来源：东方财富/天天基金,"),today)        
    
    return df

if __name__=='__main__':
     df=mmf_rank_china()

#==============================================================================
if __name__=='__main__':
    fund='320019'
    fromdate='2020-1-1'
    todate='2020-10-16'
    power=0

def mmf_trend_china(fund,fromdate,todate,power=0):
    """
    功能：货币型基金业绩趋势，7日年化收益率
    """
    
    #检查日期
    result,start,end=check_period(fromdate,todate)
    if not result:
        print("  #Error(mmf_trend_china): invalid date period:",fromdate,todate)
        return None
    import datetime
    startdate=datetime.datetime.strftime(start,"%Y-%m-%d")
    enddate=str(datetime.datetime.strftime(end,"%Y-%m-%d"))
    
    print("Searching for money market fund (MMF) trend info in China ...")
    import akshare as ak   

    #基金历史数据
    import datetime; today = datetime.date.today()
    source=texttranslate("数据来源：东方财富/天天基金")

    
    #绘制收益率单线图
    df = ak.fund_em_money_fund_info(fund)
    df.sort_values(by=['净值日期'],ascending=True,inplace=True)
    df['7日年化%']=df['7日年化收益率'].astype("float")
    
    import pandas as pd
    df['date']=pd.to_datetime(df['净值日期'])
    df.set_index(['date'],inplace=True) 
    
    dfp = df[(df.index >= startdate)]
    dfp = dfp[(dfp.index <= enddate)]    
    if len(dfp) == 0:
        print("  #Error(mmf_trend_china): no info found for",fund,"in the period:",fromdate,todate)
        return    
    
    colname='7日年化%'; collabel=texttranslate('7日年化%')
    ylabeltxt=''
    titletxt=texttranslate("货币型基金的7日年化收益率趋势：")+codetranslate(fund)
    footnote=source+', '+str(today)
    plot_line(dfp,colname,collabel,ylabeltxt,titletxt,footnote,power=power)    
    
    return df
    
#==============================================================================
if __name__=='__main__':
    info_type='单位净值'
    fund_type='全部类型'

def etf_rank_china(info_type='单位净值',fund_type='全部类型',rank=10):
    """
    功能：中国ETF基金排名，单位净值，累计净值，手续费
    """
    typelist=['单位净值','累计净值','市价']
    if info_type not in typelist:
        print("  #Error(etf_rank_china): unsupported info type",info_type)
        print("  Supported info type:",typelist)
        return None
    
    print("Searching for exchange traded fund (ETF) information in China ...")
    import akshare as ak   
    
    #获取ETF基金实时信息
    df1 = ak.fund_em_etf_fund_daily()
    #删除全部为空值'---'的列
    df1t=df1.T
    df1t['idx']=df1t.index
    df1t.drop_duplicates(subset=['idx'],keep='last',inplace=True)
    df2=df1t.T
    #删除空值'---'的列
    
    #提取净值日期
    collist=list(df2)
    nvname1=collist[3]
    nvdate=nvname1[:10]
    nvname2=collist[4]
    #修改列名
    df=df2.rename(columns={nvname1:'单位净值',nvname2:'累计净值'}) 
    
    #过滤基金类型
    if fund_type != '全部类型':
        fundtypelist=list(set(list(df['类型'])))
        found=False
        for ft in fundtypelist:
            if fund_type in ft: 
                found=True
                break
        if not found:
            print("  #Error(etf_rank_china): unsupported fund type",fund_type)
            print("  Supported fund type:",fundtypelist)
            return None
        fund_filter=lambda x: fund_type in x
        df['基金类型s']=df['类型'].apply(fund_filter)
        df=df[df['基金类型s']==True]     
    
    if info_type == '单位净值':
        df.sort_values(by=['单位净值'],ascending=False,inplace=True)
        dfprint=df[['基金简称','基金代码','类型','单位净值','累计净值','市价']]
        print(texttranslate("\n===== 中国ETF基金排名：单位净值 ====="))
    
    if info_type == '累计净值':
        df.sort_values(by=['累计净值'],ascending=False,inplace=True)
        dfprint=df[['基金简称','基金代码','类型','累计净值','单位净值','市价']]
        print(texttranslate("\n===== 中国ETF基金排名：累计净值 ====="))        
    
    if info_type == '市价':
        df.sort_values(by=['市价'],ascending=False,inplace=True)
        dfprint=df[['基金简称','基金代码','类型','市价','累计净值','单位净值']]
        print(texttranslate("\n===== 中国ETF基金排名：市价 ====="))          
        
    #设置打印对齐
    import pandas as pd
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    
    dfprint.dropna(inplace=True)
    dfprint.reset_index(drop=True,inplace=True)
    if rank >=0:
        dfprint10=dfprint.head(rank)
    else:
        dfprint10=dfprint.tail(-rank)
    #print(dfprint10.to_string(index=False))
    print(dfprint10)
    print(texttranslate("共找到披露净值信息的ETF基金数量:"),len(dfprint),'\b. ',end='')
    print(texttranslate("基金类型:"),fund_type)
    
    print(texttranslate("净值日期:"),nvdate,'\b. ',end='')
    import datetime
    today = datetime.date.today()
    print(texttranslate("数据来源：东方财富/天天基金,"),today)        
    
    return df

if __name__=='__main__':
     df=etf_rank_china(info_type='单位净值',fund_type='全部类型')
     df=etf_rank_china(info_type='累计净值')
     df=etf_rank_china(info_type='市价')

#==============================================================================
if __name__=='__main__':
    fund='159922'
    fromdate='2020-1-1'
    todate='2020-10-16'

def etf_trend_china(fund,fromdate,todate):
    """
    功能：ETF基金业绩趋势，单位净值，累计净值
    """
    #检查日期
    result,start,end=check_period(fromdate,todate)
    if not result:
        print("  #Error(oef_trend_china): invalid date period:",fromdate,todate)
        return None
    #转换日期格式
    import datetime
    startdate=datetime.datetime.strftime(start,"%Y-%m-%d")
    enddate=str(datetime.datetime.strftime(end,"%Y-%m-%d"))

    print("Searching for exchange traded fund (ETF) trend info in China ...")
    import akshare as ak   

    import datetime; today = datetime.date.today()
    source=texttranslate("数据来源：东方财富/天天基金")

    
    #绘制单位/累计净值对比图
    df = etf_hist_df = ak.fund_em_etf_fund_info(fund)
    import pandas as pd
    df['date']=pd.to_datetime(df['净值日期'])
    df.set_index(['date'],inplace=True) 
    df['单位净值']=df['单位净值'].astype("float")
    df['累计净值']=df['累计净值'].astype("float")
        
    dfp=df[(df['净值日期'] >= startdate)]
    dfp=dfp[(dfp['净值日期'] <= enddate)]
    if len(dfp) == 0:
        print("  #Error(etf_trend_china): no info found for",fund,"in the period:",fromdate,todate)
        return    
        
    #绘制双线图
    ticker1=fund; colname1='单位净值';label1=texttranslate('单位净值')
    ticker2=fund; colname2='累计净值';label2=texttranslate('累计净值')
    ylabeltxt=texttranslate('人民币元')
    titletxt=texttranslate("ETF基金的净值趋势：")+codetranslate(fund)
    footnote=source+', '+str(today)
    
    plot_line2(dfp,ticker1,colname1,label1, \
               dfp,ticker2,colname2,label2, \
               ylabeltxt,titletxt,footnote)
    
    return df
    
if __name__=='__main__':
    df=etf_trend_china('510580','2019-1-1','2020-9-30')
    
#==============================================================================

def fund_summary_china():
    """
    功能：中国基金投资机构概况
    爬虫来源地址：https://zhuanlan.zhihu.com/p/97487003
    """
    print("Searching for fund investment institutions in China ...")
    import akshare as ak

    #会员机构综合查询：
    #机构类型：'商业银行','支付结算机构','证券公司资管子公司','会计师事务所',
    #'保险公司子公司','独立服务机构','证券投资咨询机构','证券公司私募基金子公司',
    #'私募基金管理人','公募基金管理公司','地方自律组织','境外机构','期货公司',
    #'独立第三方销售机构','律师事务所','证券公司','其他机构','公募基金管理公司子公司',
    #'期货公司资管子公司','保险公司'
    amac_member_info_df = ak.amac_member_info()
        
    typelist=['公募基金管理公司','公募基金管理公司子公司','私募基金管理人', \
                '期货公司','期货公司资管子公司','证券公司', \
                '证券公司私募基金子公司','证券公司资管子公司','境外机构']
    maxlen=0
    for t in typelist:
        tlen=strlen(t)
        if tlen > maxlen: maxlen=tlen
    maxlen=maxlen+1
        
    print(texttranslate("\n===== 中国基金投资机构概况 ====="))
    print(texttranslate("机构（会员）数量："),end='')
    num=len(list(set(list(amac_member_info_df["机构（会员）名称"]))))
    print("{:,}".format(num))
        
    print(texttranslate("其中包括："))
    for t in typelist:
        tlen=strlen(t)
        df_sub=amac_member_info_df[amac_member_info_df['机构类型']==t]
        n=len(list(set(list(df_sub['机构（会员）名称']))))
        prefix=' '*4+t+' '*(maxlen-tlen)+':'
        print(prefix,"{:,}".format(n),"\b,",round(n/num*100,2),'\b%')       
        
    import datetime; today = datetime.date.today()
    source=texttranslate("数据来源：中国证券投资基金业协会")
    footnote=source+', '+str(today)  
    print(footnote)
        
    print(texttranslate("\n===== 中国基金投资机构会员代表概况 ====="))
    print(texttranslate("会员代表人数："),end='')
    num=len(list(set(list(amac_member_info_df["会员代表"]))))
    print("{:,}".format(num))        
        
    print(texttranslate("其中工作在："))
    for t in typelist:
        tlen=strlen(t)
        df_sub=amac_member_info_df[amac_member_info_df['机构类型']==t]
        n=len(list(set(list(df_sub['会员代表']))))
        prefix=' '*4+t+' '*(maxlen-tlen)+':'
        print(prefix,"{:,}".format(n),"\b,",round(n/num*100,2),'\b%')  
    print(footnote)        
    
    return amac_member_info_df


#==============================================================================
if __name__=='__main__':
    location='全国'

def pef_manager_china(location='全国'):
    """
    功能：中国私募基金管理人地域分布概况
    爬虫来源地址：https://zhuanlan.zhihu.com/p/97487003
    """
    
    print("Searching for private equity fund (PEF) managers info in China ...")
    import akshare as ak
    import pandas as pd

    #私募基金管理人综合查询
    manager_df = ak.amac_manager_info()
    num=len(list(manager_df["法定代表人/执行事务合伙人(委派代表)姓名"]))
    
    #注册地检查
    if location != '全国':
        typelist=sort_pinyin(list(set(list(manager_df['注册地']))))
        typelist.remove('')
        if location not in typelist:
            print("  #Error(pef_manager_china): failed to find registration place-"+location)
            print("  Supported registration place：",typelist+['全国'])
            return

    #设置打印对齐
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)

    import datetime; today = datetime.date.today()
    source=texttranslate("数据来源：中国证券投资基金业协会")
    footnote=source+', '+str(today)          
    
    if location != '全国':
        manager_df=manager_df[manager_df['注册地']==location]
        print(texttranslate("\n===== 中国私募基金管理人角色分布 ====="))
        print(texttranslate("地域：")+location)
        print(texttranslate("法定代表人/执行合伙人数量："),end='')
        num1=len(list(manager_df["法定代表人/执行事务合伙人(委派代表)姓名"]))
        print("{:,}".format(num1),texttranslate('\b, 占比全国'),round(num1/num*100.0,2),'\b%')
        
        print(texttranslate("其中, 角色分布："))
        #instlist=list(set(list(manager_df['机构类型'])))
        instlist=['私募股权、创业投资基金管理人','私募证券投资基金管理人','私募资产配置类管理人','其他私募投资基金管理人']
        mtype=pd.DataFrame(columns=['管理人类型','人数','占比%'])
        for t in instlist:
            df_sub=manager_df[manager_df['机构类型']==t]
            n=len(list(df_sub['法定代表人/执行事务合伙人(委派代表)姓名']))
            pct=round(n/num1*100,2)
            s=pd.Series({'管理人类型':t,'人数':n,'占比%':pct})
            mtype=mtype.append(s,ignore_index=True) 
        mtype.sort_values(by=['人数'],ascending=False,inplace=True)
        mtype.reset_index(drop=True,inplace=True)        
        
        print(mtype)
        print(footnote)
        return manager_df
    
    print(texttranslate("\n== 中国私募基金管理人地域分布概况 =="))
    print(texttranslate("法定代表人/执行合伙人数量："),end='')
    num=len(list(manager_df["法定代表人/执行事务合伙人(委派代表)姓名"]))
    print("{:,}".format(num))  
        
    typelist=sort_pinyin(list(set(list(manager_df['注册地']))))
    typelist.remove('')
        
    print(texttranslate("其中分布在："))
    location=pd.DataFrame(columns=['注册地','人数','占比%'])
    for t in typelist:
        df_sub=manager_df[manager_df['注册地']==t]
        n=len(list(df_sub['法定代表人/执行事务合伙人(委派代表)姓名']))
        pct=round(n/num*100,2)
        s=pd.Series({'注册地':t,'人数':n,'占比%':pct})
        location=location.append(s,ignore_index=True) 
    location.sort_values(by=['人数'],ascending=False,inplace=True)
        
    location.reset_index(drop=True,inplace=True)
    location10=location.head(10)
    pctsum=round(location10['占比%'].sum(),2)
    
    print(location10)
    print(texttranslate("上述地区总计占比:"),pctsum,'\b%')
    print(footnote)             
    
    """
    print("\n===== 中国私募基金管理人角色分布 =====")
    print("地域："+location)
    print("法定代表人/执行合伙人数量：",end='')
    num1=len(list(manager_df["法定代表人/执行事务合伙人(委派代表)姓名"]))
    print("{:,}".format(num1),'\b, 占比全国',round(num1/num*100.0,2),'\b%')
        
    print("其中, 角色分布：")
    #instlist=list(set(list(manager_df['机构类型'])))
    instlist=['私募股权、创业投资基金管理人','私募证券投资基金管理人','私募资产配置类管理人','其他私募投资基金管理人']
    mtype=pd.DataFrame(columns=['管理人类型','人数','占比%'])
    for t in instlist:
        df_sub=manager_df[manager_df['机构类型']==t]
        n=len(list(df_sub['法定代表人/执行事务合伙人(委派代表)姓名']))
        pct=round(n/num1*100,2)
        s=pd.Series({'管理人类型':t,'人数':n,'占比%':pct})
        mtype=mtype.append(s,ignore_index=True) 
    mtype.sort_values(by=['人数'],ascending=False,inplace=True)
    mtype.reset_index(drop=True,inplace=True)        
        
    print(mtype)
    print(footnote)
    """
    
    return manager_df


#==============================================================================

def pef_product_china():
    
    """
    功能：中国私募基金管理人的产品管理概况
    爬虫来源地址：https://zhuanlan.zhihu.com/p/97487003
    """
    print("Searching for private equity fund (PEF) products info in China ...")
    import akshare as ak
    import pandas as pd

    #私募基金管理人基金产品
    product_df = ak.amac_fund_info()
    
    print(texttranslate("\n== 中国私募基金管理人的产品与运营概况 =="))
    print(texttranslate("产品数量："),end='')
    num=len(list(product_df["基金名称"]))
    print("{:,}".format(num))  
        
    #管理类型
    print(texttranslate("产品的运营方式分布："))
    #typelist=list(set(list(product_df['私募基金管理人类型'])))
    typelist=['受托管理','顾问管理','自我管理']
    for t in typelist:
            df_sub=product_df[product_df['私募基金管理人类型']==t]
            n=len(list(set(list(df_sub['基金名称']))))
            prefix=' '*4+t+':'
            print(prefix,"{:,}".format(n),"\b,",round(n/num*100,2),'\b%')     
        
    #运行状态
    print(texttranslate("产品的运营状态分布："))
    """
    typelist=list(set(list(product_df['运行状态'])))
    typelist=['状态不明' if i =='' else i for i in typelist]
    """
    typelist=['正在运作','提前清算','正常清算','延期清算','投顾协议已终止','']
    maxlen=0
    for t in typelist:
            tlen=strlen(t)
            if tlen > maxlen: maxlen=tlen
    maxlen=maxlen+1 
        
    for t in typelist:
            df_sub=product_df[product_df['运行状态']==t]
            n=len(list(set(list(df_sub['基金名称']))))
            if t =='': t='状态不明'
            tlen=strlen(t)
            prefix=' '*4+t+' '*(maxlen-tlen)+':'
            print(prefix,"{:,}".format(n),"\b,",round(n/num*100,2),'\b%')      

    import datetime; today = datetime.date.today()
    source=texttranslate("数据来源：中国证券投资基金业协会")
    footnote=source+', '+str(today)       
    print(footnote)
        
    #推出产品数量排行
    print(texttranslate("\n===== 中国推出产品数量最多的私募基金管理人 ====="))
    subttl=pd.DataFrame(product_df.groupby(by=['私募基金管理人名称'])['基金名称'].count())
    subttl.rename(columns={'基金名称':'产品数量'}, inplace=True)
    subttl['占比‰']=round(subttl['产品数量']/num*1000.0,2)
    subttl.sort_values(by=['产品数量'],ascending=False,inplace=True)
    subttl.reset_index(inplace=True)
    subttl10=subttl.head(10)
        
    #设置打印对齐
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    
    print(subttl10)
    
    pctsum=round(subttl10['占比‰'].sum(),2)    
    print(texttranslate("上述产品总计占比:"),pctsum,'\b‰')     
    print(footnote)
        
    print(texttranslate("\n===== 中国私募基金管理人的产品托管概况 ====="))
    #托管产品数量排行
    tnum=len(list(set(list(product_df['托管人名称']))))
    print(texttranslate("托管机构数量:"),"{:,}".format(tnum))
    
    subttl=pd.DataFrame(product_df.groupby(by=['托管人名称'])['基金名称'].count())
    subttl.rename(columns={'基金名称':'产品数量'}, inplace=True)
    subttl.sort_values(by=['产品数量'],ascending=False,inplace=True)
    subttl.reset_index(inplace=True)
        
    subttl=subttl[subttl['托管人名称']!='']
    #subttl.drop(subttl.index[0], inplace=True)       # 删除第1行
    subttl.reset_index(drop=True,inplace=True)
    subttl['占比%']=round(subttl['产品数量']/num*100.0,2)
    subttl10=subttl.head(10)
        
    pctsum=round(subttl10['占比%'].sum(),2)
    print(subttl10)
    print(texttranslate("上述金融机构托管产品总计占比:"),pctsum,'\b%')
    print(footnote)     
        
    return product_df   


#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#以下信息专注于中国内地基金信息，来源于akshare，尚未利用
#==============================================================================
def fund_info_china():
    
    #证券公司集合资管产品
    cam_df = ak.amac_securities_info()
    
    #证券公司直投基金：
    #中国证券投资基金业协会-信息公示-私募基金管理人公示-基金产品公示-证券公司直投基金
    sdif_df = ak.amac_aoin_info()
    
    #证券公司私募投资基金
    speif_df = ak.amac_fund_sub_info()
    
    #证券公司私募基金子公司管理人信息
    spesub_manager_df = ak.amac_member_sub_info()
    
    #基金公司及子公司集合资管产品
    #中国证券投资基金业协会-信息公示-私募基金管理人公示-基金产品公示-基金公司及子公司集合资管产品
    sscam_df = ak.amac_fund_account_info()
    
    #期货公司集合资管产品
    #中国证券投资基金业协会-信息公示-私募基金管理人公示-基金产品公示-期货公司集合资管产品
    fccam_df = ak.amac_futures_info()
    
    #==========================================================================
    #以下为公募数据：
    
    #基金净值估算数据，当前获取在交易日的所有基金的净值估算数据
    #爬虫来源：https://zhuanlan.zhihu.com/p/140478554?from_voters_page=true
    #信息内容：基金代码，基金类型，单位净值，基金名称
    fnve_df = ak.fund_em_value_estimation()
    
    #挑选QDII产品
    fnve_list=list(set(list(fnve_df['基金类型'])))
    qdii=lambda x: True if 'QDII' in x else False
    fnve_df['is_QDII']=fnve_df['基金类型'].apply(qdii)
    fnve_qdii_df=fnve_df[fnve_df['is_QDII']==True]
    
    #基金持股：获取个股的基金持股数据
    #爬虫来源：https://my.oschina.net/akshare/blog/4428824
    #持股的基金类型：symbol="基金持仓"; choice of {"基金持仓", "QFII持仓", "社保持仓", "券商持仓", "保险持仓", "信托持仓"}
    #返回：单次返回指定 symbol 和 date 的所有历史数据
    df = ak.stock_report_fund_hold(symbol="基金持仓", date="20200630")
    
    ###Fama-French三因子回归A股实证（附源码）
    #代码来源：https://mp.weixin.qq.com/s?__biz=MzU5NDY0NDM2NA==&mid=2247486057&idx=1&sn=0fb3f8558da4e55789ce340c03b648cc&chksm=fe7f568ac908df9c22bae8b52207633984ec91ef7b2728eea8c6a75089b8f2db284e3d611775&scene=21#wechat_redirect

    ###Carhart四因子模型A股实证（附源码）
    #代码来源：https://my.oschina.net/akshare/blog/4340998
    
    #==========================================================================
    ###其他公募基金实时/历史行情
    #爬虫来源：https://cloud.tencent.com/developer/article/1624480
    
    ###########XXX理财型基金-实时数据
    #基金代码，基金简称，当前交易日-7日年化收益率，封闭期，申购状态
    wmf_df = ak.fund_em_financial_fund_daily()
    #理财型基金-历史数据
    #净值日期，7日年化收益率，申购状态，赎回状态
    wmf_hist_df = ak.fund_em_financial_fund_info(fund="000134")
    
    ###########分级基金(结构化基金)-实时数据
    #基金代码，基金简称，单位净值，累计净值，市价，折价率，手续费
    gsf_df = ak.fund_em_graded_fund_daily()
    #分级基金-历史数据
    #净值日期，7日年化收益率，申购状态，赎回状态
    gsf_hist_df = ak.fund_em_graded_fund_info(fund="150232")
    
    ###抓取沪深股市所有指数关联的公募基金列表（含ETF、增强、分级等）
    #代码来源：https://blog.csdn.net/leeleilei/article/details/106124894
    
    ###pyecharts绘制可伸缩蜡烛图
    #代码地址：https://segmentfault.com/a/1190000021999451?utm_source=sf-related
    
#==============================================================================



























