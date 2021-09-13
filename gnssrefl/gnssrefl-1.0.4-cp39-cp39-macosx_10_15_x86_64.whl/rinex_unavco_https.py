def rinex_unavco_https(station, year, month, day):
    """
    author: kristine larson
    picks up a RINEX file from default unavco area, i.e. not highrate.  
    it tries to pick up an o file,
    but if it does not work, it tries the "d" version, which must be
    decompressed.  the location of this executable is defined in the crnxpath
    variable. 
    year, month, and day are INTEGERS

    WARNING: only rinex version 2 in this world

    21sep01  changed from ftp to https
    """
    exedir = os.environ['EXE']
    crnxpath = hatanaka_version()  # where hatanaka will be
    if day == 0:
        doy = month
        cyyyy = str(year)
        cdoy = '{:03d}'.format(doy)
        cyy = '{:02d}'.format(year-2020)
    else:
        doy,cdoy,cyyyy,cyy = ymd2doy(year,month,day)
    rinexfile,rinexfiled = rinex_name(station, year, month, day)
    unavco= 'https://data.unavco.org/archive/gnss/rinex.obs/'
    filename1 = rinexfile + '.Z'
    filename2 = rinexfiled + '.Z'
    # URL path for the o file and the d file
    url1 = unavco+ cyyyy + '/' + cdoy + '/' + filename1
    url2 = unavco+ cyyyy + '/' + cdoy + '/' + filename2
    print(url1)
    print(url2)

    #print('try regular RINEX at unavco')
    try:
        wget.download(url1,filename1)
        status = subprocess.call(['uncompress', filename1])
    # removed to keep jupyter notebooks clean. 
    #except Exception as err:
    #    print(err)
    except:
        okokok =1

    #print('try hatanaka RINEX at unavco')
    if not os.path.exists(rinexfile):
        # look for hatanaka version
        if os.path.exists(crnxpath):
            try:
                wget.download(url2,filename2)
                status = subprocess.call(['uncompress', filename2])
                status = subprocess.call([crnxpath, rinexfiled])
                status = subprocess.call(['rm', '-f', rinexfiled])
            except:
                okokok =1
            #except Exception as err:
            #    print(err)
        else:
            hatanaka_warning()

