# -*- coding: utf-8 -*-
"""
版权：王德宏，北京外国语大学国际商学院
功能：Fama-French股票市场资产定价因子（不包括单独的中国大陆市场）
版本：2.1，2019-10-10
"""
#==============================================================================
#关闭所有警告
import warnings; warnings.filterwarnings('ignore')
from siat.common import *
from siat.translate import *
from siat.security_prices import *
#==============================================================================
import matplotlib.pyplot as plt

#处理绘图汉字乱码问题
import sys; czxt=sys.platform
if czxt in ['win32','win64']:
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置默认字体
    mpfrc={'font.family': 'SimHei'}

if czxt in ['darwin']: #MacOSX
    plt.rcParams['font.family']= ['Heiti TC']
    mpfrc={'font.family': 'Heiti TC'}

if czxt in ['linux']: #website Jupyter
    plt.rcParams['font.family']= ['Heiti TC']
    mpfrc={'font.family':'Heiti TC'}

# 解决保存图像时'-'显示为方块的问题
plt.rcParams['axes.unicode_minus'] = False 
#==============================================================================
def get_ff_factors(start,end,scope='US',factor='FF3',freq='yearly'):
   """
   【支持的因子种类(factor)】
   FF3: FF3各个因子
   FF5: FF5各个因子
   Mom: 动量因子
   ST_Rev: 短期反转因子
   LT_Rev: 长期反转因子

   【支持的国家/地区(scope)】
   US: 美国
   North_America：北美(美国+加拿大)
   Global: 全球
   Global_ex_US: 全球(除美国外)
   Asia_Pacific_ex_Japan: 亚太(除日本外)，拟作近似中国
   Japan: 日本
   Europe: 欧洲

   【支持的取样频率(freq)】
   yearly: 年
   monthly: 月
   weekly: 周(仅支持美国FF3)
   daily: 日
   """
    
   import pandas as pd
   s=pd.DataFrame([
        ['US','FF3','monthly','F-F_Research_Data_Factors',0],
        ['US','FF3','yearly','F-F_Research_Data_Factors',1],
        ['US','FF3','weekly','F-F_Research_Data_Factors_weekly',0],
        ['US','FF3','daily','F-F_Research_Data_Factors_daily',0],
        ['US','FF5','monthly','F-F_Research_Data_5_Factors_2x3',0],
        ['US','FF5','yearly','F-F_Research_Data_5_Factors_2x3',1],
        ['US','FF5','daily','F-F_Research_Data_5_Factors_2x3_daily',0],  
        ['US','Mom','monthly','F-F_Momentum_Factor',0],
        ['US','Mom','yearly','F-F_Momentum_Factor',1],
        ['US','Mom','daily','F-F_Momentum_Factor_daily',0],  
        ['US','ST_Rev','monthly','F-F_ST_Reversal_Factor',0],
        ['US','ST_Rev','yearly','F-F_ST_Reversal_Factor',1],
        ['US','ST_Rev','daily','F-F_ST_Reversal_Factor_daily',0],    
        ['US','LT_Rev','monthly','F-F_LT_Reversal_Factor',0],
        ['US','LT_Rev','yearly','F-F_LT_Reversal_Factor',1],
        ['US','LT_Rev','daily','F-F_LT_Reversal_Factor_daily',0],   \
        
        ['Global','FF3','monthly','Global_3_Factors',0],
        ['Global','FF3','yearly','Global_3_Factors',1],
        ['Global','FF3','daily','Global_3_Factors_Daily',0],   
        ['Global_ex_US','FF3','monthly','Global_ex_US_3_Factors',0],
        ['Global_ex_US','FF3','yearly','Global_ex_US_3_Factors',1],
        ['Global_ex_US','FF3','daily','Global_ex_US_3_Factors_Daily',0],  
        ['Europe','FF3','monthly','Europe_3_Factors',0],
        ['Europe','FF3','yearly','Europe_3_Factors',1],
        ['Europe','FF3','daily','Europe_3_Factors_Daily',0],  
        ['Japan','FF3','monthly','Japan_3_Factors',0],
        ['Japan','FF3','yearly','Japan_3_Factors',1],
        ['Japan','FF3','daily','Japan_3_Factors_Daily',0],    
        ['Asia_Pacific_ex_Japan','FF3','monthly','Asia_Pacific_ex_Japan_3_Factors',0],
        ['Asia_Pacific_ex_Japan','FF3','yearly','Asia_Pacific_ex_Japan_3_Factors',1],
        ['Asia_Pacific_ex_Japan','FF3','daily','Asia_Pacific_ex_Japan_3_Factors_Daily',0],   
        ['North_America','FF3','monthly','North_America_3_Factors',0],
        ['North_America','FF3','yearly','North_America_3_Factors',1],
        ['North_America','FF3','daily','North_America_3_Factors_Daily',0], \
         
        ['Global','FF5','monthly','Global_5_Factors',0],
        ['Global','FF5','yearly','Global_5_Factors',1],
        ['Global','FF5','daily','Global_5_Factors_Daily',0],   
        ['Global_ex_US','FF5','monthly','Global_ex_US_5_Factors',0],
        ['Global_ex_US','FF5','yearly','Global_ex_US_5_Factors',1],
        ['Global_ex_US','FF5','daily','Global_ex_US_5_Factors_Daily',0],  
        ['Europe','FF5','monthly','Europe_5_Factors',0],
        ['Europe','FF5','yearly','Europe_5_Factors',1],
        ['Europe','FF5','daily','Europe_5_Factors_Daily',0],  
        ['Japan','FF5','monthly','Japan_5_Factors',0],
        ['Japan','FF5','yearly','Japan_5_Factors',1],
        ['Japan','FF5','daily','Japan_5_Factors_Daily',0],    
        ['Asia_Pacific_ex_Japan','FF5','monthly','Asia_Pacific_ex_Japan_5_Factors',0],
        ['Asia_Pacific_ex_Japan','FF5','yearly','Asia_Pacific_ex_Japan_5_Factors',1],
        ['Asia_Pacific_ex_Japan','FF5','daily','Asia_Pacific_ex_Japan_5_Factors_Daily',0],   
        ['North_America','FF5','monthly','North_America_5_Factors',0],
        ['North_America','FF5','yearly','North_America_5_Factors',1],
        ['North_America','FF5','daily','North_America_5_Factors_Daily',0], \

        ['Global','Mom','monthly','Global_Mom_Factor',0],
        ['Global','Mom','yearly','Global_Mom_Factor',1],
        ['Global','Mom','daily','Global_Mom_Factor_Daily',0],   
        ['Global_ex_US','Mom','monthly','Global_ex_US_Mom_Factor',0],
        ['Global_ex_US','Mom','yearly','Global_ex_US_Mom_Factor',1],
        ['Global_ex_US','Mom','daily','Global_ex_US_Mom_Factor_Daily',0],  
        ['Europe','Mom','monthly','Europe_Mom_Factor',0],
        ['Europe','Mom','yearly','Europe_Mom_Factor',1],
        ['Europe','Mom','daily','Europe_Mom_Factor_Daily',0],  
        ['Japan','Mom','monthly','Japan_Mom_Factor',0],
        ['Japan','Mom','yearly','Japan_Mom_Factor',1],
        ['Japan','Mom','daily','Japan_Mom_Factor_Daily',0],    
        ['Asia_Pacific_ex_Japan','Mom','monthly','Asia_Pacific_ex_Japan_MOM_Factor',0],
        ['Asia_Pacific_ex_Japan','Mom','yearly','Asia_Pacific_ex_Japan_MOM_Factor',1],
        ['Asia_Pacific_ex_Japan','Mom','daily','Asia_Pacific_ex_Japan_MOM_Factor_Daily',0],   
        ['North_America','Mom','monthly','North_America_Mom_Factor',0],
        ['North_America','Mom','yearly','North_America_Mom_Factor',1],
        ['North_America','Mom','daily','North_America_Mom_Factor_Daily',0]                 
        ], columns=['scope','factor','freq','symbol','seq'])

   #数据源
   source='famafrench'
   if scope == "China":
       scope="Asia_Pacific_ex_Japan"
    
   #匹配：scope+factor+freq
   ss=s[s['scope'].isin([scope]) & s['factor'].isin([factor]) \
                                  & s['freq'].isin([freq])]  
   #如果未找到匹配的模式，显示信息后返回
   if len(ss)==0:
        print("Sorry, no data available for",scope,factor,freq)
        return None

   #重新索引，第1行的索引编号为0
   sss=ss.reset_index(drop=True)    
   #取出对应的symbol
   symbol=sss.iloc[0]['symbol']    
   #取出对应的月(0)/年(1)编号
   seq=sss.iloc[0]['seq']

   #抓取数据
   import pandas_datareader.data as web
   try:
        ds = web.DataReader(symbol, source, start, end)
   except:
        print("  Sorry, connection to data source failed for",symbol)        
        return None
    
   #提取希望的资产定价因子
   factor_df=ds[seq]
   if len(factor_df)==0:
        print("Sorry, no data available for",start,end,scope,factor,freq)
        #print("Tracing process:"s,ss,sss,symbol,seq,ds)
        return None    
    
   return factor_df

