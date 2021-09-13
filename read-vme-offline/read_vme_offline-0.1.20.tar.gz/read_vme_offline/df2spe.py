#!/usr/bin/env ipython
"""
I have only one funtion here; convert...
# needs lot of stuff:

sudo -H apt install texlive-latex-extra

"""
from fire import Fire
from read_vme_offline.version import __version__

#print("i... module read_vme_offline/df2spe is being run")
#print("i...   I NEED:  root_numpy pylatex")
import pandas as pd
import tables # here, to avoid a crash when writing pandas
import h5py


import ROOT
#%jsroot on
from ROOT import TH1F, TCanvas, TSpectrum, TH1D, TPolyMarker
import root_numpy
#------------------------------ pythons import
import pandas as pd
import matplotlib.pyplot as plt
#%matplotlib inline
import numpy as np
import math
from matplotlib.colors import LogNorm
import time


import pylatex
from pylatex import Document, Section, Subsection, Command
from pylatex.utils import italic, NoEscape
from pylatex import Document, Section, Subsection, Tabular, Math, TikZ, Axis,Plot, Figure, Matrix, Alignat, Table, Label, Ref
from pylatex.utils import italic
from pylatex.package import Package

import os

import gc

from tabulate import tabulate


import pathlib




# ------------------------------- called from main convert
def convert_piece( df, df_stat, allhistos, Ethres, Emax, channel, timewin ):
    """
    df is source;
    df_stat ... collect information;
    allhistos ... dictionary == root histograms
    Ethres = like 1,2 - bellow is noise
    Emax = above are overflows....
    """

    # select event from channel==channel


    # SELECT ONE CHANNEL
    dfca = df.loc[ df['c']==channel ].copy()

    # CREATE COLUMN WITH dt [us]
    dfca['dtus'] = (dfca.t-dfca.t.shift())*1000*1000
    dfca[0,'dtus']=0
    # MODIFIED DF....DFM
    # ----------extend the dataframe with next line values-----
    # and double the columns of the DataFrame with next_
    dfm = pd.concat([dfca, dfca.shift(-1).add_prefix('next_')], axis=1)

    #====================== start selections

    nonz= dfm[ ( dfm['E']> 0)   ]  # nonzero

    #-------these are 4 regions of apocalypse-------------
    zero= dfm[ ( dfm['E']==0)  ]  # zero
    nois= dfm[ ((dfm['E']<=Ethres) & (dfm['E']>0) )        ]  # E>0 but low E:  noise under Threshold
    good= dfm[ ((dfm['E']>Ethres) & (dfm['E']<Emax )  )   ]  # good E>0==Ethres  above Threshold
    ovfl= dfm[ ( dfm['E']>= Emax)  ]  # ovfl



    #    dfm = pd.concat([dfca, dfca.shift(-1).add_prefix('next_')], axis=1) # already done

    # ----------- calculate double / single / stanalone zeroes
    aldbl = dfm.loc[ (dfm.next_dtus<timewin) ]
    ddz   = dfm.loc[ ((dfm.E==0) & (dfm.next_E==0)) & (dfm.next_dtus<timewin) ]
    ssz   = dfm.loc[ ((dfm.E>0) & (dfm.next_E==0)) & (dfm.next_dtus<timewin) ]
    isz   = dfm.loc[ ((dfm.E==0) & (dfm.next_E>0)) & (dfm.next_dtus<timewin) ]  #inverted singlezero

    # standalone zeroes NUMBER
    stazero = len(zero)-len(ssz)-len(ddz)


    # --------------------------- first and last times ----------------
    ftime = dfm['t'].iloc[0]
    ltime = dfm['t'].iloc[-1]

    # ------------------------------------- enter into table --------in convertpiece
    tota= len(dfm)
    df_stat.loc[len(df_stat)] = np.NaN
    print(".... dfstat chan==", channel)
    df_stat.loc[len(df_stat)-1 ,'ch']  = int(channel)
    df_stat.loc[len(df_stat)-1 ,'Total']  = tota
    df_stat.loc[len(df_stat)-1 ,'Good']   = len(good)
    df_stat.loc[len(df_stat)-1 ,'NonZero']= len(nonz)
    df_stat.loc[len(df_stat)-1 ,'Zero']   = len(zero)
    df_stat.loc[len(df_stat)-1 ,'Noise']   = len(nois)
    df_stat.loc[len(df_stat)-1 ,'Ovfl']   = len(ovfl)
    df_stat.loc[len(df_stat)-1 ,'Sgl0']   = len(ssz)
    df_stat.loc[len(df_stat)-1 ,'Dbl0']   = len(ddz)
    df_stat.loc[len(df_stat)-1 ,'Stand0']   = stazero
    df_stat.loc[len(df_stat)-1 ,'FTime']   = ftime
    df_stat.loc[len(df_stat)-1 ,'LTime']   = ltime

    #df_stat['T:NZ_Z'] = df_stat['NonZero'] + df_stat['Zero'] - df_stat['Total']
    #df_stat['T:NOG'] = df_stat['Noise'] + df_stat['Ovfl'] + df_stat['Good'] + df_stat['Zero'] - df_stat['Total']

    # at the end.
    # df_stat['DT'] = df_stat['Zero']/df_stat['Total']*100
    # df_stat['DT'] = df_stat.DT.apply(lambda x: round(x, 2))


    #---------------------- FILLING HISTOGRAMS
    histoname="chan{:02.0f}".format(channel)
    root_numpy.fill_hist( allhistos[histoname], nonz['E'].to_numpy() )


    histoname="erlang{:02.0f}".format(channel)
    root_numpy.fill_hist( allhistos[histoname], dfm['dtus'].to_numpy() )
    histoname="_erlang{:02.0f}_good".format(channel)
    root_numpy.fill_hist( allhistos[histoname], good['dtus'].to_numpy() )

    # zeroes Erlang
    histoname="erlZeroes{:02.0f}".format(channel)
    root_numpy.fill_hist( allhistos[histoname], aldbl['next_dtus'].to_numpy() ) # alz==all DBL events
    histoname="_erlZeroes{:02.0f}_s".format(channel)
    root_numpy.fill_hist( allhistos[histoname], ssz['next_dtus'].to_numpy() )
    histoname="_erlZeroes{:02.0f}_d".format(channel)
    root_numpy.fill_hist( allhistos[histoname], ddz['next_dtus'].to_numpy() )


    # zeroes run time distr
    histoname="distrTwoZeroes{:02.0f}".format(channel)
    root_numpy.fill_hist( allhistos[histoname], aldbl['t'].to_numpy() )  # alz==all double
    histoname="_distrTwoZeroes{:02.0f}_s".format(channel)
    root_numpy.fill_hist( allhistos[histoname], ssz['t'].to_numpy() )
    histoname="_distrTwoZeroes{:02.0f}_d".format(channel)
    root_numpy.fill_hist( allhistos[histoname], ddz['t'].to_numpy() )
    histoname="_distrTwoZeroes{:02.0f}_i".format(channel)
    root_numpy.fill_hist( allhistos[histoname], isz['t'].to_numpy() )


    histoname="distr_in_time{:02.0f}".format(channel)
    root_numpy.fill_hist( allhistos[histoname], dfm['t'].to_numpy() )
    histoname="_distr_in_time{:02.0f}_z".format(channel)
    root_numpy.fill_hist( allhistos[histoname], zero['t'].to_numpy() )
    histoname="_distr_in_time{:02.0f}_o".format(channel)
    root_numpy.fill_hist( allhistos[histoname], ovfl['t'].to_numpy() )




    return     # ------- leave convert_piece -----------------------------------------------------








