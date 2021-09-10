#!/usr/bin/env python3
'''
  !---------------------------------------------------------------------------! 
  ! NX_MLatom_interface: Interface between NEWTON-X and MLatom                ! 
  ! Implementations by: Pavlo O. Dral and Fuchun Ge                           ! 
  !---------------------------------------------------------------------------! 
'''

import sys, os, subprocess, re
import stopper
mlatomdir=os.path.dirname(__file__)
mlatomfbin="%s/MLatomF" % mlatomdir

class ifMLatomCls(object):           
    @classmethod
    def run(cls, argsMLatomF, shutup=False, cwdpath='.'):
        t_train=0
        t_descr=0
        t_hyperopt=0
        t_finaltrain=0
        t_pred=0
        t_wc=0
        Ntrain=None
        Ntest=None
        rmsedict={}
        yflag=0
        gflag=0
        deadlist=[]
        for arg in argsMLatomF:
            flagmatch = re.search('(^nthreads)|(^hyperopt)|(^setname=)|(^learningcurve$)|(^lcntrains)|(^lcnrepeats)|(^mlmodeltype)|(^mlprog)|(^deltalearn)|(^yb=)|(^yt=)|(^yestt=)|(^nlayers=)|(^selfcorrect)|(^$)', arg.lower(), flags=re.UNICODE | re.MULTILINE | re.DOTALL | re.IGNORECASE)
            if flagmatch:
                deadlist.append(arg)
        for i in deadlist: argsMLatomF.remove(i)
        proc = subprocess.Popen([mlatomfbin] + argsMLatomF, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwdpath)
        for line in iter(proc.stdout.readline, b''):
            readable = line.decode('ascii')
            if 'Descriptor generation time' in readable:
                t_descr = float(readable.split()[-2])
            if 'Hyperparameter optimization time:' in readable:
                t_hyperopt = float(readable.split()[-2])
            if 'Training time' in readable:
                t_finaltrain = float(readable.split()[-2])
            elif 'Training time' in readable:
                t_train += float(readable.split()[2])
            elif 'Validating time' in readable:
                t_train += float(readable.split()[2])
            elif 'Test time' in readable:
                t_pred = float(readable.split()[-2])
            if 'Wall-clock time:' in readable and not 'min' in readable:
                t_wc = float(readable.split()[-2])  
            if 'Statistical analysis for' in readable and 'entries in the training set' in readable and Ntrain == None:
                Ntrain = float(readable.split()[3])  
            if 'Statistical analysis for' in readable and 'entries in the test set' in readable and Ntest == None:
                Ntest = float(readable.split()[3])  
            elif 'Prediction time' in readable:
                t_pred += float(readable.split()[2])
            elif 'Analysis for values' in readable: yflag=1
            elif 'Analysis for gradients in XYZ coordinates' in readable: gflag=1
            elif 'RMSE ='in readable:
                if yflag:
                    rmsedict['eRMSE'] = float(readable.split()[2])
                    yflag = 0
                if gflag:
                    rmsedict['fRMSE'] = float(readable.split()[2])
                    gflag = 0
            # if not shutup or '<!>' in readable: print(readable.replace('\n',''))
            print(readable.replace('\n',''))
        proc.stdout.close()
        if Ntrain != None:
            t_train = t_hyperopt + t_finaltrain + t_descr
        if Ntrain == None and Ntest == None:
            t_pred = t_wc
        if Ntrain != None and Ntest != None:
            t_train -= t_descr / (Ntrain + Ntest) * Ntest
            t_pred  += t_descr / (Ntrain + Ntest) * Ntest
            
        return [t_train, t_pred, rmsedict]

def printHelp():
    proc = subprocess.Popen([mlatomfbin] + ['help'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for line in iter(proc.stdout.readline, b''):
        readable = line.decode('ascii')
        print(readable.rstrip())

if __name__ == '__main__':
    print(__doc__)
    ifMLatomCls.run(sys.argv[1:])