if __name__=='__main__':
    ff3_factors_us=get_ff_factors("01/01/2009","07/18/2019",scope='US', \
                                  factor='FF3',freq='yearly')

    ff3_factors_jp=get_ff_factors("01/01/2009","07/18/2019",scope='Japan', \
                                  factor='FF3',freq='yearly')

    ff3_factors_eu=get_ff_factors("2009-01-01","2019-07-18",scope='Europe', \
                                  factor='FF3',freq='yearly')



#==============================================================================
def get_ff3_factors(start,end,scope='US',freq='yearly'):    
    """
    功能：抓取Fama-French三因子模型的三个市场因子
    1）市场风险溢价(Rmarket-Rf，收益率风险溢价) 
    2）小市值风险溢价(SMB，规模因子，即小市值股票对比大市值股票的超额收益率)
    3）高市净率风险溢价(HML，价值因子，高溢价股票对比低溢价股票的超额收益率)
    
    输入参数：
    start/end：开始/结束日期，格式为YYYY-MM-DD或MM/DD/YYYY
    scope：地区(美国，日本，欧洲，全球，除美国外的全球，除日本外的亚太)
    freq：采样周期(日、周、月、年，其中周仅支持美国市场)
    输出：按照采样周期排列的指定地区的FF3因子(pandas格式)
    """
    
    #仅为测试用
    #start="2018-01-01"
    #end="2018-12-31"
    #scope='US'
    #freq='monthly'
    
    #抓取FF3因子
    factor='FF3'
    ff3_factors=get_ff_factors(start,end,scope,factor,freq)   
    
    return ff3_factors

