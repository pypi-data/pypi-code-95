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
#>>> import pandas as pd
#>>> import matplotlib.pyplot as plt
#>>> df=pd.read_hdf("run0001_20200526_102519.h5")
#>>> plt.hist( df['E'][  (df.xx=0) & ( (df.t-df.t.shift())<0.0001) ] , 1024, range=[0,2048] )
# plt.show()
#
#


import time

#import alive_progress
from alive_progress import alive_bar,config_handler

# memory sizes
from pympler import asizeof

#from memory_profiler import profile
#import gc

##############################################################################
#
#
def get_nice_time(tnanotext):
    #return datetime.timedelta(seconds= int(tnanotext)/1e8 )
    print( "D.gnt.. seconds={:16s}".format( str(int(tnanotext)/1e+8 ) ) )
    secs=int(  int(tnanotext)/1e+8  )
    #print(secs)
    h=int(secs/3600)
    rem=secs % 3600
    #print("D... H ",h,rem)
    m=int(rem/60)
    rem=rem % 60
    #print("D... M ",m,rem)
    s=int(rem)
    #print("D... S ",s,rem)
#    return h
    return "{:02d}:{:02d}:{:02d}".format( h,m,s )





##############################################################################
#
#
def print_progress( columns, i, eol="\r",  zero=-1 , nonzero=-1, silent=False):
    out=">  {} sec {:5.1f}Mevts {} ... DT~ {:.2f} %   ".format(  datetime.timedelta(seconds= columns[0]/1e8 ),
                                                                       i/1000000,
                                                                       columns,
                                                                       zero/(zero+nonzero)*100)
#    if not silent:
#        st.write( out )
    print(out, end=eol)






##############################################################################
#
#
def extract_start(filename):
    f=filename.split(".asc")[0]
    print("D...exs... filename to extract:", f)
    startok = False
    try:
        da=f.split("_")[1]
        ti=f.split("_")[2]
        #print("D... ",da,ti)
        start=datetime.datetime.strptime( da+ti,"%Y%m%d%H%M%S" )
        print("D.ex... start time=",start)
        startok = True
    except:
        start=datetime.datetime.now()
        print("i... cannot say the beggining time from filename")


    # i also probe one line before the end
    linemin = sp.check_output(['tail', '-2', filename]).decode("utf8").split("\n")[0]
    print("D.... BEFORE LASTLINE ={:16s}".format(linemin))

    line =    sp.check_output(['tail', '-1', filename]).decode("utf8")
    print("D....        LASTLINE ={:16s}".format(line))

    if int( linemin.split()[0] ) > int( line.split()[0] ):
        line=linemin
        print("X...  ... incomplete file probably? ... taking before last line")
    real=get_nice_time( line.split(" ")[0] )


    print("i... measuring number of lines of the file...")
    ps = sp.Popen( ['cat', filename], stdout=sp.PIPE)
    output = sp.check_output(('wc', '-l'), stdin=ps.stdout)
    ps.wait()
    nlines=int(output.decode("utf8").split()[0])

    # ========================
    print("_"*50)
    print("D...                     File :",filename)
    if startok:
        print("D...               start time =", start)
    else:
        print("D...               start time =", "unknown")
    print("D...                real time =",real)


    print("D....   lines in file:        = {:.3f} M  ({})".format(nlines/1000000,  nlines) )
    print("_"*50)
    print()

    return start,real, float(line.split(" ")[0])/1e+8, nlines






###############################################################
#
#
#
#

def convert(filename):
    """
    convert asc file into h5 file
     - see the progress
    """
    print("="*70)
    print("               Conversion to h5 : ", filename )
    print("_"*70)
    print("   ls -1 *asc | xargs -n 1 -I III  read_vme_offline a2df III")
    print()
    #========================= CREATE DF


    #==========================
    zero=0
    nonzero=1
    #---------------------------------- taken from z_speread
    start,real,lastsec,nlines=extract_start( filename ) # real....
    # WORKS OK    3.5MEvts  for 15 seconds
