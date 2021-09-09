import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from . import backend as be

def data(trange=['2021-01-01/00:00','2021-01-02/00:00'], filename=None, lognumbers=[], level='3', numpy=False):
    """
    Read dosimeter data from TFTP server or local file into `pandas` dataframe or `numpy` array.

    ### Parameters
    * trange : string array-like, optional
        >Time range of dosimeter data to download from the TFTP server. Format 'YYYY-MM-DD/HH:MM' in UTC.
        Default `['2021-01-01/00:00','2021-01-02/00:00']`.
    * filename : str, optional
        >Name of DSFS logfile to read. Only specify if you have a local CuPID binary file you want to read.
        Overrides `trange` if specified. Default `None`.
    * lognumbers : int, array-like, optional
        >Lognumber(s) of DSFS logfiles being read. Only specify if you have a local CuPID binary file you want to read and sync to UTC time.
        Default `[]`.
    * level : str, optional
        >Data processing level of dosimeter data to download. Only specify if data is to be downloaded. Options:
        >
        >     '1' : Level 1 data (time in onboard payload time)
        >
        >     '2': Level 2 data (time in UTC)
        >
        >     '3': Level 3 data (time in UTC, rates calculated)
        >
        >If time sync fails for manually processed file when level 2 specified, returned data uses the mission elapsed time of the dosimeter in seconds to tag particle arrivals.
        >Default `'3'`.
    * numpy : bool, optional
        >If `True`, returns numpy array of dosimeter data. If `False`, returns `pandas` DataFrame of dosimeter data. Default `False`.

    ### Returns
    * dosi : float array-like
        >Dataframe (if not `numpy`) or numpy array (if `numpy`) of dosimeter data.

    ### Examples
    Read in data from particle precipitation event on January 3rd, 2022 from 12:30 to 13:00
    ```python
        from cupid import dosi
        from cupid import backend
        dosidata = dosi.data(trange=['2022-01-03/12:30','2022-01-03/13:00'])
    ```
    Plot the countrates in dosimeter A and dosimeter B during this event
    ```python
        import matplotlib.pyplot as plt
        plt.plot(dosidata['time_utc'],dosidata['a_rate'],color=backend.red)
        plt.plot(dosidata['time_utc'],dosidata['b_rate'],color=backend.blue)
        plt.legend(['A','B'])
    ```
    This is great for making custom plots, but if you want to plot quickly and easily it may be better to use `cupid.dosi.plot`.

    """
    if filename is None: #If filename is not specified
        raise NameError("TFTP Download not implemented in current release. Please specify filename argument.")
    else:
        dosi = be.read_dsfs(filename)
        if ((level == '1')|(level==1)):
            dosi = be.makeL1(dosi)
            dosi = pd.DataFrame(dosi,columns=be.dsfs_hdr_l1)
        if ((level=='2')|(level==2)):
            dosi = be.makeL1(dosi)
            dosi = be.makeL2(dosi,lognumbers)
            dosi = pd.DataFrame(dosi,columns=be.dsfs_hdr_l2)
        if ((level=='3')|(level==3)):
            dosi = be.makeL1(dosi)
            dosi = be.makeL2(dosi,lognumbers)
            dosi = be.makeL3(dosi,lognumbers)
            dosi = pd.DataFrame(dosi,columns=be.dsfs_hdr_l3)
        if numpy:
            return dosi.to_numpy()
        else:
            return dosi

