import numpy as np


class Sweep:
    """ 
    Returns t and E for a sweep potential waveform.
    All the parameters are given a default value.
    """

    def __init__(self, params):
        self.Eini = params[0]
        self.Efin = params[1]
        self.sr = params[2]
        self.dE = params[3]
        self.ns = params[4]

        Ewin = abs(self.Efin-self.Eini)
        tsw = Ewin/self.sr # total time for one sweep
        nt = int(Ewin/self.dE)

        self.E = np.array([])
        self.t = np.linspace(0, tsw*self.ns, nt*self.ns)

        for n in range(1, self.ns+1):
            if (n%2 == 1):
                self.E = np.append(self.E, np.linspace(self.Eini, self.Efin, nt))
            else:
                self.E = np.append(self.E, np.linspace(self.Efin, self.Eini, nt))



class Step:
    """ 
    Returns t and E for a step potential waveform.
    All the parameters are given a default value.
    """

    def __init__(self, params):
        
        self.Es = params[0]
        self.ttot = params[1]
        self.dt = params[2]
        self.nt = int(self.ttot/self.dt)

        self.E = np.ones([self.nt])*self.Es
        self.t = np.linspace(0, self.ttot, self.nt)



class Construct_wf:
    """ 
    
    Returns t and E for a customised potential waveform.
    
    Parameters
    ----------
    wf:     list containing the waveform object
    
    Returns
    -------
    t:      s, time array
    E:      V, potential array
    
    Examples
    --------
    >>> import softpotato as sp
    >>> wf1 = sp.step(Estep, tini, ttot, dt)
    >>> wf2 = sp.sweep(Eini, Efin, sr, dE, ns)
    >>> wf = sp.Construct_wf([wf1, wf2])
    
    Returns t and E calculated with the parameters given
    """

    def __init__(self, wf):
        n = len(wf)
        t = np.array([0])
        E = np.array([0])

        for i in range(n):
            t = np.concatenate([t,wf[i].t+t[-1]])
            E = np.concatenate([E,wf[i].E])

        # Remove first data point to prevent repeating time
        self.t = t[1:]
        self.E = E[1:]
        