if __name__=='__main__':
    factors=get_ff3_factors("2018-01-01","2018-12-31",scope='US', \
                                  freq='monthly')
    print("\n",factors)

#==============================================================================
def test_ff3_factors():
    """
    功能：交互式测试资产定价模型FF3的因子
    输入：用户输入
    显示：各个因子
    返回值：无
    """
    
    import easygui as g

    title="Test the Factors of Fama-French 3-factor Model"
    msg="Please fill in the information below"
    fldnames=["Start date (YYYY-MM-DD)","End date (YYYY-MM-DD)", \
          "Scope (US, China, Japan, Europe)", \
          "Frequency (yearly, monthly, daily)"]
    fldvalues=[]
    values=("2018-01-01","2019-04-30","US","monthly")
    fldvalues=g.multenterbox(msg,title=title,fields=fldnames,values=values)
    """
    如果用户输入的值比选项少的话，则返回列表中的值用空字符串填充用户为输入的选项。
    如果用户输入的值比选项多的话，则返回的列表中的值将截断为选项的数量。
    如果用户取消操作，则返回域中的列表的值或者None值
    """
    
    if fldvalues:
        start=fldvalues[0]
        end=fldvalues[1]
        scope=fldvalues[2]
        freq=fldvalues[3]
        
        ff_factors=get_ff3_factors(start,end,scope,freq)
        if ff_factors is None:
            g.msgbox(msg="Sorry, no factor data available under the condition.", \
                     title=title)                       
        else: 
            g.msgbox(msg=ff_factors,title=title)
    else:
        g.msgbox(msg="Sorry, user cancelled the operation, no data retrieved.", \
                 title=title)
        
    return

if __name__=='__main__':
    test_ff3_factors()        

#==============================================================================
def draw1_ff_factors(model,scope,factors,factor_type):    
    """
    功能：绘制单曲线的FF因子变化图
    输入参数：
    model: 模型类型, 任意字符串(例如FF3, FFC4, FF5)
    scope: 市场范围, 任意字符串(例如US, China, Europe)
    factors：包括FF各个因子的数据框
    factor_type：因子类型，严格限于RF/Mkt-RF/SMB/HML/MOM/RMW/CMA
    输出：图形
    返回值：无
    """
    #仅用作测试，完成后应注释掉
    #model="Fama-French 3-factor Model"
    #scope="US"
    #factor_type='ALL'
    
    if factor_type in ['Mkt-RF']:    
        #绘制市场收益率风险溢价变化图
        """
        线段的颜色：c='r'，红色
        线型：ls='-'，实线；':'则为虚线
        线段的粗细：lw=3
        节点形状：marker='o'，圆形
        节点大小：ms=10
        节点颜色：mfc='y'，黄色
        """
        try:
            factors.plot(y=['Mkt-RF'], \
                     c='r',ls='-',lw=3,marker='o',ms=10,mfc='y')
        except:
            print("Sorry, no MKT factor data available")
            return
        plt.axhline(y=0.0,color='b',linestyle=':')  #画0点虚线X轴做基准
        title1="\n"+model+": "+scope+", "+" Mkt-RF Factor"
        plt.title(title1,fontsize=12,fontweight='bold')
        plt.ylabel('Mkt-RF',fontsize=12,fontweight='bold')
        plt.xticks(factors.index,fontsize=8,rotation=45)
        plt.legend(loc='best')    
        plt.show()   
        
    if factor_type in ['SMB']:            
        #绘制规模因子变化图
        try:
            factors.plot(y=['SMB'], \
                     c='b',ls='-',lw=3,marker='o',ms=10,mfc='r')
        except:
            print("Sorry, no SMB factor data available")
            return
        plt.axhline(y=0.0,color='b',linestyle=':')
        title1="\n"+model+": "+scope+", "+"SMB Factor"
        plt.title(title1,fontsize=12,fontweight='bold')
        plt.ylabel('SMB',fontsize=12,fontweight='bold')
        plt.xticks(factors.index,fontsize=8,rotation=45)
        plt.legend(loc='best')
        plt.show()   

    if factor_type in ['HML']:     
        #绘制价值因子变化图
        try:
            factors.plot(y=['HML'], \
                     c='c',ls='-',lw=3,marker='o',ms=10,mfc='r')
        except:
            print("Sorry, no HML factor data available")
            return
        plt.axhline(y=0.0,color='b',linestyle=':')  #画一条0点的虚线做基准参考
        title1="\n"+model+": "+scope+", "+"HML Factor"
        plt.title(title1,fontsize=12,fontweight='bold')
        plt.ylabel('HML',fontsize=12,fontweight='bold')
        plt.xticks(factors.index,fontsize=8,rotation=45)
        plt.legend(loc='best')
        plt.show()   

    if factor_type in ['RF']:      
        #绘制无风险收益率变化图
        try:
            factors.plot(y=['RF'], \
                     c='g',ls='-',lw=3,marker='*',ms=14,mfc='r')
        except:
            print("Sorry, no RF data available")
            return
        title1="\n"+model+": "+scope+", "+"HML Factor"
        plt.title(title1,fontsize=12,fontweight='bold')
        plt.ylabel('RF %',fontsize=12,fontweight='bold')
        plt.xticks(factors.index,fontsize=8,rotation=45)
        plt.legend(loc='best')
        plt.show()  

    if factor_type in ['MOM']:         
        #绘制动量因子变化图
        try:
            factors.plot(y=['MOM'], \
                     c='deeppink',ls='-',lw=3,marker='*',ms=15,mfc='y')
        except:
            print("Sorry, no MOM factor data available")
            return
        plt.axhline(y=0.0,color='b',linestyle=':')
        title1="\n"+model+": "+scope+", "+"MOM Factor"
        plt.title(title1,fontsize=12,fontweight='bold')
        plt.ylabel('Mom',fontsize=12,fontweight='bold')
        plt.xticks(factors.index,fontsize=8)
        plt.legend(loc='best')
        plt.show()  


    if factor_type in ['RMW']:      
        #绘制盈利因子变化图
        try:
            factors.plot(y=['RMW'], \
                     c='blue',ls='-',lw=3,marker='*',ms=15,mfc='r')
        except:
            print("Sorry, no RMW factor data available")
            return        
        plt.axhline(y=0.0,color='b',linestyle=':')
        title1="\n"+model+": "+scope+", "+"RMW Factor"
        plt.title(title1,fontsize=12,fontweight='bold')
        plt.ylabel('RMW',fontsize=12,fontweight='bold')
        plt.xticks(factors.index,fontsize=8)
        plt.legend(loc='best')
        plt.show()  

    if factor_type in ['CMA']:          
        #绘制投资因子变化图
        try:
            factors.plot(y=['CMA'], \
                     c='black',ls='-',lw=3,marker='*',ms=15,mfc='r')
        except:
            print("Sorry, no CMA factor data available")
            return
        plt.axhline(y=0.0,color='b',linestyle=':')
        title1="\n"+model+": "+scope+", "+"CMA Factor"
        plt.title(title1,fontsize=12,fontweight='bold')
        plt.ylabel('CMA',fontsize=12,fontweight='bold')
        plt.xticks(factors.index,fontsize=8)
        plt.legend(loc='best')
        plt.show() 
    
    return