# -----------------------------------------MAIN CONVERT-----------------#
# def convert(filename, Ethres=0.0, Emax=16382*2, channel=0, timewin=30, maxmemmega=50):
def convert(filename, Ethres=1.0, Emax=16382*2, timewin=30, maxmemmega=150):
    """
     50MEvents - ~ 20GB of memory needed
    """

    print("="*70)
    print("               Conversion  h5 to spectra and org : ", filename )
    print("_"*70)
    print("   ls -1 *.h5 | xargs -n 1 -I III  read_vme_offline df2s III --Emax 15200 --Ethres 5  ")
    print()


    # ----- prepare filename and temp files
    # pdfname=os.path.splitext(filename)[0]+".pdf"

    pdfname=os.path.splitext(filename)[0]
    fig1="temp_"+pdfname+"_1.jpg"
    fig2="temp_"+pdfname+"_2.jpg"
    fig3="temp_"+pdfname+"_3.png"
    fig4="temp_"+pdfname+"_4.jpg"
    fig5="temp_"+pdfname+"_5.jpg"


    # ----------------------- MAIN STATISTICS TABLE --------------------
    df_stat=pd.DataFrame(columns=['ch','Total','NonZero','Good','Zero',
                                  'Noise','Ovfl',
                                  'Sgl0','Dbl0','Stand0',
                                  'FTime','LTime'] )
    # ------------ histograms ----------------------- CREATION-------
    allhistos={}

    # pd.set_option('display.height', 10)
    pd.set_option('display.max_rows', 10)
    # print("D... -------- NUMBER TYPES IN H5:\n", df.dtypes)

    #----------------------------------- open 1st time
    df=pd.read_hdf(filename ) # READ FILE
    dflen = len(df)

    print("_"*45,"info: df length=", dflen)
    df.info()
    print("_"*45,"info")


    allchans=df['c'].unique() # detect channels inside:
    print("i... channels:",sorted(allchans) )

    del df
    gc.collect()
    df=pd.DataFrame()
    print("D... memory cleared")
    # -------------------------------------- close





    print("D... creating histograms...", end = "")
    # ---------------------------------------------------------------------- create HISTOS
    for ca in np.sort(allchans):
        # HISTO -------
        histoname="chan{:02.0f}".format(ca)
        if histoname not in allhistos:
            h1 = TH1D( histoname, ' '+filename+'; channel', 32768, 0, 32768 )
            allhistos[ histoname ] = h1


        histoname="distr_in_time{:02.0f}".format(ca)
        if histoname not in allhistos:
            h1 = TH1D( histoname, ' '+filename+'; t [s]; allevts, zeroes_red, ovfl_magenta', 32768, 0, 32768 )
            allhistos[ histoname ] = h1

        histoname="_distr_in_time{:02.0f}_z".format(ca)  # SILENTLY - not parsed in keys
        if histoname not in allhistos:
            h1 = TH1D( histoname, ' '+filename+'; t [s]', 32768, 0, 32768 )
            allhistos[ histoname ] = h1

        histoname="_distr_in_time{:02.0f}_o".format(ca)  # SILENTLY - not parsed in keys
        if histoname not in allhistos:
            h1 = TH1D( histoname, ' '+filename+'; t [s]', 32768, 0, 32768 )
            allhistos[ histoname ] = h1



        # HISTO ------- pure erlang - long
        histoname="erlang{:02.0f}".format(ca)
        if histoname not in allhistos:
            h1 = TH1D( histoname, ' '+filename+'; dt [us]; all evts, good evts', 32768, 0, 32768 )
            allhistos[ histoname ] = h1

        # HISTO -------
        histoname="_erlang{:02.0f}_good".format(ca)
        if histoname not in allhistos:
            h1 = TH1D( histoname, ' '+filename+'; dt [us]', 32768, 0, 32768 )
            allhistos[ histoname ] = h1



        # HISTO ------- erlangZeroes - short
        histoname="erlZeroes{:02.0f}".format(ca)
        if histoname not in allhistos:
            h1 = TH1D( histoname, ' '+filename+'; dt [us];allevents_blue,singleZero_red,doubleZero_green', 32768, 0, 32768 )
            allhistos[ histoname ] = h1

        # HISTO -------
        histoname="_erlZeroes{:02.0f}_s".format(ca)
        if histoname not in allhistos:
            h1 = TH1D( histoname, ' '+filename+'; dt [us]', 32768, 0, 32768 )
            allhistos[ histoname ] = h1

        # HISTO -------
        histoname="_erlZeroes{:02.0f}_d".format(ca)
        if histoname not in allhistos:
            h1 = TH1D( histoname, ' '+filename+'; dt [us]', 32768, 0, 32768 )
            allhistos[ histoname ] = h1



        # HISTO ------- timedistr Zeroes
        histoname="distrTwoZeroes{:02.0f}".format(ca)
        if histoname not in allhistos:
            # h1 = TH1D( histoname, ' '+filename+'; t [s];AllTwinEvents_blue,SingleZ_red,DoubleZ_grn,InvSnglZ_mgnta', 32768, 0, 32768 )
            h1 = TH1D( histoname, ' '+filename+'; t [s];AllTwinEvents_blue,SingleZ_red,DoubleZ_grn', 32768, 0, 32768 )
            allhistos[ histoname ] = h1

        # HISTO -------
        histoname="_distrTwoZeroes{:02.0f}_s".format(ca)
        if histoname not in allhistos:
            h1 = TH1D( histoname, ' '+filename+'; t [s]', 32768, 0, 32768 )
            allhistos[ histoname ] = h1

        # HISTO -------
        histoname="_distrTwoZeroes{:02.0f}_d".format(ca)
        if histoname not in allhistos:
            h1 = TH1D( histoname, ' '+filename+'; t [s]', 32768, 0, 32768 )
            allhistos[ histoname ] = h1

        # HISTO -------
        histoname="_distrTwoZeroes{:02.0f}_i".format(ca)
        if histoname not in allhistos:
            h1 = TH1D( histoname, ' '+filename+'; t [s]', 32768, 0, 32768 )
            allhistos[ histoname ] = h1





    print("D...  histograms created:", len(allhistos) )
    #print("_"*50)
    #print()
    i0=0
    part=1
    print("i... reading file in {} MB parts:".format(maxmemmega) )

    # IF more then 1 part => goes here
    for i in range(0,dflen,maxmemmega*1000*1000):
        if i==0:
            continue
        print("D1... reading event range {} - {}".format(i0,i) )
        df=pd.read_hdf(filename, where='(index>={}) and (index<{})'.format(i0,i) ) # READ FILE
        i0=i


        for ca in np.sort(allchans):
            print("D... PART {:3d}  CHANNEL=={}".format( part, ca) , end="               \r" )
            convert_piece( df, df_stat, allhistos, Ethres, Emax, ca , timewin )
            part+=1

            del df
            gc.collect()
            df=pd.DataFrame()
            print("D... ....................................memory cleared, part #", part)

    #print("D... all parts done_____________________________")

    # IF only ONE PART => goes here
    if i<dflen:
        print("D2... reading event range {} - {} ... the last PART".format(i,dflen) )
        df=pd.read_hdf(filename, where='(index>={}) and (index<{})'.format(i,dflen) )

        # PROCESS HERE
        allchans=df['c'].unique() # detect channels inside:
        for ca in np.sort(allchans):
            print("D... PART {:3d}  CHANNEL #{}".format( part, ca) , end="               \r"  )
            convert_piece( df, df_stat, allhistos, Ethres, Emax, ca, timewin )

    print("\n","_"*45," ALL PROCESSED, everything converted.")



    # df_stat = df_stat.sum(axis=0)
    # sums = pd.Series(df_stat['Total'].sum(), index = ['Total'])
    # df_stat.append(sums,ignore_index=True)
    # df_stat.select_dtypes(pd.np.number).sum().rename('total')
    # df.loc['total'] = df.select_dtypes(pd.np.number).sum()

    df_stat.loc['TOT'] = df_stat.sum()

    df_stat.loc['TOT','ch'] = np.NaN

    df_stat.loc['TOT','FTime'] = np.NaN
    df_stat.loc['TOT','LTime'] = np.NaN
    df_stat.loc['TOT','FTime'] = df_stat.FTime.min()
    df_stat.loc['TOT','LTime'] = df_stat.LTime.max()


    # --------------------- operations on columns crosscheck