#    df = pd.DataFrame( columns=['t','E','c','x','xx'], index=np.arange(nlines), dtype=np.float64)
    # WORKS -    3.5 MEvts for 15 sec.  (38 if int

    print("i... I am allocating memory for {:.3f} milion lines".format(nlines/1000000) )
    # Here I preallocate the memory !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # python 3.8, numpy 1.20 -------change np. to nothing  2021 02 22
    df = pd.DataFrame( {'t':pd.Series( np.arange(nlines),dtype=np.float64),
                        'E':pd.Series( np.arange(nlines),dtype=np.int16),
                        'Eshift':pd.Series( np.arange(nlines),dtype=np.int8),
                        'c':pd.Series( np.arange(nlines),dtype=np.int8),
                        'xx':pd.Series( np.arange(nlines),dtype=np.int8),
                        } )
    #        columns=['t','E','c','x','xx'], index=np.arange(nlines), dtype=np.float64)

    print(df.memory_usage())
    print("i... INITIAL TYPES in dataframe:")
    print(df.dtypes," \n\n")
    s1=0
    s2=lastsec+10
    #s2=2
    lastline=True # print the last liine
    firstline=True

    print("M... df_size=/{:.1f}/ G  ".format(asizeof.asizeof( df )/1024/1024/1024 ) )


    #============================== taken from z_speread-----------
    with open(filename,"r") as f:
        ii=0
        i=0
        line=f.readline()
        endoffile=False

        with alive_bar( nlines) as bar:
            #============================================== i==0 now
            while line:
                bar()
                if line.find("#")>=0:
                    line=f.readline()
                    continue # freadline +continue
                if line.find("H")>=0:
                    line=f.readline()
                    continue # freadline +continue
                ii=ii+1
                #bar()
                #================================== decompose the line here
                columns = line.split()
                columns = [ int(i) for i in columns ]
                #----define columns=============
                #secs=datetime.timedelta(seconds= columns[0]/1e8).total_seconds()
                secs=columns[0]/1e8

                # We had a problem with a bad data format ??? but we comment it now.......
                #if secs>lasttimemark*10:#  we have seen an error - 10x bigger time next event
                #    line =f.readline()
                #    continue # freadline +continue


                try:
                    energy= int(columns[1] )
                    if energy==0:
                        zero+=1
                    else:
                        nonzero+=1

                except:
                    endoffile=True
                try: #-------------Eshift>>MAXBITS
                    xtrapu= int( columns[2] )
                except:
                    endoffile=True

                if endoffile:
                    print("D.... END OF FILE ... BREAK")
                    break
                # --------- read even from mc2 file - it has NO column #3 with channel present.
                try:
                    channel= int( columns[3] )
                except:
                    channel=0
                try: #--------------------- in the new gregory (2020/02) WE print one more xtra COLUMN
                    xxtra= int( columns[4] )
                except:
                    xxtra=0
                #=======================================decomposed=========

                #=======================first last printouts-================
                if firstline:
                    print("the first event of the file:")
                    print_progress( columns,i , "\n" , zero,nonzero )
                    firstline=False
                if secs < s1:
                    real2a=secs # reset the start time allthetime
                    line =f.readline()
                    continue # freadline +continue
                if secs>s2:
                    if lastline:
                        print("\nthe last event of the time selection:")
                        print_progress( columns,i , "\n" , zero,nonzero )
                        real2b=secs
                        lastline=False # dont print the last line anymore
                    line =f.readline() # freadline +continue
                    print("D...  time is over the s2, BREAK")
                    break
                    #continue

                else: #======= REAL COUNTING FROM HERE ===================
                    if i==0:
                        print("\nthe first event of the time selection:")
                        print_progress( columns,i , "\n" , zero,nonzero )
                        #====== INITIALIZE DFBIS
                        dfbis=[]
                    i=i+1
                    #bar()

                #========= === === == = = = = = = == = = = = = =  = = =
                #========= === === == = = = = = = == = = = = = =  = = =
                #  ENTER TO DF   ,   dfbis==list
                #========= === === == = = = = = = == = = = = = =  = = =
                #========= === === == = = = = = = == = = = = = =  = = =
                dfbis.append( [ np.float64(secs), np.int16(energy),  np.int8(xtrapu), np.int8(channel) ,np.int8(xxtra) ] )

                #print( "{}   i={}     nlines={}".format(len(dfbis),  i,   nlines) )
                #                  no typing         np.typing
                # DF2LEN=1000     # 15.68s              2:38:00 /40MEvs
                # DF2LEN=10000    # 14.46s / 3.5M            17:20
                # DF2LEN=30000    # 14.46s / 3.5M               7:00
                # DF2LEN=100000   #                           3:25
                # DF2LEN=300000   #                           2:45
                DF2LEN=1000000  #                            2:20
                # DF2LEN=3000000  #                            2:10
                if i% DF2LEN==0:
                    # print("D... batch full")
                    # i is already 1 OR MORE.......
                    # start of the LIST is CORRECT
                    # I must put from backwords
                    l1=len(dfbis)
                    l2b=(i-1+1)
                    l2a= (i-1-DF2LEN+1)
                    if l2b-l2a!=l1 : #the last in range is not
                        print("##",l1,"################# D2FLEN ###  NOT #### SAME ### AS ### RANGE ##### ",l2a," ... ",l2b)

                    df.loc[ range( l2a , l2b ), df.columns  ] = dfbis
                    print_progress( columns,i , "\r" , zero,nonzero, silent=True )
                    #bar()
                    #print( df.memory_usage() )
                    #print(df.dtypes," \n\n")

                    #df.loc[ range( l2a , l2b ), df.columns ]=dfbis
                    #del dfbis
                    #gc.collect()
                    dfbis=[]




                #================= PRINTOUTS================================
                #print(ii, end="\r")
                #if ii%(1000*1000)==0:
                #    print_progress( columns,i , "\r" , zero,nonzero, silent=True )

    #================================= READ AT THE END ====================
                line=f.readline()





        #==================== end of processing ==== only a last batch
        #==================== end of processing ==== only a last batch
        #==================== end of processing ==== only a last batch
        # LAST BATCH OF DF2 data ===========================================
        #@
        if len(dfbis)>0:
            l1=len(dfbis)
            print( "... dfbis 0",dfbis[0] )
            print( "... dfbis-1",dfbis[-1] )
            l2b=(i-1)
            l2a= (i-1-len(dfbis)+1)
            if l2b-l2a!=l1 : #the last in range is not
                print("##",l1,"###LAST########## D2FLEN ###  NOT #### SAME ### AS ### RANGE ##### ",l2a," ... ",l2b)
            # I must put from backwords
            #df.loc[ range(i-1-len(dfbis)+1, i-1+1), df.columns ]=dfbis
            df.loc[ range(l2a, l2b+1), df.columns ]=dfbis
            print(df.dtypes," TYPES HAVE PROBABLY CHANGED... ...")

            dfbis=[]


        print("D... Now I change types back ...")
        df = df.astype({"E":np.int16, "c": np.int8, "Eshift": np.int8, "xx":np.int8})
        OUTNAME='database.h5'
        OUTNAME=filename.replace(".asc",".h5")

        print("D... predicted columns: {} , really columns: {}".format(nlines,i))
        if nlines!=i:
            df.drop(df.tail(nlines-i).index,inplace=True) # drop last n rows
        #WORKS-----------
        print("D... sorting:      {}".format( "dataframe" )  )
        df.sort_values(by='t',ascending=True, inplace=True)
        df.reset_index(drop=True, inplace=True)



        # savepart=1
        # i0 = 0
        # for i in range(0,len(df), 1000*1000):
        #     itemname = filename.replace(".","_")+str(savepart)
        #     print("D... saving to .h5: {} -  {}-{}/{}   name={}".format(
        #         OUTNAME, i0,i , len(df) , itemname )
        #     )
        #     df.iloc[ i0:i ,: ].to_hdf( OUTNAME , itemname ,  mode='a')
        #     savepart+=1
        #     i0 = i
        # print("i... All parts saved")

        itemname = filename.replace(".","_")
        # I need to save with format TABLE -
        #     to be able to read part of the DF later
        df.to_hdf( OUTNAME , itemname ,  mode='a', format='table')


        #print()#=====keep last line
        print_progress( columns,i , "\n" , zero,nonzero, silent=True )
        print(df)

        sort_data = False
        if sort_data == True:
            # print("+++++++++++++++++SORTING...: ++++++++")
            print("+++++++++++++++++just look at these sorted: ++++++++")
            print(df.sort_values(by=['E','t'],ascending=True))
            #print("+++++++++++++++++good bye+++++++++++++++++++++++++++")
            #        print( df.loc[0]['t'] )
            #        print( df.loc[1]['t'] )
            #        print( df.loc[-2]['t'] )
            #        print( df.loc[-1]['t'] )
        print("... verify with:\n      tdb_io ls ",OUTNAME )
        print(df.dtypes ," FINAL DTYPES")



if __name__=="__main__":
    #print("D... in main of project/module:  read_vme_offline/ascdf ")
    #print("D... version :", __version__ )
    Fire({"convert": convert })