if __name__=='__main__':
    factors1=get_ff3_factors("2018-01-01","2018-12-31",scope='US', \
                                  freq='monthly')
    factors2=get_ff3_factors("2018-01-01","2018-12-31",scope='China', \
                                  freq='monthly')    
    draw1_ff_factors("FF3 model","US",factors1,"SMB")
    draw1_ff_factors("FF3 model","Japan",factors2,"SMB")

#==============================================================================
def draw2_ff_factors(model,scope1,scope2,factors1,factors2,factor_type):    
    """
    功能：绘制双曲线的FF因子变化图
    输入参数：
    model: 模型类型, 任意字符串(例如FF3, FFC4, FF5)
    scope: 市场范围, 任意字符串(例如US, China, Europe)
    factors1/2：用于对比的包括FF各个因子的两个数据框
    factor_type：因子类型，严格限于RF/MKT/SMB/HML/MOM/RMW/CMA
    输出：图形
    返回值：无
    """
    #仅用作测试，完成后应注释掉
    #model="FF3 Model"
    #scope1="US"
    #scope2="Europe"
    #factor_type='Mkt-RF'
   
    #转换索引类型为DatetimeIndex，便于后续处理
    import pandas as pd
    factors1['Date']=factors1.index.strftime("%Y-%m-%d")
    factors1['Date']=pd.to_datetime(factors1['Date'])
    factors1.set_index('Date',inplace=True)
    
    factors2['Date']=factors2.index.strftime("%Y-%m-%d")
    factors2['Date']=pd.to_datetime(factors2['Date'])
    factors2.set_index('Date',inplace=True)    

    try:
        plt.plot(factors1[factor_type],label=scope1,marker='o')
        plt.plot(factors2[factor_type],label=scope2,marker='*')
    except:
        print("Sorry, no available data for factor",factor_type)
        return
    plt.axhline(y=0.0,color='b',linestyle=':')  
    title1="\n"+model+": "+scope1+" vs. "+scope2+", "+" Factor "+factor_type
    plt.title(title1,fontsize=12,fontweight='bold')
    plt.ylabel(factor_type,fontsize=12,fontweight='bold')
    plt.legend(loc='best')    
    plt.show()       
    
    return

if __name__=='__main__':
    factors1=get_ff3_factors("2009-01-01","2018-12-31",scope='US', \
                                  freq='yearly')
    factors2=get_ff3_factors("2009-01-01","2018-12-31",scope='Europe', \
                                  freq='yearly')
    draw2_ff_factors("FF3 model","US","Europe",factors1,factors2,"Mkt-RF")
    draw2_ff_factors("FF3 model","US","Europe",factors1,factors2,"SMB")
    draw2_ff_factors("FF3 model","US","Europe",factors1,factors2,"HML")

