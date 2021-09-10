#!/usr/bin/env python3

from fire import Fire
from read_vme_offline.version import __version__

#print("i... module read_vme_offline/ascdf is being run")

import pandas as pd
import tables # here, to avoid a crash when writing pandas
import h5py
import datetime
import subprocess as sp
import numpy as np

import os
import datetime as dt

import matplotlib.pyplot as plt

#>>> import pandas as pd
#>>> import matplotlib.pyplot as plt
#>>> df=pd.read_hdf("run0001_20200526_102519.h5")
#>>> plt.hist( df['E'][  (df.xx=0) & ( (df.t-df.t.shift())<0.0001) ] , 1024, range=[0,2048] )
# plt.show()
#
#


def shift_channels(df , TSHIFT, TWIN, x,y):

    # df = df.loc[  df["ch"]==1 , "time"] = df["time"] + 100
    # df['time'] = df['ch'].apply(lambda x: df["time"]+100 if  x==1 else df["time"] )

    #works
    #df["time"] = df["time"] + TSHIFT*df["ch"]

    #df.loc[df['chan'] == x, 'time'] = df.loc[ df['chan']==x , 'time'] + TSHIFT
    df.loc[df['ch'] == y, 'time'] = df.loc[ df['ch']==y , 'time'] + TSHIFT
    return df


def only_read( filename, x=0, y=1, batch=0, read_last=0):
    """
    reads the filename to DF and returns it
    """
    basename = os.path.basename(filename)
    basename = os.path.splitext(basename)[0]
    startd = basename.split("_")[1]
    startt = basename.split("_")[2]
    print("D...  time start MARK=",startd+startt)


    ok = False
    try:
        start = dt.datetime.strptime(startd+startt,"%Y%m%d%H%M%S" )
        ok = True
        print("D... succesfull start with 4 digit year")
    except:
        print("x... year may not by 4 digits")

    if not(ok):
        print("X... trying 2 digits for year")
        start = dt.datetime.strptime(startd+startt,"%y%m%d%H%M%S" )

    with open(filename) as f:
        count = sum(1 for _ in f)

    print("D... total lines=",count)
    print("D... real start",start)

    print("D... basename = ",basename)
    if read_last>0:
        df = pd.read_table( filename, names=['time',"e",'x','ch','y'],
                        sep = "\s+", comment="#",
                        nrows = read_last,
                        skiprows=count-read_last)
                        #nrows = MAXROWS,
                        #skiprows=MAXROWS*batch)
    else:
        df = pd.read_table( filename, names=['time',"e",'x','ch','y'],
                        sep = "\s+", comment="#",
                        nrows = MAXROWS,
                        skiprows=MAXROWS*batch)

    return df


def fastread(filename, x=0, y=1, batch = 0, read_last=0, df = None, plot = False):
    """
    use: ./bin_readvme fast run0023_20200220_144753.asc 0 1  --read_last 500
    """
    TSHIFT = 20 # 10 seems ok, 20 is safe (200ns)
    TWIN = 2*TSHIFT
    CHAN0=x
    CHAN1=y
    ENE_0="chan_"+str(CHAN0)
    ENE_1="chan_"+str(CHAN1)
    MAXROWS = 1000*1000*35


    if df is None:
        df = only_read(filename, x,y,batch, read_last)

    # energy is marked "e"
    df = df.rename(columns={"e":ENE_0})


    if (len(df)<MAXROWS):
        print("X... END OF FILE REACHED ***")
        CONTINUE = False
    else:
        CONTINUE = True
    print("D... len=", len(df))
    df = shift_channels(df, TSHIFT, TWIN, x, y)
    print("D... len=", len(df) )


    print("D... SORTING BY TIME")
    df1=df.sort_values(by="time")
    df1.reset_index(inplace=True, drop=True)
    print("D... len=", len(df) )

    print(f"D... select channels {x},{y}")
    df1 = df1.loc[  (df1["ch"]==CHAN0)|(df1["ch"]==CHAN1) ]
    print("D... len=", len(df) )


    print("D... introducing shift differences")
    df1['prev'] = df1['time'] - df1.shift(1)['time']
    df1['next'] = - df1['time'] + df1.shift(-1)['time']

    print("D... len=", len(df1) , " dropping lonely events" )
    #df1 = df1[ (df1["prev"]<TWIN) | (df1["next"]<TWIN) ]
    df1 = df1[ (df1["prev"]<TWIN) | (df1["next"]<TWIN) ]


    print("D... len=", len(df1))

    if (1==0): # CHECK THE EVENTS IN WINDOW ========== NEXT IS GOOD
        dfnext = df1[ (df1["ch"]==0) & (df1["next"]<TWIN)]
        print("D... DF next", len(dfnext) )
        dfprev = df1[ (df1["ch"]==0) & (df1["prev"]<TWIN)]
        print("D... DF prev", len(dfprev) )


    df1[ENE_1] = df1.shift(-1)[ENE_0]
    # print(df1)

    print("D... dropping all when NEXT < ",TWIN )
    df2 = df1.loc[  df1["next"]<TWIN ]
    print( "D... len =",len(df2) )
    print("D...  window mean / 3sigma ... {:.1f} +- {:.1f}".format(df2.next.mean(),  3*df2.next.std() ))


    if CONTINUE:
        print(f"D... only {MAXROWS} read")
        print("X...  INCOMPLETE FILE, TRY TO READ batch=", batch+1)

    if plot:
        df2.plot.scatter(x=ENE_0,  y=ENE_1,
                     ylim=(0, 2000), xlim=(0,2000),
                     s=.01);
        plt.show()
        return

    return df2










