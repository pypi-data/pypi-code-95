def splinef(th,h):
    """
    inputs for now are time (days) and RH (h)
    """

    fillgap = 1/24 # one hour fake values
    gap = 4/24 # up to four hour gap allowed

    tnew =[] ; ynew =[]; 
    # fill in gaps using variables called tnew and ynew
    for i in range(1,len(th)):
        d= th[i]-th[i-1]
        if (d > gap):
            #print(t[i], t[i-1])
            print('found a gap in hours',d*24)
            x0 = th[i-1:i+1]
            h0 = h[i-1:i+1]
            f = scipy.interpolate.interp1d(x0,h0)
            tnew = np.arange(th[i-1]+fillgap, th[i], fillgap)
            ynew = f(tnew)
#            print('new t values', tnew)
#            print('new h values', ynew)

# append the interpolated values so the splines don't get unhappy

    if (len(tnew) > 0):
        tnew = np.append(th,tnew)
        ynew = np.append(h,ynew)
        # try sorting to see if that fixes it
        ii = np.argsort( tnew) 
        tnew = tnew[ii]
        ynew = ynew[ii]
    else:
        tnew = th
        ynew = h

    knots_per_day = 12

    Ndays = tnew.max()-tnew.min()
    numKnots = int(knots_per_day*(Ndays))
    print('First and last time values', '{0:8.3f} {1:8.3f} '.format (tnew.min(), tnew.max()) )
    print('Number of RH obs', len(h))
    print('Average obs per day', '{0:5.1f} '.format (len(h)/Ndays) )
    print('Number of knots: ', numKnots)
    print('Number of days of data: ', '{0:8.2f}'.format ( Ndays) )

    # need the first and last knot to be inside the time series
    t1 = tnew.min()+0.05
    t2 = tnew.max()-0.05
    # try this 
    # 
    knots =np.linspace(t1,t2,num=numKnots)

    t, c, k = interpolate.splrep(tnew, ynew, s=0, k=3,t=knots,task=-1)
    # user specifies how many values per day you want to send back to the user  

    # should i do extrapolate True? it is the default  - could make it periodic?
    spline = interpolate.BSpline(t, c, k, extrapolate=True)
    # equal spacing in both x and y
    # evenly spaced data - units of days
    N = int(Ndays*perday)
    xx = np.linspace(tnew.min(), tnew.max(), N)
    spl_x = xx; spl_y = spline(xx)