#==============================================================================
def get_ffc4_factors(start,end,scope='US',freq='yearly'):    
    """
    功能：抓取Fama-French-Carhart四因子模型的四个市场因子
    1）市场风险溢价(Rmarket-Rf，收益率风险溢价) 
    2）小市值风险溢价(SMB，规模因子，即小市值股票对比大市值股票的超额收益率)
    3）高市净率风险溢价(HML，价值因子，高溢价股票对比低溢价股票的超额收益率)
    4）交易动量因子(MOM，市场交易中资本利差最高的那部分股票被称为赢家winner，
    而最低的那部分股票被称为输家loser。短期内，赢家具有保持作为赢家的趋势，
    输家具有继续作为输家的趋势。这种现象称为交易惯性，惯性即动量。动量因子
    就是高收益率股票对比低收益率股票的超额收益率)
    
    输入参数：
    start/end：开始/结束日期，格式为YYYY-MM-DD或MM/DD/YYYY
    scope：地区(美国，日本，欧洲，全球，除美国外的全球，除日本外的亚太)
    freq：采样周期(日、周、月、年，其中周仅支持美国市场)
    输出：按照采样周期排列的指定地区的FFC4因子(pandas格式)
    """
    
    #仅为测试用
    #start="2018-01-01"
    #end="2018-12-31"
    #scope='US'
    #freq='monthly'
    
    #抓取FF3因子
    factor='FF3'
    ff3=get_ff_factors(start,end,scope,factor,freq)   
    
    #抓取Mom因子
    factor='Mom'
    try:
        Mom=get_ff_factors(start,end,scope,factor,freq)  
    except:
        print("Sorry, connection to data source failed:-( Try later!")
        return
    
    #将动量数据列名一致化
    if scope == 'US':
        Mom=Mom.rename(columns={'Mom   ':'MOM'})    #针对US数据
    else:
        Mom=Mom.rename(columns={'WML':'MOM'})    #针对非US数据        

    #合成FF3+Mom因子
    import pandas as pd
    ffc4_factors=pd.merge(ff3,Mom,how='inner',left_index=True,right_index=True)
    
    return ffc4_factors


if __name__=='__main__':
    start="2018-01-01"
    end="2018-12-31"
    scope='Europe'
    freq="monthly"
    factors1=get_ffc4_factors("2009-01-01","2018-12-31",scope='US', \
                                  freq='yearly')
    factors2=get_ffc4_factors("2009-01-01","2018-12-31",scope='Japan', \
                                  freq='yearly')
    draw1_ff_factors("FFC4 model","US",factors1,"MOM")


#==============================================================================
def test_ffc4_factors():
    """
    功能：交互式测试资产定价模型FFC4的因子
    输入：用户输入
    显示：各个因子
    返回值：无
    """
    
    import easygui as g

    title="Test the Factors of Fama-French-Carhart 4-factor Model"
    msg="Please fill in the information below"
    fldnames=["Start date (YYYY-MM-DD)","End date (YYYY-MM-DD)", \
          "Scope (US, China, Japan, Europe)", \
          "Frequency (yearly, monthly, daily)"]
    fldvalues=[]
    values=("2018-01-01","2019-04-30","US","monthly")
    fldvalues=g.multenterbox(msg,title=title,fields=fldnames,values=values)
    """
    如果用户输入的值比选项少的话，则返回列表中的值用空字符串填充用户为输入的选项。
    如果用户输入的值比选项多的话，则返回的列表中的值将截断为选项的数量。
    如果用户取消操作，则返回域中的列表的值或者None值
    """
    
    if fldvalues:
        start=fldvalues[0]
        end=fldvalues[1]
        scope=fldvalues[2]
        freq=fldvalues[3]
        
        ff_factors=get_ffc4_factors(start,end,scope,freq)
        if ff_factors is None:
            g.msgbox(msg="Sorry, no factor data available under the condition.", \
                     title=title)                       
        else: 
            g.msgbox(msg=ff_factors,title=title)
    else:
        g.msgbox(msg="Sorry, user cancelled the operation, no data retrieved.", \
                 title=title)
        
    return

if __name__=='__main__':
    test_ffc4_factors()        


#==============================================================================
def get_ff5_factors(start,end,scope='US',freq='yearly'):    
    """
    功能：抓取Fama-French五因子模型的五个市场因子
    1）市场风险溢价(Rmarket-Rf，收益率风险溢价) 
    2）小市值风险溢价(SMB，规模因子，即小市值股票对比大市值股票的超额收益率)
    3）高市净率风险溢价(HML，价值因子，高溢价股票对比低溢价股票的超额收益率)
    4）盈利因子(RMW，盈利好和盈利差的多元化股票组合收益之间的差异。其中，盈利
    定义为年营业收入减去营业成本、利息费用、销售费用和管理费用后再除以t-1财年
    末的账面权益)
    5）投资因子(CMA：投资低和投资高的多元化股票组合收益之间的差异(投资高对长远
    未来有利，但将影响当年业绩。其中，投资定义为t-1财年的新增总资产除以t-2财年
    末的总资产)
    
    输入参数：
    start/end：开始/结束日期，格式为YYYY-MM-DD或MM/DD/YYYY
    scope：地区(美国，日本，欧洲，全球，除美国外的全球，除日本外的亚太)
    freq：采样周期(日、周、月、年，其中周仅支持美国市场)
    输出：按照采样周期排列的指定地区的FF5因子(pandas格式)
    """
    
    #仅为测试用
    #start="2018-01-01"
    #end="2018-12-31"
    #scope='US'
    #freq='monthly'
    
    #抓取FF5因子
    factor='FF5'
    ff5_factors=get_ff_factors(start,end,scope,factor,freq)   
    
    return ff5_factors

