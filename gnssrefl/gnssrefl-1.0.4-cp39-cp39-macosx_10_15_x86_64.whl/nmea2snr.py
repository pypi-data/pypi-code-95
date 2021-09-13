from progress.bar import Bar

def read_NMEA(fname):
    """
    read NMEA data    
    Makan Karegar, Uni Bonn    
    Dec, 2019
    """
    
    f=open(fname, 'rb')
    lines = f.read().splitlines()
    f.close()

    t = []; prn = []; az = []; elv = []; snr = []
    for i, line in enumerate(lines):
    
        if b"GPGGA" in line: #read GPGGA sentence: Global Positioning System Fix Data 
            hr = int(line.decode("utf-8").split(",")[1][0:2])
            mn = int(line.decode("utf-8").split(",")[1][2:4])
            sc = float(line.decode("utf-8").split(",")[1][4:8])
            t_sec = hr*3600 + mn*60 + sc
            if (i > 100 and t_sec == 0):                   #set t to 86400 for the midnight data
                t_sec = 86400

        elif b"GPGSV" in line:                             #read GPGSV sentence: GPS Satellites in view in this cycle   
        
            sent = line.decode("utf-8").split(",")         #GPGSV sentence 
            ttl_ms = int(sent[1])                          #Total number of messages in the GPGSV sentence 
            ms = int(sent[2])                              #Message number 
        
            if (len(sent) == 20):                          #Case 1: 4 sat in view in this sentence 
                cnt = 0
                for j in range(0,4):
                    prn.append(sent[4+cnt])                #field 4,8,12,16 :  SV PRN number
                    elv.append(sent[5+cnt])                #field 5,9,13,17 :  Elevation in degrees, 90 maximum
                    az.append(sent[6+cnt])                 #field 6,10,14,18:  Azimuth in degrees
                    snr.append(sent[7+cnt].split("*")[0])  #field 7,11,15,19:  SNR, 00-99 dB (null when not tracking)
                    if ms <= ttl_ms:
                        t.append(t_sec)
                    
                    cnt = cnt + 4
#            ###    
            elif (len(sent) == 16):                       #Case 2: 3 sat in view in this sentence    
                cnt = 0
                for j in range(0,3):
                    prn.append(sent[4+cnt])               
                    elv.append(sent[5+cnt])             
                    az.append(sent[6+cnt])                
                    snr.append(sent[7+cnt].split("*")[0]) 
                    if ms <= ttl_ms:
                        t.append(t_sec)
                
                    cnt = cnt + 4
#            ###    
            elif (len(sent) == 12):                       #Case 3: 2 sat in view in this sentence    
                cnt = 0
                for j in range(0,2):
                    prn.append(sent[4+cnt])              
                    elv.append(sent[5+cnt])                
                    az.append(sent[6+cnt])                 
                    snr.append(sent[7+cnt].split("*")[0]) 
                    if ms <= ttl_ms:
                        t.append(t_sec)
                
                    cnt = cnt + 4
#            ###                   
            elif (len(sent) == 8):                        #Case 4: 1 sat in view in this sentence    
                cnt = 0
                for j in range(0,1):
                    prn.append(sent[4+cnt])               
                    elv.append(sent[5+cnt])                
                    az.append(sent[6+cnt])                
                    snr.append(sent[7].split("*")[0])  
                    if ms <= ttl_ms:
                        t.append(t_sec)
                
                    cnt = cnt + 4
#            ###    
            ttl_ms = 0
            ms = 0
    ijk = (elv > 0)
    delv = delv[ijk]
    print(len(elv), len(delv))
    return t, prn, az, elv, snr
    

def nmea_snr(fname,oname):
    """
    inputs are input and output file names
    """
#read one day data
    t, prn, az, elv, snr =  read_NMEA(fname)
    okok = 1
    # using format without extra columns
    f = open(oname, 'w+')
    #print(int(prn[i]), float(t[i]) )
    with Bar('Processing NMEA', max=len(t),fill='@',suffix='%(percent)d%%') as bar:
        for i in range(len(t)):
            try:
                f.write("%2g %10.4f %12.4f %9g %7s %7s %7.2f   0.00 \n" % (int(prn[i]), float(elv[i]), float(az[i]), float(t[i]),'0.00', '0.00', float(snr[i]) ))
                #bar.next()
            except:
                print( prn[i],t[i],snr[i],elv[i],az[i] )
                okok = okok + 1

    f.close()
    print(okok, 'records')
   