def plot(trange=['2021-01-01/00:00','2021-01-02/00:00'], filename=None, lognumbers=[], level='3', dosi = None, countrate=True, linscale=True, title = None, cutfirst=False
        ):
    """
    Plot dosimeter data for given time range, file, or existing DataFrame.

    ### Parameters
    * trange : string array-like, optional
        >Time range of dosimeter data to download from the TFTP server. Format 'YYYY-MM-DD/HH:MM' in UTC.
        Default `['2021-01-01/00:00','2021-01-02/00:00']`.
    * filename : str, optional
        >Name of DSFS logfile to read. Only specify if you have a local CuPID binary file you want to read.
        Overrides `trange` if specified. Default `None`.
    * lognumbers : int, array-like, optional
        >Lognumber(s) of DSFS logfiles being read. Only specify if you have a local CuPID binary file you want to read and sync to UTC time.
        Default `[]`.
    * level : str, optional
        >Data processing level of dosimeter data to download. Only specify if data is to be downloaded. Options:
        >
        >     '1' : Level 1 data (time in onboard payload time)
        >
        >     '2': Level 2 data (time in UTC)
        >
        >     '3': Level 3 data (time in UTC, rates calculated)
        >
        >If time sync fails for manually processed file when level 2 specified, returned data uses the mission elapsed time of the dosimeter in seconds to tag photon arrivals.
        >Default `'3'`.
    * dosi : DataFrame, optional
        >DataFrame of dosimeter counts as read with `cupid.dosi.data()`. Can be supplied instead of logfile or time range. Default `None`.
    * linscale : bool, optional
        >If `True`, uses linear scale on y axes. If `False`, uses log scale on y axes. Default `True`.
    * title : str, optional
        >If specified, adds title to plot of counts or countrates. Default `None`.
    * cutfirst : bool, optional
        >If `True`, cuts the first ten counts or countrates. This is recommended when plotting data from when the dosimeter first turns on. Default `False`.

    ### Returns
    * dosi : float array-like
        >Dataframe of dosimeter data.

    ### Examples
    Plot the countrates in dosimeter A and dosimeter B during particle precipitation event on January 3rd, 2022 from 12:30 to 13:00
    ```python
        from cupid import dosi
        dosidata = dosi.plot(trange=['2022-01-03/12:30','2022-01-03/13:00'])
    ```
    If we have a binary logfile we want to look at, we can specify the path to the logfile.
    ```python
        dosidata = dosi.plot(filename='dsfs-26')
    ```
    """
    if (dosi is None):
        dosi = data(trange=trange, filename=filename, lognumbers=lognumbers, level=level)
    if cutfirst:
        if ((level=='1')|(level==1)|(level=='2')|(level==2)):
            dosi = dosi[2:]
        if ((level=='3')|(level==3)):
            dosi = dosi[20:]
    if ((level=='3')|(level==3)):
        t = dosi['time_utc']
        label = 'Time (UTC)'
        plt.plot(t,dosi['rate_a'],color=be.red)
        plt.plot(t,dosi['rate_b'],color=be.black)
        plt.xlabel(label)
        plt.ylabel('Countrate (counts/s)')
        plt.legend(['A','B'])
        if not linscale:
            plt.yscale('log')
        if title is None:
            plt.title('CuPID Dosimeter Countrate '+trange[0]+' to '+trange[1])
        else:
            plt.title(title)
        plt.show()
    elif ((level=='1')|(level==1)|(level=='2')|(level==2)):
        if ((level == '1')|(level==1)):
            t = dosi['time']
            label = 'Dosimeter Mission Elapsed Time'
        if ((level=='2')|(level==2)):
            t = dosi['time_utc']
            label = 'Time (UTC)'
        t_exp = np.zeros(len(t)*10)
        for i in range(len(t_exp)):
            t_exp[i] = t[i//10]+i%10
        a_low_lin = dosi[['dosa_low[0]','dosa_low[1]','dosa_low[2]','dosa_low[3]','dosa_low[4]','dosa_low[5]',
                          'dosa_low[6]','dosa_low[7]','dosa_low[8]','dosa_low[9]']].values.ravel()
        b_low_lin = dosi[['dosb_low[0]','dosb_low[1]','dosb_low[2]','dosb_low[3]','dosb_low[4]','dosb_low[5]',
                          'dosb_low[6]','dosb_low[7]','dosb_low[8]','dosb_low[9]']].values.ravel()
        a_med = dosi['dosa_med']
        b_med = dosi['dosb_med']
        a_counts = np.zeros(len(a_low_lin))
        b_counts = np.zeros(len(b_low_lin))
        for i in range(len(a_counts)):
            a_counts[i] = a_low_lin[i]+a_med[i//10]
            b_counts[i] = b_low_lin[i]+b_med[i//10]
        plt.plot(t_exp,a_counts,color=backend.red)
        plt.plot(t_exp,b_counts,color=backend.black)
        plt.xlabel(label)
        plt.ylabel('Counts')
        plt.legend(['A','B'])
        if not linscale:
            plt.yscale('log')
        if title is None:
            plt.title('CuPID Dosimeter Counts '+trange[0]+' to '+trange[1])
        else:
            plt.title(title)
        plt.show()
    return dosi