if __name__=='__main__':
    factors1=get_ff5_factors("2018-01-01","2018-12-31",scope='US', \
                                  freq='monthly')
    draw1_ff_factors("FFC4 model","US",factors1,"RMW")
    
    factors2=get_ff5_factors("2018-01-01","2018-12-31",scope='Europe', \
                                  freq='monthly')    
    draw1_ff_factors("FFC4 model","US",factors2,"CMA")
    draw2_ff_factors("FFC4 model","US","Europe",factors1,factors2,"RMW")    

#==============================================================================
def test_ff5_factors():
    """
    功能：交互式测试资产定价模型FF5的因子
    输入：用户输入
    显示：各个因子
    返回值：无
    """
    
    import easygui as g

    title="Test the Factors of Fama-French 5-factor Model"
    msg="Please fill in the information below"
    fldnames=["Start date (YYYY-MM-DD)","End date (YYYY-MM-DD)", \
          "Scope (US, China, Japan, Europe)", \
          "Frequency (yearly, monthly, daily)"]
    fldvalues=[]
    values=("2018-01-01","2019-04-30","US","monthly")
    fldvalues=g.multenterbox(msg,title=title,fields=fldnames,values=values)
    """
    如果用户输入的值比选项少的话，则返回列表中的值用空字符串填充用户为输入的选项。
    如果用户输入的值比选项多的话，则返回的列表中的值将截断为选项的数量。
    如果用户取消操作，则返回域中的列表的值或者None值
    """
    
    if fldvalues:
        start=fldvalues[0]
        end=fldvalues[1]
        scope=fldvalues[2]
        freq=fldvalues[3]
        
        ff_factors=get_ff5_factors(start,end,scope,freq)
        if ff_factors is None:
            g.msgbox(msg="Sorry, no factor data available under the condition.", \
                     title=title)                       
        else: 
            g.msgbox(msg=ff_factors,title=title)
    else:
        g.msgbox(msg="Sorry, user cancelled the operation, no data retrieved.", \
                 title=title)
        
    return

if __name__=='__main__':
    test_ff5_factors()   


#==============================================================================

def reg_ff3_betas(ticker,start,end,scope='US',graph=True):
    """
    功能：测试一只股票对于FF3各个因子的系数大小、符号方向和显著性
    输入：
    ticker: 股票代码
    start/end: 开始/结束日期，格式：YYYY-MM-DD或MM/DD/YYYY
    scope: 股票市场地域
    输出：FF3模型对于一只股票日收益率的回归结果
    """
    
    #仅为测试使用，过后应注释掉
    #scope='Japan'
    #ticker='9983.T'
    #start='01/01/2018'
    #end='06/30/2019'        

    #抓取每日股价
    price=get_price(ticker,start,end)
    
    #计算股票日收益率
    import pandas as pd
    ret=pd.DataFrame(price['Close'].pct_change()*100)
    ret=ret.dropna()
    #命名日收益率字段为dRet
    ret=ret.rename(columns={'Close':'dRet'})

    #抓取FF3因子
    freq='daily'
    ff3=get_ff3_factors(start,end,scope,freq)
    if ff3 is None:
        print("  #Error(reg_ff3_betas): factors tentatively inaccessible for",scope,freq)
        return None
    
    #改造索引类型为时间戳索引（DatetimeIndex），便于与ret合成
    ff3['Date']=ff3.index.strftime("%m/%d/%Y")
    ff3['Date']=pd.to_datetime(ff3['Date'])
    ff3.set_index('Date',inplace=True)

    #内连接：股票日收益率+每日FF3因子
    sample=pd.merge(ret,ff3,how='inner',left_index=True,right_index=True)
    sample=sample.dropna()

    #回归FF3模型
    import statsmodels.api as sm
    y=sample['dRet']
    X=sample[['Mkt-RF','SMB','HML']]
    X1=sm.add_constant(X)
    results=sm.OLS(y,X1).fit() 
    
    #生成回归参数
    #dir(results)    #查看回归结果results的属性
    parms=regparms(results)

    #输出结果并绘制横向柱状图    
    if graph == True:
        gparms=parms.iloc[[1,2,3]]
        print("\n",parms)
        title=codetranslate(ticker)+": FF3模型的贝塔系数"
        plt.title(title,fontsize=12,fontweight='bold')
        plt.ylabel("贝塔系数",fontsize=12,fontweight='bold')
        
        import datetime; today = datetime.date.today()
        footnote="FF3因子"+"\n数据来源：雅虎财经, "+str(today)
        plt.xlabel(footnote,fontsize=12,fontweight='bold')
        plt.bar(gparms.index,gparms.coef,0.5,color=['r','g','b'],alpha=0.5)
        plt.axhline(y=0.0,color='blue',linestyle=':')

    return parms

