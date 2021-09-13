#!/usr/bin/env python3

#ROOT.gInterpreter.ProcessLine('#include "THttpServer.h"')


from fire import Fire
from read_vme_offline.version import __version__

import ROOT
import time

#import uproot
import pandas as pd
import os
import inotify
import inotify.adapters
import glob

from simple_read import fastread, only_read

CLEARME = 0

def fill_h2(df, h ):
    nrow,ncol = df.shape
    ## Fill array
    #print(df)
    params = []
    for c in df.columns:
        if c.find("_")>0:
            params.append(c)
    for index, row in df.iterrows():
        x = int(row[params[0]])
        y = int(row[params[1]])
        #print(x,y)
        h.Fill(x, y, 1)

    ## Finally
    return h


#takn from coin2edit.py
# follow2
def follow_lastfile(  ):
    """
    earlier version was watching completely every line of every file. now we only want the last file
    """
    global CLEARME
    datadir = os.path.expanduser("~/DATA/")
    syslog_file="a.asc"
    file_opened=False
    from_beginning = False
    notifier = inotify.adapters.Inotify()
    while True:  # 1st passage ever
        #print(datadir+'r*.asc')
        list_of_files = glob.glob(datadir+'r*.asc') # * means all if need specific format then *.csv
        # print( list_of_files )
        latest_file = max(list_of_files, key=os.path.getctime)
        #print("D.... LATEST ASC FILE==",latest_file)
        yield latest_file

        ##==================================== watching the ASDC file line by line with DUBNA
        # #syslog_file=latest_file

        # #try:
        # #------------------------- check
        # if not os.path.exists(syslog_file):
        #     print('D... file does not exist')
        #     time.sleep(1)
        #     continue
        # print("X... opening and starting to watch "+ syslog_file)
        # #------------------------- open
        # if not file_opened:
        #     file = open(syslog_file, 'r')

        #     if from_beginning:
        #         for line in file.readlines():
        #             #process(line, history=True)
        #             yield line
        # else:
        #     file.seek(0,2) # goto end of file
        #     #file.seek(0) # goto start of file
        #     from_beginning = True
        # #------------------------- watch
        # notifier.add_watch(syslog_file)  # ADDED THE FILE TO WATCH
        # #try:
        # for event in notifier.event_gen():  # this will loop over
        #     #try
        #     if event is None:
        #         #time.sleep(1)
        #         list_of_files = glob.glob('run*.asc') # * means all if need specific format then *.csv
        #         #print( list_of_files )
        #         latest_file = max(list_of_files, key=os.path.getctime)
        #         #print("D.... LATEST ASC FILE==",latest_file)
        #         if (syslog_file!=latest_file):
        #             CLEARME=1
        #             break

        #     if event is not None:

        #         (header, type_names, watch_path, filename) = event
        #         if set(type_names) & set(['IN_MOVE_SELF']): # moved
        #             print("X... syslog_file moved")
        #             notifier.remove_watch(syslog_file)
        #             file.close()
        #             time.sleep(1)
        #             #continue # continue leaves the watch stalled 2018-12-17
        #             break # we break, because we need new file assesment??
        #         elif set(type_names) & set(['IN_MODIFY']): # modified
        #             for line in file.readlines():
        #                 #process(line, history=False)
        #                 yield line
        #         elif set(type_names) & set(['IN_CLOSE_WRITE']): # modified
        #             print("D... SENDING  #END" )
        #             break
        #             yield "#END"





def main():
    """
    ROOT HTTP server with crafted COINC matrices
    """



    LASTN = 100*1000 # READ_LAST milion?
    #return
    s9009 = ROOT.THttpServer( "http:9009;global;top-BiDIM")

    #s9009.SetItemField("/", "_toptitle", "BiDIM")
    #s9009.SetItemField("/", "_layout", "vert3");
    s9009.SetItemField("/", "_monitoring", "1000");
    #s9009.SetItemField("/", "_drawopt", "[colz,hist]");

    #    s9009.SetTimer(100, False ) # Crashes - or rather stucks
    s9009.SetTimer(500, True ) # more stable

    h = ROOT.TH1F("myHist", "myTitle", 64*8, -4, 4)
    h.FillRandom("gaus",100)



    histo1 = ROOT.TH2F("de1p1"," 2d histogram",1000,0,6000,1000,0,6000)
    histo2 = ROOT.TH2F("de2p2"," 2d histogram",1000,0,6000,1000,0,6000)
    histo3 = ROOT.TH2F("de1e1"," 2d histogram",1000,0,6000,1000,0,6000)
    histo4 = ROOT.TH2F("de2e2"," 2d histogram",1000,0,6000,1000,0,6000)

    #s9009.Register("/" ,     h  )


    loglines = follow_lastfile()
    # HERE IS THE LASTFILE
    counter = 0
    for filename in loglines:
        counter+=1
        # filename = os.path.expanduser("~/DATA/run0022_20200220_143421.asc")
        print(f"D... FILE == {filename}")
        if "df" in locals():
            del df
        print("D... opening file ===============================",counter)
        df = only_read(filename , 0,1, batch=0, read_last = LASTN )
        #print(df)
        print("D... file done __________________________________")







        if "df1" in locals():
            del df1
        df1 = fastread(filename, 0,1, batch = 0, read_last = LASTN, df=df, plot=False)
        #print(df1)
        histo1.Reset("ICESM")
        fill_h2(df1,histo1)


        if "df2" in locals():
            del df2
        df2 = fastread(filename, 3,4, batch = 0, read_last = LASTN, df=df, plot=False)
        #print(df2)
        histo2.Reset("ICESM")
        fill_h2(df2,histo2)



        if "df" in locals():
            del df
        print("D... opening file ===============================",counter)
        df = only_read(filename , 0,1, batch=0, read_last = LASTN )
        #print(df)
        print("D... file done __________________________________")


        if "df3" in locals():
            del df3
        df3 = fastread(filename, 2,0, batch = 0, read_last = LASTN, df=df, plot=False)
        #print(df3)
        histo3.Reset("ICESM")
        fill_h2(df3,histo3)



        if "df4" in locals():
            del df4
        df4 = fastread(filename, 5,3, batch = 0, read_last = LASTN, df=df, plot=False)
        #print(df4)
        histo4.Reset("ICESM")
        fill_h2(df4,histo4)


        #print(histo2.GetSum())

        h.FillRandom("gaus", 15)
        #print(h.GetSum())
        # s9009.ProcessRequests()
        nmax=9
        while nmax>0:
            time.sleep(1)
            print(f"D... sleeping ........ {nmax}")
            nmax-=1

if __name__=="__main__":
    Fire(main)
