# -*- coding: utf-8 -*-

import os; os.chdir('S:/siat')
from siat.security_prices import *
from siat.grafix import *

#==============================================================================
df=get_prices('INTC','2021-1-1','2021-3-31')
df.Close.plot()

dfm=df_smooth(df,method='pchip',sampling='H',order=3)
dfm.Close.plot()

dfa=df_smooth(df,method='akima')
dfa.Close.plot()

#==============================================================================

df.plot(y=['High','Close','Low'])

#================
#按照小时为单位重新采样日期时间
dfh=df.resample('H')
methodlist=['quadratic','cubic','slinear','linear','zero','nearest','time','index','barycentric', \
            'krogh','piecewise_polynomial','pchip','akima','from_derivatives']
for m in methodlist:
    dfm=dfh.interpolate(method=m)
    dfm.plot(y=['High','Close','Low'],xlabel='Method = '+m)
#结果：pchip效果最真实，akima也不错

methodlist_o=['spline','polynomial']
orderlist=[1,2,3,4,5,6]
for mo in methodlist_o:
    for od in orderlist:
        try:
            dfm=dfh.interpolate(method=mo,order=od)
            dfm.plot(y=['High','Close','Low'],xlabel='Method = '+mo+', order = '+str(od))
        except: continue
#结果：效果都不佳
#===================

dfh=df.resample('H')
dfhp=dfh.interpolate(method='pchip')

import matplotlib.pyplot as plt
# 解决中文显示问题：SimHei黑体  FangSong仿宋
plt.rcParams['font.sans-serif'] = ['SimHei']  
plt.rcParams['axes.unicode_minus'] = False

titletxt='绘图'
stylelist=[]
footnote='日期'
ylabeltxtleft='收盘价'
ylabeltxtright='最高价'
dfh.Close.plot(title=titletxt,legend=True,xlabel=footnote,ylabel=ylabeltxt,fontsize=8)

dfhp[['High','Close']].plot(secondary_y=['High'])
ax=dfhp.plot(y=['High','Close'],secondary_y=['High'])
ax.set_ylabel(ylabeltxtleft)
ax.right_ax.set_ylabel(ylabeltxtright)

dfhc.plot(y=['Close'])
dfhc.plot(y=['High'],secondary_y=True)
plt.show()


import matplotlib.pyplot as plt
# 解决中文显示问题：SimHei黑体  FangSong仿宋
plt.rcParams['font.sans-serif'] = ['SimHei']  
plt.rcParams['axes.unicode_minus'] = False

x=dfhc.index; y=dfhc.Close

plt.plot(x, y, linewidth=1)
plt.title("绘图", fontsize=14)#标题及字号
plt.xlabel("X", fontsize=12)#X轴标题及字号
plt.ylabel("Y", fontsize=12)#Y轴标题及字号
plt.tick_params(axis='both', labelsize=8)#刻度大小
plt.show()


#==============================================================================

 

 