def main1(filename,  od=0, do=9999999 , chan=1):
    """
    use: read_vme_offline cut1 filename_with_asc  60 120
    """
    # od = 0
    # do = 999999


    basename = os.path.basename(filename)
    basename = os.path.splitext(basename)[0]
    startd = basename.split("_")[1]
    startt = basename.split("_")[2]
    print("D...  time start MARK=",startd+startt)


    ok = False
    #try:
    start = dt.datetime.strptime(startd+startt,"%Y%m%d%H%M%S" )
    ok = True
    print("D... succesfull start with 4 digit year")
    #except:
    #    print("x... year may not by 4 digits")

    if not(ok):
        print("X... trying 2 digits for year")
        start = dt.datetime.strptime(startd+startt,"%y%m%d%H%M%S" )



    print("D... real start",start)
    od_dt = dt.timedelta(seconds=od)
    do_dt = dt.timedelta(seconds=do)
    print(f"D... skip     {od} sec ",od_dt)
    startcut = start + od_dt
    stopcut = start + do_dt
    print("D...  cut start",startcut)
    print("D...  cut stop ",stopcut)

    print(basename)
    df = pd.read_table( filename, names=['time','E','x','ch','y'], sep = "\s+", comment="#")
    print(df)

    print(f"D...  selecting events for  channel {chan} from {od}s to {do}s")

    ex = 1e+8
    # df1 = df[ (df.ch==chan)&(df.E!=0)&(df.time>ex*od)&(df.time<ex*do)  ]
    df1 = df[ (df.ch==chan)&(df.time>ex*od)&(df.time<ex*do)  ]
    #df2=df['E']
    #df3 = df2[ (df1.E!=0)  ]


    print(f"D...  numpy array for ch {chan}  ________________________CUT___________")
    df1.reset_index(inplace=True, drop=True)
    print(df1)

    dfzero = df1[ (df.E==0) ]
    df2 = df1[ df.E!=0 ]
    df2.reset_index(inplace=True, drop=True)


    print()
    print("i... ZEROES == ", len(dfzero))
    print("i... EVENTS == ", len(df2))
    deadtpr = len(dfzero)/len(df2) * 100
    fev = df1.time.iloc[0]/ex
    lev = df1.time.iloc[-1]/ex
    print(f"i... DT %   == {deadtpr:.2f}")
    # print(f"i... events == {fev} ... {lev}")
    # print(f"i... times  == {fev:.2f} ... {lev:.2f}")
    dift = lev - fev
    deadt = dift*deadtpr/100
    livet = dift - deadt

    stopcut = start + dt.timedelta(seconds=lev)

    print(f"i... times  == {fev:.2f} ... {lev:.2f}")
    print(f"i... real T == {dift:.2f} s")
    print(f"i... live T == {livet:.2f} s")
    print(f"i... dead T == {deadt:.2f} s")
    print(f"i... start  == {start} ")
    print(f"i... CUTsta == {startcut} ")
    print(f"i... CUTsto == {stopcut} ")
    # print(f"i... stop   == {stop} ")
    print()

    narr = df2.E.to_numpy()

    print(f"D...  creating histogram for channel {chan} from numpy")

    his,bins = np.histogram(narr,bins=1024*32,range=(0.0,1024*32) )
    print(his)
    print(bins)

    outfile = os.path.splitext(filename)[0]+".txt"
    print("D... outfile=", outfile)
    np.savetxt(outfile, his, fmt="%d")



if __name__=="__main__":
    print("D... fastread can be called too, from bin_readvme")
    Fire(main1)
