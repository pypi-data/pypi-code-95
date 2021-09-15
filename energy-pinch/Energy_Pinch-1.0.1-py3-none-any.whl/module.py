# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 18:41:06 2020
@author: Hedi ROMDHANA 
hedi.romdhana@agroparistech.fr
"""
from numpy import array, diff,sort,cumsum,concatenate,linspace,polyfit,polyval,RankWarning
import matplotlib.pyplot as plt
#from scipy.interpolate import interp1d
import warnings
#from scipy import interpolate
def pinch(streams,dt=10,table=False,composites=False,grand_composite=False):
    Ts=[] # shifted temperatures
    Thot=[] #actual hot temperatures
    Tcold=[] #actual cold temperatures
    for s in streams:
        s['T']=array(s['T'])
        if diff(s['T'])[0]<0:
            s['type']=1
            s['Ts']=s['T']-dt/2
        else:
            s['type']=0
            s['Ts']=s['T']+dt/2
        for Ts1 in s['Ts']:
            if not Ts1 in Ts:
                Ts.append(Ts1)
        for T1 in s['T']:
            if s['type']:
                if not T1 in Thot:
                    Thot.append(T1)
            else:
                if not T1 in Tcold:
                    Tcold.append(T1)
                    
    for i in range(len(streams)):
        #print('assign names...')
        if not 'name' in streams[i].keys():
           if streams[i]['type']==1:
                streams[i]['name']='hot_'+str(i)
           else:
                streams[i]['name']='cold_'+str(i)
    Ts=sort(Ts)[::-1]
    Thot=sort(Thot)
    Tcold=sort(Tcold)
    
    #print(Thot)
    #print(Tcold)
    
    #grouping
    groups=[]
    count=-1
    for i in range(len(Ts)-1):
        count+=1
        groups.append({'streams':[],'dh':0,'dts':Ts[i]-Ts[i+1]})
        for j in range(len(streams)):
            if Ts[i+1]>=streams[j]['Ts'][0] and Ts[i]<=streams[j]['Ts'][1] or Ts[i+1]>=streams[j]['Ts'][1] and Ts[i]<=streams[j]['Ts'][0]:
                groups[count]['streams'].append(j)
                f=-1
                if streams[j]['type']:
                   f=1
                #net balance
                groups[count]['dh']+=f*groups[count]['dts']*streams[j]['DC']
    cascade1=concatenate(([0],cumsum(list(map(lambda x:x['dh'],groups)))))
    hot_utility=-min(cascade1)
    pinchTs=Ts[cascade1==min(cascade1)]
    pinchThot=pinchTs[0]+dt/2
    pinchTcold=pinchTs[0]-dt/2
    cold_utility=cascade1[-1]+hot_utility
    Hhot=[0]
    for i in range(len(Thot)-1):
        Hhot.append(0)
        for j in range(len(streams)):
            if streams[j]['type'] and Thot[i+1]<=streams[j]['T'][0] and Thot[i]>=streams[j]['T'][1]:
                Hhot[i+1]+=streams[j]['DC']*(Thot[i+1]-Thot[i])
    Hhot=cumsum(Hhot)
    
    Hcold=[cold_utility]
    for i in range(len(Tcold)-1):
        Hcold.append(0)
        for j in range(len(streams)):
            if not streams[j]['type'] and Tcold[i+1]<=streams[j]['T'][1] and Tcold[i]>=streams[j]['T'][0]:
                Hcold[i+1]+=streams[j]['DC']*(Tcold[i+1]-Tcold[i])
    Hcold=cumsum(Hcold)
    
    if table:
        from prettytable import PrettyTable
        t = PrettyTable(['Ts °C','streams','DT °C','Bilan net kW',"cascade 1 kW",'cascade 2 kW'])
        for i in range(len(groups)):
            t.add_row([Ts[i],'','','',cascade1[i],cascade1[i]+hot_utility])
            groups_=[]
            for j in range(len(groups[i]["streams"])):
                groups_.append(streams[groups[i]["streams"][j]]['name'])
            t.add_row(['',groups_,groups[i]['dts'],groups[i]['dh'],'',''])
        t.add_row([Ts[-1],'','','',cascade1[-1],cascade1[-1]+hot_utility])
        print(t.get_string(title="Pinch analysis DT="+str(dt)+"°C"))
    if composites:
        plt.figure(1)
        plt.plot(Hcold,Tcold,markerfacecolor='white',marker='s',markersize=4,color='blue',label='Cold composite curve')
        plt.plot(Hhot,Thot,markerfacecolor='white',marker='s',markersize=4,color='red',label='Hot composite curve')
        # plt.plot([cold_utility]*100,linspace(Tcold[0],Thot[-1],100),'--',color='gray')
        # plt.plot([0]*100,linspace(Tcold[0],Thot[-1],100),'--',color='gray')
        # plt.plot([Hhot[-1]]*100,linspace(Tcold[0],Thot[-1],100),'--',color='gray')
        # plt.plot([Hcold[-1]]*100,linspace(Tcold[0],Tcold[-1],100),'--',color='gray')
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', RankWarning)
        zhot = polyfit(Hhot,Thot, 6)
        zcold = polyfit(Hcold,Tcold,1)
        # tck_hot = interpolate.splrep(Hhot,Thot)
        #plt.fill_between([0,cold_utility],[pinchTcold,pinchTcold],hatch='////',facecolor='white',)
        #plt.fill_between([Hhot[-1],Hcold[-1]],[Thot[-1],Thot[-1]],[pinchThot,pinchThot],hatch='////',facecolor='white',)
        plt.plot([cold_utility]*100,linspace(Tcold[0], polyval(zhot,cold_utility),100),'--',color='gray')
        plt.plot([Hhot[-1]]*100,linspace(Thot[-1], polyval(zcold,Hhot[-1]),100),'--',color='gray')
        plt.annotate('', xy=(0, polyval(zhot,cold_utility)),xytext=(cold_utility,polyval(zhot,cold_utility)), arrowprops=dict(arrowstyle="<->",linestyle="-",color='gray'))
        plt.annotate('', xy=(Hhot[-1], polyval(zcold,Hhot[-1])),xytext=(Hcold[-1],polyval(zcold,Hhot[-1])), arrowprops=dict(arrowstyle="<->",linestyle="-",color='gray'))
        plt.text(Hcold[0]/40,pinchThot,'{:.1f}'.format(cold_utility)+' kW')
        plt.text(Hhot[-1]*1,polyval(zcold,Hhot[-1])*.9,'{:.1f}'.format(hot_utility)+' kW')
        plt.grid()
        plt.legend()
        plt.xlabel('Heat flow (kW)')
        plt.ylabel('Temperature (°C)')
        #plt.yticks(concatenate((Thot,Tcold)))
       
    if grand_composite:
        plt.figure(2)
        plt.plot(cascade1+hot_utility,Ts)
        plt.grid()
        plt.xlabel('Net heat flow (kW)')
        plt.ylabel('Shifted temperature (°C)')
        # plt.annotate('', xy=(0, Ts[-1]),xytext=(cold_utility,Ts[-1]), arrowprops=dict(arrowstyle="<->",linestyle="-",color='gray'))
        # plt.annotate('', xy=(0, Ts[0]),xytext=(hot_utility,Ts[0]), arrowprops=dict(arrowstyle="<->",linestyle="-",color='gray'))
        plt.fill_between(cascade1+hot_utility,Ts,where=Ts<=pinchTs,hatch='//',facecolor='skyblue')
        plt.fill_between(cascade1+hot_utility,Ts,Ts[0],where=Ts>=pinchTs,hatch='\\',facecolor="salmon")
        plt.text(hot_utility,Thot[-1]*.9,'{:.1f}'.format(hot_utility)+' kW')
        plt.text(cold_utility*.85,5,'{:.1f}'.format(cold_utility)+' kW')
    return {'hot_utility':hot_utility,'cold_utility':cold_utility}
def test(ex):
    if ex=="TD GPB 2020":
        streams=[{'DC':2,'T':[20,135.],'name':'F1'},
                 {'DC':3,'T':[170,60],'name':'C1'},
                 {'DC':4,'T':[80,140],'name':'F2'},
                 {'DC':1.5,'T':[150,30],'name':'C2'}]
        pinch(streams,10);