#    df_stat['xchkZ'] = df_stat['NonZero'] + df_stat['Zero'] - df_stat['Total']
#    df_stat['xchkT'] = df_stat['Noise'] + df_stat['Ovfl'] + df_stat['Good'] + df_stat['Zero'] - df_stat['Total']

    df_stat['DeadT'] = df_stat['Zero']/df_stat['Total']*100
    df_stat['DeadT'] = df_stat.DeadT.apply(lambda x: round(x, 2))

    df_stat['FTime'] = df_stat.FTime.apply(lambda x: round(x, 1))  # first event time
    df_stat['LTime'] = df_stat.LTime.apply(lambda x: round(x, 1))  # last event time


    df_stat['noisPr'] = df_stat['Noise']/df_stat['Total']*100
    df_stat['cps'] = df_stat['Total']/df_stat['LTime']

    df_stat['noisPr'] = df_stat.noisPr.apply(lambda x: round(x, 1))
    df_stat['cps'] = df_stat.cps.apply(lambda x: int(round(x, 0)))




    #print("_"*50)
    #----------------------------------_ ORGTABLE----------------------******************

    nicename = os.path.splitext(filename)[0].replace("_","-" )
    picfolder = './pic_'+nicename
    pathlib.Path(picfolder).mkdir(parents=True, exist_ok=True)
    rootfile = nicename+".root"

    #---------------------- list of all histograms:

    org_content=[]

    print()
    print()

    org_content.append( "#+LATEX_HEADER: \\usepackage[margin=0.5in]{geometry} ")
    org_content.append( "#+latex_class_options: [10pt]")

    org_content.append( "*Thing to check* ")
    org_content.append( " - check the number of /E/ bits written to disk 14 or 15 ? (16000 or 32000)")
    org_content.append( " - the format of data written : /t E eshif Chan xtra/ OR /t E eshift Chan/")
    org_content.append( " - the h5 format after the conversion ")

    org_content.append( "** "+os.path.splitext(filename)[0].replace("_","-" ) )
    print()

    org_content.append( "#+NAME:{}".format( os.path.splitext(filename)[0]) )
    org_content.append( '#+LATEX:\\footnotesize' )
    #print(df_stat) # summary collected during the time
    org_content.append( tabulate(df_stat, headers="keys", tablefmt="orgtbl") )
    org_content.append( f"""
   - Ethres = {Ethres}
   - Emax   = {Emax}
   - good :   Ethres < Xover < Emax
   - noise:   0< X <=Ethrs
   - ovfl :   Emax <= X
   - Zero  = Sgl0 + Dbl0 + Stand0
   - Total = NonZero+Zero = Zero+Noise+Good+Ovfl
   - FTime ... first event arrival time
   - LTime ... last event arrival time
""")
    org_content.append( '#+LATEX:\\normalsize' )

    # Set up canvas :
    w = 1400
    h =  700
    can  = TCanvas("can", "histograms   ", w, h)

    #include "TError.h"
    ROOT.gInterpreter.ProcessLine('#include "TError.h"')

    #gErrorIgnoreLevel = ROOT.kWarning;
    ROOT.gErrorIgnoreLevel = ROOT.kFatal



    sections={'chan':"*** Spectra - channels",
              'distr_in_time':"*** Time ditribution - T",
              'erlang':"*** Erlang distributions - deltaT",
              'erlZero':"*** Erlang Zeroes spectra - deltaT",
              'distrTwoZero':"*** time distributed zeroes spectra - T",
    }
    f = ROOT.TFile.Open( rootfile, "UPDATE")
    for i in sorted(allhistos.keys()):
        if i[0]=="_":
            continue
        HNAME = allhistos[i].GetName()
        for j in list(sections.keys()):
            if HNAME.find(j)==0:
                org_content.append( sections[j] )
                sections.pop(j, None)

        # allhistos[i].Print()
        allhistos[i].Write()
        allhistos[i].Draw()
        # second hitogram on
        if HNAME.find("chan")>=0:
            allhistos[i].GetXaxis().SetRange(0, int(Emax)+2000 )
        if HNAME.find("distr_in_time")>=0:
            # limit to RUN Time
            allhistos[i].GetXaxis().SetRange(0, int(df_stat.LTime.max()+2) )
            _hname = "_"+i+"_z"
            allhistos[_hname].Draw("SAME")
            allhistos[_hname].SetLineColor(2)
            allhistos[_hname].Write()

            _hname = "_"+i+"_o"
            allhistos[_hname].Draw("SAME")
            allhistos[_hname].SetLineColor(6) # magenta ovfl 4blue 5yellow 6mage
            allhistos[_hname].Write()



        if HNAME.find("erlang")>=0:
            _hname = "_"+i+"_good"
            allhistos[_hname].Draw("SAME")
            allhistos[_hname].SetLineColor(3)
            allhistos[_hname].Write()

        if HNAME.find("erlZeroes")>=0:
            # limit to timewin 30us)
            allhistos[i].GetXaxis().SetRange(0, 2*int(timewin) )
            _hname = "_"+i+"_s"
            allhistos[_hname].Draw("SAME")
            allhistos[_hname].SetLineColor(2)
            allhistos[_hname].Write()

            _hname = "_"+i+"_d"
            allhistos[_hname].Draw("SAME")
            allhistos[_hname].SetLineColor(3)
            allhistos[_hname].Write()

        if HNAME.find("distrTwoZeroes")>=0:
            # Run Time limit
            allhistos[i].GetXaxis().SetRange(0, int(df_stat.LTime.max()+2) )
            _hname = "_"+i+"_s"
            allhistos[_hname].Draw("SAME")
            allhistos[_hname].SetLineColor(2)
            allhistos[_hname].Write()

            _hname = "_"+i+"_d"
            allhistos[_hname].Draw("SAME")
            allhistos[_hname].SetLineColor(3)
            allhistos[_hname].Write()

            #_hname = "_"+i+"_i"    # should be just like noise
            #allhistos[_hname].Draw("SAME")
            #allhistos[_hname].SetLineColor(6) # 6magenta inverted

        can.SetGridx()
        can.SetGridy()
        can.SetLogy()
        can.Update()      # Shows the histogram in the Canvas without having to click on it.
        picname = picfolder+"/"+HNAME+".png"
        can.SaveAs(picname)

        org_content.append( "  [[file:"+picname+"]]")
    f.Close()

    with open(nicename+".org","w") as f:
        f.write("\n".join(org_content) )
    print( "\n".join(org_content) )
    return
#======================================================================================
#======================================================================================
#======================================================================================
#======================================================================================
#======================================================================================




if __name__=="__main__":
    #print("D... in main of project/module:  read_vme_offline/df2spe ")
    #print("D... version :", __version__ )
    Fire()
    #Fire({"convert": convert })