if __name__=='__main__':
    reg_ff3_betas=reg_ff3_betas('9983.T',"2018-01-01","2018-12-31",scope='Japan')
    
#==============================================================================
def test_ff3_betas():
    """
    功能：交互式测试资产定价因子的贝塔系数
    输入：用户输入
    显示：各个因子的贝塔系数
    返回值：无
    """
    
    import easygui as g

    title="Calculate A Stock's Betas Using FF3 Model"
    msg="Please fill in the information below"
    fldnames=["Start date (YYYY-MM-DD)","End date (YYYY-MM-DD)", \
          "Scope (US, China, Japan, Europe)", \
          "Stock code (mind the suffix for no-US stocks)"]
    fldvalues=[]
    values=("2018-01-01","2019-04-30","US","AAPL")
    fldvalues=g.multenterbox(msg,title=title,fields=fldnames,values=values)
    
    if fldvalues:
        start=fldvalues[0]
        end=fldvalues[1]
        scope=fldvalues[2]
        if scope == "China": scope="Asia_Pacific_ex_Japan"
        ticker=fldvalues[3]
        
        parms=reg_ff3_betas(ticker,start,end,scope)
        if parms is None:
            g.msgbox(msg="Sorry, no beta data available under the condition.", \
                     title=title)                       
        else: 
            title=ticker+"'s Betas Using FF3 Model"
            g.msgbox(msg=parms,title=title)
    else:
        g.msgbox(msg="Sorry, user cancelled the operation, no data retrieved.", \
                 title=title)
        
    return

if __name__=='__main__':
    test_ff3_betas()   

    
#==============================================================================
def reg_ffc4_betas(ticker,start,end,scope='US',graph=True):
    """
    功能：测试一只股票对于FFC4各个因子的系数大小、符号方向和显著性
    输入：
    ticker: 股票代码
    start/end: 开始/结束日期，格式：YYYY-MM-DD或MM/DD/YYYY
    scope: 股票市场地域
    输出：FFC4模型对于一只股票日收益率的回归结果
    """
    
    #仅为测试使用，过后应注释掉
    #scope='US'
    #ticker='AAPL'
    #start='01/01/2018'
    #end='06/30/2019'        

    #抓取每日股价
    import siat.security_prices as ssp
    price=get_price(ticker,start,end)
    
    #计算股票日收益率
    import pandas as pd
    ret=pd.DataFrame(price['Close'].pct_change()*100)
    ret=ret.dropna()
    #命名日收益率字段为dRet
    ret=ret.rename(columns={'Close':'dRet'})

    #抓取每日FFC4因子
    freq='daily'
    ffc4=get_ffc4_factors(start,end,scope,freq)
    if ffc4 is None:
        print("  #Error(reg_ffc4_betas): factors tentatively inaccessible for",scope,freq)
        return None    
    
    #改造索引类型为时间戳索引（DatetimeIndex），便于与ret合成
    ffc4['Date']=ffc4.index.strftime("%m/%d/%Y")
    ffc4['Date']=pd.to_datetime(ffc4['Date'])
    ffc4.set_index('Date',inplace=True)    

    #合成股票日收益率+每日FF3因子
    sample=pd.merge(ret,ffc4,how='inner',left_index=True,right_index=True)
    sample=sample.dropna()

    #回归FF3模型
    import statsmodels.api as sm
    y=sample['dRet']
    X=sample[['Mkt-RF','SMB','HML','MOM']]
    X1=sm.add_constant(X)
    results=sm.OLS(y,X1).fit() 
    
    #生成回归参数
    parms=regparms(results)

    #输出结果并绘制横向柱状图
    gparms=parms.iloc[[1,2,3,4]]
    if graph == True:
        #print("\n",parms)
        title=codetranslate(ticker)+": FFC4模型的贝塔系数"
        plt.title(title,fontsize=12,fontweight='bold')
        plt.ylabel("贝塔系数",fontsize=12,fontweight='bold')
        
        import datetime; today = datetime.date.today()
        footnote="FFC4因子"+"\n数据来源：雅虎财经, "+str(today)        
        plt.xlabel(footnote,fontsize=12,fontweight='bold')
        plt.bar(gparms.index,gparms.coef,0.5,color=['r','g','b'],alpha=0.5)
        plt.axhline(y=0.0,color='blue',linestyle=':')

    return parms


if __name__=='__main__':
    ffc4=reg_ffc4_betas('AAPL',"2018-01-01","2019-06-30",scope='US')
    
