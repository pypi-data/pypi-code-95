# -*- coding: utf-8 -*-
"""
本模块功能：绘制折线图
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2020年9月16日
最新修订日期：2020年9月16日
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
from siat.common import *
from siat.translate import *
import pandas as pd
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
def plot_line(df0,colname,collabel,ylabeltxt,titletxt,footnote,datatag=False, \
              power=0,zeroline=False,resample_freq='H'):
    """
    功能：绘制折线图。如果power=0不绘制趋势图，否则绘制多项式趋势图
    假定：数据表有索引，且已经按照索引排序
    输入：数据表df，数据表中的列名colname，列名的标签collabel；y轴标签ylabeltxt；
    标题titletxt，脚注footnote；是否在图中标记数据datatag；趋势图的多项式次数power
    输出：折线图
    返回值：无
    """

    #插值平滑
    df=df_smooth_manual(df0,resample_freq=resample_freq)

    #先绘制折线图
    """
    plt.plot(df.index,df[colname],'-',label=collabel, \
             linestyle='-',color='blue', linewidth=1, \
                 marker='o',markersize=2)
    """
    plt.plot(df.index,df[colname],'-',label=collabel, \
             linestyle='-',color='blue', linewidth=2)
    #绘制数据标签
    if datatag:
        for x, y in zip(df.index, df[colname]):
            plt.text(x,y+0.1,'%.2f' % y,ha='center',va='bottom',color='black')        
    
    #是否绘制水平0线
    if zeroline and (min(df[colname]) < 0):
        plt.axhline(y=0,ls=":",c="black",linewidth=1)
        
    #绘制趋势线
    #print("--Debug(plot_line): power=",power)
    if power > 0:
        try:
            #生成行号，借此将横轴的日期数量化，以便拟合
            df['id']=range(len(df))
        
            #设定多项式拟合，power为多项式次数
            import numpy as np
            parameter = np.polyfit(df.id, df[colname], power)
            f = np.poly1d(parameter)
            plt.plot(df.index, f(df.id),"r--", label="趋势线",linewidth=1)
        except: 
            print("  Warning(plot_line): failed to converge trend line.")
    
    plt.legend(loc='best')
    plt.gcf().autofmt_xdate() # 优化标注（自动倾斜）
    #plt.xticks(rotation=45)
    plt.ylabel(ylabeltxt)
    plt.xlabel(footnote)
    plt.title(titletxt,fontsize=12)
    plt.show()
    plt.close()
    return

if __name__ =="__main__":
    plot_line(df,'Close',"收盘价","价格","万科股票","数据来源：雅虎财经",power=4)

#==============================================================================
def plot_line2(df1,ticker1,colname1,label1, \
               df2,ticker2,colname2,label2, \
               ylabeltxt,titletxt,footnote, \
               power=0,datatag1=False,datatag2=False,yscalemax=5, \
               zeroline=False,twinx=False,yline=999,xline=999,resample_freq='H'):
    """
    功能：绘制两个证券的折线图。如果power=0不绘制趋势图，否则绘制多项式趋势图
    假定：数据表有索引，且已经按照索引排序
    输入：
    证券1：数据表df1，证券代码ticker1，列名1，列名标签1；
    证券2：数据表df2，证券代码ticker2，列名2，列名标签2；
    标题titletxt，脚注footnote；是否在图中标记数据datatag；趋势图的多项式次数power
    输出：默认绘制同轴折线图，若twinx=True则绘制双轴折线图
    返回值：无
    """
    
    if not twinx:            
        plot_line2_coaxial(df1,ticker1,colname1,label1, \
                           df2,ticker2,colname2,label2, \
                ylabeltxt,titletxt,footnote,power,datatag1,datatag2,zeroline, \
                yline,xline,resample_freq=resample_freq)
    else:
        plot_line2_twinx(df1,ticker1,colname1,label1, \
                         df2,ticker2,colname2,label2, \
                         titletxt,footnote,power,datatag1,datatag2, \
                         resample_freq=resample_freq)
    return


#==============================================================================
def plot_line2_coaxial(df01,ticker1,colname1,label1, \
                       df02,ticker2,colname2,label2, \
                    ylabeltxt,titletxt,footnote, \
                    power=0,datatag1=False,datatag2=False,zeroline=False, \
                    yline=999,xline=999,resample_freq='H'):
    """
    功能：绘制两个证券的折线图。如果power=0不绘制趋势图，否则绘制多项式趋势图
    假定：数据表有索引，且已经按照索引排序
    输入：
    证券1：数据表df1，证券代码ticker1，列名1，列名标签1；
    证券2：数据表df2，证券代码ticker2，列名2，列名标签2；
    标题titletxt，脚注footnote；是否在图中标记数据datatag；趋势图的多项式次数power
    输出：绘制同轴折线图
    返回值：无
    """

    #插值平滑
    df1=df_smooth_manual(df01,resample_freq=resample_freq)
    df2=df_smooth_manual(df02,resample_freq=resample_freq)
    
    #证券1：先绘制折线图
    plt.plot(df1.index,df1[colname1],'-',label=codetranslate(ticker1)+'('+label1+')', \
             linestyle='-',linewidth=2)
    #证券1：绘制数据标签
    if datatag1:
        for x, y in zip(df1.index, df1[colname1]):
            plt.text(x,y+0.1,'%.2f' % y,ha='center',va='bottom',color='black')        

    #是否绘制水平0线
    if zeroline and ((min(df1[colname1]) < 0) or (min(df2[colname2]) < 0)):
        plt.axhline(y=0,ls=":",c="black",linewidth=1)

    #是否绘制水平线
    if yline != 999:
        plt.axhline(y=yline,ls=":",c="black",linewidth=1)        

    #是否绘制垂直线
    if xline != 999:
        plt.axvline(x=xline,ls=":",c="black",linewidth=1)   
    
    #绘证券1：制趋势线
    if power > 0:
        try:
            #生成行号，借此将横轴的日期数量化，以便拟合
            df1['id']=range(len(df1))
        
            #设定多项式拟合，power为多项式次数
            import numpy as np
            parameter = np.polyfit(df1.id, df1[colname1], power)
            f = np.poly1d(parameter)
            plt.plot(df1.index, f(df1.id),"r--", label=codetranslate(ticker1)+"(趋势线)",linewidth=1)
        except: pass
    
    #证券2：先绘制折线图
    plt.plot(df2.index,df2[colname2],'-',label=codetranslate(ticker2)+'('+label2+')', \
             linestyle='-.',linewidth=1)
    #证券2：绘制数据标签
    if datatag2:
        for x, y in zip(df2.index, df2[colname2]):
            plt.text(x,y+0.1,'%.2f' % y,ha='center',va='bottom',color='black')        
        
    #绘证券2：制趋势线
    if power > 0:
        try:
            #生成行号，借此将横轴的日期数量化，以便拟合
            df2['id']=range(len(df2))
        
            #设定多项式拟合，power为多项式次数
            import numpy as np
            parameter = np.polyfit(df2.id, df2[colname2], power)
            f = np.poly1d(parameter)
            plt.plot(df2.index, f(df2.id),"r--", label=codetranslate(ticker2)+"(趋势线)",linewidth=1)
        except: pass
    
    plt.legend(loc='best')
    plt.gcf().autofmt_xdate() # 优化标注（自动倾斜）
    #plt.xticks(rotation=45)
    plt.ylabel(ylabeltxt)
    plt.xlabel(footnote)
    #plt.title(titletxt,fontsize=12)
    plt.title(titletxt,fontsize=12)
    plt.show()
    plt.close()
    return

if __name__ =="__main__":
    df1 = get_price('000002.SZ', '2020-1-1', '2020-3-16')
    df2 = get_price('600266.SS', '2020-1-1', '2020-3-16')
    ticker1='000002.SZ'; ticker2='600266.SS'
    colname1='Close'; colname2='Close'
    label1="收盘价"; label2="收盘价"
    ylabeltxt="价格"
    plot_line2_coaxial(df1,'000002.SZ','High','最高价', \
        df1,'000002.SZ','Low','最低价',"价格", \
        "证券价格走势对比图","数据来源：雅虎财经")
    plot_line2_coaxial(df1,'000002.SZ','Open','开盘价', \
        df1,'000002.SZ','Close','收盘价',"价格", \
        "证券价格走势对比图","数据来源：雅虎财经")

    plot_line2_coaxial(df2,'600266.SS','Open','开盘价', \
        df2,'600266.SS','Close','收盘价',"价格", \
        "证券价格走势对比图","数据来源：雅虎财经")

#==============================================================================
def plot_line2_twinx(df01,ticker1,colname1,label1, \
                     df02,ticker2,colname2,label2, \
        titletxt,footnote,power=0,datatag1=False,datatag2=False,resample_freq='H'):
    """
    功能：绘制两个证券的折线图。如果power=0不绘制趋势图，否则绘制多项式趋势图
    假定：数据表有索引，且已经按照索引排序
    输入：
    证券1：数据表df1，证券代码ticker1，列名1，列名标签1；
    证券2：数据表df2，证券代码ticker2，列名2，列名标签2；
    标题titletxt，脚注footnote；是否在图中标记数据datatag；趋势图的多项式次数power
    输出：绘制双轴折线图
    返回值：无
    """

    #插值平滑
    df1=df_smooth_manual(df01,resample_freq=resample_freq)
    df2=df_smooth_manual(df02,resample_freq=resample_freq)

    #证券1：绘制折线图，双坐标轴
    import matplotlib.dates as mdates
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(df1.index,df1[colname1],'-',label=codetranslate(ticker1)+'('+label1+')', \
             linestyle='-',color='blue',linewidth=2)   
    #证券1：绘制数据标签
    if datatag1:
        for x, y in zip(df1.index, df1[colname1]):
            ax.text(x,y+0.1,'%.2f' % y,ha='center',va='bottom',color='black')

    #绘证券1：制趋势线
    if power > 0:
        #生成行号，借此将横轴的日期数量化，以便拟合
        df1['id']=range(len(df1))
        
        #设定多项式拟合，power为多项式次数
        import numpy as np
        parameter = np.polyfit(df1.id, df1[colname1], power)
        f = np.poly1d(parameter)
        ax.plot(df1.index, f(df1.id),"r--", label=codetranslate(ticker1)+"(趋势线)",linewidth=1)

    #绘证券2：建立第二y轴
    ax2 = ax.twinx()
    ax2.plot(df2.index,df2[colname2],'-',label=codetranslate(ticker2)+'('+label2+')', \
             linestyle='-.',color='orange',linewidth=1)
    #证券2：绘制数据标签
    if datatag2:
        for x, y in zip(df2.index, df2[colname2]):
            ax2.text(x,y+0.1,'%.2f' % y,ha='center',va='bottom',color='black')
    
    #绘证券2：制趋势线
    if power > 0:
        #生成行号，借此将横轴的日期数量化，以便拟合
        df2['id']=range(len(df2))
        
        #设定多项式拟合，power为多项式次数
        import numpy as np
        parameter = np.polyfit(df2.id, df2[colname2], power)
        f = np.poly1d(parameter)
        ax2.plot(df2.index, f(df2.id),"c--", label=codetranslate(ticker2)+"(趋势线)",linewidth=1)        
        
    ax.set_xlabel(footnote)
    ax.set_ylabel(label1+'('+codetranslate(ticker1)+')')
    ax.legend(loc='upper left')
    ax2.set_ylabel(label2+'('+codetranslate(ticker2)+')')
    ax2.legend(loc='upper right')
    
    #自动优化x轴标签
    #格式化时间轴标注
    #plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%y-%m-%d')) 
    plt.gcf().autofmt_xdate() # 优化标注（自动倾斜）
    
    plt.title(titletxt, fontsize=12)
    plt.show()
    
    return


if __name__ =="__main__":
    df1 = get_price('000002.SZ', '2020-1-1', '2020-3-16')
    df2 = get_price('600266.SS', '2020-1-1', '2020-3-16')
    ticker1='000002.SZ'; ticker2='600266.SS'
    colname1='Close'; colname2='Close'
    label1="收盘价"; label2="收盘价"
    ylabeltxt="价格"
    plot_line2_twinx(df1,'000002.SZ','Close','收盘价', \
        df2,'600266.SS','Close','收盘价', \
        "证券价格走势对比图","数据来源：雅虎财经")

    plot_line2_twinx(df1,'000002.SZ','Close','收盘价', \
        df2,'600266.SS','Close','收盘价', \
        "证券价格走势对比图","数据来源：雅虎财经",power=3)

#==============================================================================
def draw_lines(df0,y_label,x_label,axhline_value,axhline_label,title_txt, \
               data_label=True,resample_freq='H'):
    """
    函数功能：根据df的内容绘制折线图
    输入参数：
    df：数据框。有几个字段就绘制几条折现。必须索引，索引值将作为X轴标记点
    axhline_label: 水平辅助线标记。如果为空值则不绘制水平辅助线
    axhline_value: 水平辅助线的y轴位置
    y_label：y轴标记
    x_label：x轴标记
    title_txt：标题。如需多行，中间用\n分割
    
    输出：
    绘制折线图
    无返回数据
    """

    #插值平滑
    df=df_smooth_manual(df0,resample_freq=resample_freq)

    #取得df字段名列表
    collist=df.columns.values.tolist()  
    
    #绘制折线图    
    for c in collist:
        plt.plot(df[c],label=c,linewidth=2)
        #为折线加数据标签
        if data_label==True:
            for a,b in zip(df.index,df[c]):
                plt.text(a,b+0.02,str(round(b,2)), \
                         ha='center',va='bottom',fontsize=7)
    
    #绘制水平辅助线
    if axhline_label !="":
        plt.axhline(y=axhline_value,label=axhline_label,color='green',linestyle=':',linewidth=0.5)  
    
    #坐标轴标记
    plt.ylabel(y_label,fontweight='bold')
    if x_label != "":
        plt.xlabel(x_label,fontweight='bold')
    #图示标题
    plt.title(title_txt,fontsize=12)
    plt.xticks(rotation=45)
    plt.legend(loc='best')
    plt.show()
    
    return    
    
if __name__=='__main__':
    title_txt="Stock Risk \nCAPM Beta Trends"
    draw_lines(df,"market line",1.0,"Beta coefficient","",title_txt)    

#==============================================================================
def plot_barh(df,colname,titletxt,footnote,datatag=True, \
              colors=['r','g','b','c','m','y','aquamarine','dodgerblue', \
              'deepskyblue','silver'],tag_offset=0.05,axisamp=1.3):
    """
    功能：绘制水平柱状图，并可标注数据标签。
    输入：数据集df；列名colname；标题titletxt；脚注footnote；
    是否绘制数据标签datatag，默认是；柱状图柱子色彩列表。
    输出：水平柱状图
    """

    plt.barh(df.index,df[colname],align='center',color=colors,alpha=0.8)
    coltxt=ectranslate(colname)
    plt.xlabel(footnote)
    plt.title(titletxt,fontsize=12)
    
    #xmin=int(min(df[colname]))
    xmin0=min(df[colname])
    if xmin0 > 0:
        xmin=xmin0*0.8
    else:
        xmin=xmin0*1.05
    #xmax=(int(max(df[colname]))+1)*1.1
    xmax0=max(df[colname])
    scale_max=abs((xmax0-xmin0)/xmax0)*axisamp  #经验值放大倍数
    xmax=xmax0*scale_max
    """
    if xmax0 > 0:
        xmax=xmax0*1.8
    else:
        xmax=xmax0*1.2
    """
    plt.xlim([xmin,xmax])
    
    tag_off=tag_offset * xmax
    for x,y in enumerate(list(df[colname])):
        #plt.text(y+0.1,x,'%s' % y,va='center')
        plt.text(y+tag_off,x,'%s' % y,va='center')

    """
    yticklist=list(df.index)
    yticknames=[]
    for yt in yticklist:
        ytname=codetranslate(yt)
        yticknames=yticknames+[ytname]
    """
    yticknames=list(df.index)
    plt.yticks(df.index,yticknames)

    plt.show(); plt.close()
    
    return

#==============================================================================
#==============================================================================
#==============================================================================
def plot_2lines(df01,colname1,label1, \
                df02,colname2,label2, \
                ylabeltxt,titletxt,footnote,hline=0,vline=0,resample_freq='H'):
    """
    功能：绘制两个证券的折线图。如果hline=0不绘制水平虚线，vline=0不绘制垂直虚线
    假定：数据表有索引，且已经按照索引排序
    输入：
    证券1：数据表df1，列名1，列名标签1；
    证券2：数据表df2，列名2，列名标签2；
    标题titletxt，脚注footnote
    输出：绘制同轴折线图
    返回值：无
    """

    #插值平滑
    try:
        df1=df_smooth_manual(df01,resample_freq=resample_freq)
        df2=df_smooth_manual(df02,resample_freq=resample_freq)
    except:
        df1=df01
        df2=df02
    
    plt.title(titletxt,fontsize=12)
    
    #证券1：先绘制折线图
    plt.plot(df1.index,df1[colname1],label=label1,linestyle='-',linewidth=2)
    
    #证券2：先绘制折线图
    plt.plot(df2.index,df2[colname2],label=label2,linestyle='-.',linewidth=2)
    """
    #是否绘制水平虚线
    if not (hline == 0):
        plt.axhline(y=hline,ls=":",c="black")
    #是否绘制垂直虚线
    if not (vline == 0):
        plt.axvline(x=vline,ls=":",c="black")
    """    
    plt.ylabel(ylabeltxt)
    plt.xlabel(footnote)
    plt.legend(loc='best')
    plt.show()
    
    return

if __name__ =="__main__":
    df1=bsm_call_maturity(42,40,[50,200],0.015,0.23,90,1.5)
    df2=bsm_put_maturity(42,40,[50,200],0.015,0.23,90,1.5)
    ticker1='A'; colname1='Option Price'; label1='A1'
    ticker2='B'; colname2='Option Price'; label2='B2'
    ylabeltxt='ylabel'; titletxt='title'; footnote='\n\n\n\n4lines'
    power=0; datatag1=False; datatag2=False; zeroline=False
    
#==============================================================================
def df_smooth(df):
    """
    功能：对df中的数值型样本进行插值，以便绘制的折线图相对平滑。
    要求：df的索引为pandas的datetime日期型
    注意1：如果样本数量较多，例如多于100个，平滑效果不明显。
    注意2：order阶数仅对'spline'和'polynomial'方法有效，其中'polynomial'方法的阶数只能为奇数。
    """
    
    """
    #如果样本个数多于100个，其实没必要进行平滑
    if len(df) >= 100: return df
    """
    
    #定义重采样频率
    """
    常用的采样频率：
    H: hourly, BH: business hour, T: minutely, S: secondly, B: business day, W: weekly, 
    SM: semi-month end, SMS: semi-month start, 
    BMS: business month start,BM: business month end,
    BQ: business quarter end, BQS: business quarter start,
    BA/BY: business year end, BAS/BYS: business year start.    
    
    例如：
    df2=df.resample('2D').sum()
    df2=df.resample('W').mean()
    """
    #将索引转换为Datetimeindex，不然resample会失败
    df['date']=pd.to_datetime(df.index)
    df.set_index('date',inplace=True)
    
    #重新采样
    rflag=False
    freqlist=['H','B','W','M','Q']
    for f in freqlist:
        try:
            #dfh=df.resample(f).ffill()
            dfh=df.resample(f)
        except:
            continue
        else:
            rflag=True
            break
    
    if not rflag: 
        #print('  #Warning(df_smooth): resampling failed for frequency',freqlist)
        dfh=df
    
    #插值
    methodlist=['pchip','nearest','cubic','quadratic','slinear','linear','zero','time','index', \
            'piecewise_polynomial','akima','from_derivatives','spline','polynomial']
    methodlist_order=['spline','polynomial']
    order=3
    for method in methodlist:
        if method in methodlist_order:
            try:
                dfm=dfh.interpolate(method=method,order=order)
            except:
                #print('  #Warning(df_smooth): interpolate failed for method',method,'with order',order)
                #若出错就原样返回
                return df
            else: break
        else:
            try:
                dfm=dfh.interpolate(method=method)
            except:
                #print('  #Warning(df_smooth): interpolate failed for method',method)
                return df
            else: break
    
    #成功返回经过重采样的df
    return dfm        
    
        
#==============================================================================
def df_smooth_manual(df,method='pchip',resample_freq='H',order=3):
    """
    功能：对df中的数值型样本进行插值，以便绘制的折线图相对平滑。
    要求：df的索引为pandas的datetime日期型
    注意1：如果样本数量较多，例如多于100个，平滑效果不明显。
    注意2：order阶数仅对'spline'和'polynomial'方法有效，其中'polynomial'方法的阶数只能为奇数。
    """
    
    """
    #如果样本个数多于100个，没必要进行平滑
    if len(df) >= 100: return df
    """
    
    #检查平滑方法是否支持
    methodlist=['quadratic','cubic','slinear','linear','zero','nearest','time','index', \
            'piecewise_polynomial','pchip','akima','from_derivatives','spline','polynomial']
    if not (method in methodlist): return df
    
    #定义重采样频率
    """
    常用的采样频率：
    H: hourly, BH: business hour, T: minutely, S: secondly, B: business day, W: weekly, 
    SM: semi-month end, SMS: semi-month start, 
    BMS: business month start,BM: business month end,
    BQ: business quarter end, BQS: business quarter start,
    BA/BY: business year end, BAS/BYS: business year start.    
    
    例如：
    df2=df.resample('2D').sum()
    df2=df.resample('W').mean()
    """
    #将索引转换为Datetimeindex，不然resample会失败
    df['date']=pd.to_datetime(df.index)
    df.set_index('date',inplace=True)    
    
    try:
        dfh=df.resample(resample_freq)
    except:
        print('  #Warning(df_smooth): resampling failed for frequency',resample_freq)
        return df
    
    #重新采样
    methodlist_o=['spline','polynomial']
    if method in methodlist_o:
        try:
            dfm=dfh.interpolate(method=method,order=order)
        except:
            print('  #Warning(df_smooth): interpolate failed for method',method,'with order',order)
            #若出错就原样返回
            return df
        #成功返回经过重采样的df
        return dfm
    
    try:
        dfm=dfh.interpolate(method=method)
    except:
        print('  #Warning(df_smooth): interpolate failed for method',method)
        return df
    return dfm        
#==============================================================================
        
    
    
    