#==============================================================================
def test_ffc4_betas():
    """
    功能：交互式测试资产定价因子的贝塔系数
    输入：用户输入
    显示：各个因子的贝塔系数
    返回值：无
    """
    
    import easygui as g

    title="Calculate A Stock's Betas Using FFC4 Model"
    msg="Please fill in the information below"
    fldnames=["Start date (YYYY-MM-DD)","End date (YYYY-MM-DD)", \
          "Scope (US, China, Japan, Europe)", \
          "Stock code (mind the suffix for no-US stocks)"]
    fldvalues=[]
    values=("2018-01-01","2019-04-30","Europe","BMW.DE")
    fldvalues=g.multenterbox(msg,title=title,fields=fldnames,values=values)
    
    if fldvalues:
        start=fldvalues[0]
        end=fldvalues[1]
        scope=fldvalues[2]
        if scope == "China": scope="Asia_Pacific_ex_Japan"
        ticker=fldvalues[3]
        
        parms=reg_ffc4_betas(ticker,start,end,scope)
        if parms is None:
            g.msgbox(msg="Sorry, no beta data available under the condition.", \
                     title=title)                       
        else: 
            title=ticker+"'s Betas Using FFC4 Model"
            g.msgbox(msg=parms,title=title)
    else:
        g.msgbox(msg="Sorry, user cancelled the operation, no data retrieved.", \
                 title=title)
        
    return

if __name__=='__main__':
    test_ffc4_betas() 
    
#==============================================================================
def reg_ff5_betas(ticker,start,end,scope='US',graph=True):
    """
    功能：测试一只股票对于FF5各个因子的系数大小、符号方向和显著性
    输入：
    ticker: 股票代码
    start/end: 开始/结束日期，格式：YYYY-MM-DD或MM/DD/YYYY
    scope: 股票市场地域
    输出：FF5模型对于一只股票日收益率的回归结果
    """
    
    #仅为测试使用，过后应注释掉
    #scope='US'
    #ticker='AAPL'
    #start='01/01/2018'
    #end='06/30/2019'        

    #抓取每日股价
    import siat.security_prices as ssp
    price=get_price(ticker,start,end)
    
    #计算股票日收益率
    import pandas as pd
    ret=pd.DataFrame(price['Close'].pct_change()*100)
    ret=ret.dropna()
    #命名日收益率字段为dRet
    ret=ret.rename(columns={'Close':'dRet'})

    #抓取每日FF3因子
    freq='daily'
    ff5=get_ff5_factors(start,end,scope,freq)
    if ff5 is None:
        print("  #Error(reg_ff5_betas): factors tentatively inaccessible for",scope,freq)
        return None       
    
    #改造索引类型为时间戳索引（DatetimeIndex），便于与ret合成
    ff5['Date']=ff5.index.strftime("%m/%d/%Y")
    ff5['Date']=pd.to_datetime(ff5['Date'])
    ff5.set_index('Date',inplace=True)    

    #合成股票日收益率+每日FF3因子
    sample=pd.merge(ret,ff5,how='inner',left_index=True,right_index=True)
    sample=sample.dropna()

    #回归FF3模型
    import statsmodels.api as sm
    y=sample['dRet']
    X=sample[['Mkt-RF','SMB','HML','RMW','CMA']]
    X1=sm.add_constant(X)
    results=sm.OLS(y,X1).fit() 
    
    #生成回归参数
    parms=regparms(results)

    #输出结果并绘制横向柱状图
    gparms=parms.iloc[[1,2,3,4,5]]
    if graph == True:
        #print("\n",parms)
        title=codetranslate(ticker)+"：FF5模型的贝塔系数"
        plt.title(title,fontsize=12,fontweight='bold')
        plt.ylabel("贝塔系数",fontsize=12,fontweight='bold')
        
        import datetime; today = datetime.date.today()
        footnote="FF5因子"+"\n数据来源：雅虎财经, "+str(today)           
        plt.xlabel(footnote,fontsize=12,fontweight='bold')
        plt.bar(gparms.index,gparms.coef,0.5,color=['r','g','b'],alpha=0.5)
        plt.axhline(y=0.0,color='blue',linestyle=':')

    return parms


if __name__=='__main__':
    ff5_betas=reg_ff5_betas('AAPL',"2018-01-01","2019-07-18",scope='US')
    
#==============================================================================
def test_ff5_betas():
    """
    功能：交互式测试资产定价因子的贝塔系数
    输入：用户输入
    显示：各个因子的贝塔系数
    返回值：无
    """
    
    import easygui as g

    title="Calculate A Stock's Betas Using FF5 Model"
    msg="Please fill in the information below"
    fldnames=["Start date (YYYY-MM-DD)","End date (YYYY-MM-DD)", \
          "Scope (US, China, Japan, Europe)", \
          "Stock code (mind the suffix for no-US stocks)"]
    fldvalues=[]
    values=("2018-01-01","2019-04-30","Japan","9983.T")
    fldvalues=g.multenterbox(msg,title=title,fields=fldnames,values=values)
    
    if fldvalues:
        start=fldvalues[0]
        end=fldvalues[1]
        scope=fldvalues[2]
        if scope == "China": scope="Asia_Pacific_ex_Japan"
        ticker=fldvalues[3]
        
        parms=reg_ff5_betas(ticker,start,end,scope)
        if parms is None:
            g.msgbox(msg="Sorry, no beta data available under the condition.", \
                     title=title)                       
        else: 
            title=ticker+"'s Betas Using FF5 Model"
            g.msgbox(msg=parms,title=title)
    else:
        g.msgbox(msg="Sorry, user cancelled the operation, no data retrieved.", \
                 title=title)
        
    return

if __name__=='__main__':
    test_ff5_betas() 
    
#==============================================================================    