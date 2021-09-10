#!/usr/bin/python3
'''
  !---------------------------------------------------------------------------! 
  ! Interface_DeePMDkit: Interface between DeePMD-kit and MLatom              ! 
  ! Implementations by: Fuchun Ge                                             ! 
  !---------------------------------------------------------------------------! 
'''
import numpy as np
import os, sys, subprocess, time, shutil, re, math, random, json
import stopper
from args_class import ArgsBase
from args_class import AttributeDict

filedir = os.path.dirname(__file__)

class Args(ArgsBase):
    def __init__(self):
        super().__init__()
        self.add_default_dict_args([
            'learningCurve'
            ],
            bool
        )
        self.add_default_dict_args([
            'xyzfile', 'yfile', 'ygradxyzfile','itrainin','itestin','isubtrainin','ivalidatein','mlmodelin'
            ],
            ""
        )        
        self.add_dict_args({
            'mlmodeltype': 'DeepPot-SE',
            'mlmodelout': "graph.pb",
            'sampling': "random",
            'yestfile': "enest.dat",
            'ygradxyzestfile': "gradest.dat",
            'lcNtrains': [],
            'natom': 0,
            'atype': []
        })
        self.parse_input_content([
            'deepmd.earlystopping.threshold=0.0001',
            'deepmd.earlystopping.patience=60',
            'deepmd.earlystopping.enable=0',
            'deepmd.input=%s/template.json'%filedir
            ])
    def parse(self, argsraw):
        self.parse_input_content(argsraw)
        self.argProcess()

    def argProcess(self):

        with open(self.xyzfile,'r') as f:
            self.natom = int(f.readline())
            exec('f.readline()')
            self.atype = [f.readline().split()[0] for i in range(self.natom)]
        if not self.mlmodelin:
            self.mlmodelin = self.mlmodelout
        
        if self.learningcurve:
            self.lcNtrains = [int(i) for i in str(self.lcNtrains).split(',')]
            if self.deepmd.batch_sizes:
                self.deepmd.batch_sizes = [int(i) for i in self.lcNtrains.split(',')]
                self.deepmd.batch_size = self.deepmd.batch_sizes[self.lcNtrains.index(self.ntrain)]

        with open(self.deepmd.input, 'r') as f:
            DeePMDCls.deepmdarg= AttributeDict.dict_to_attributedict(json.load(f))
        DeePMDCls.deepmdarg.merge_dict(DeePMDCls.deepmdarg,self.deepmd.data)
        if self.mlmodeltype.lower() in ['dpmd']:
            DeePMDCls.deepmdarg.data['model']['descriptor']['type'] = 'loc_frame'

        DeePMDCls.deepmdarg.data['training']['set_prefix']='set'
        DeePMDCls.deepmdarg.data['training']['systems']=['./']
        DeePMDCls.deepmdarg.data["model"]["type_map"] = sorted(set(self.atype), key=lambda x: self.atype.index(x))
        if 'decay_rate' in DeePMDCls.deepmdarg.data['learning_rate'].keys(): 
            DeePMDCls.deepmdarg.data['learning_rate']['stop_lr']=DeePMDCls.deepmdarg.data['learning_rate']['start_lr']*DeePMDCls.deepmdarg.data['learning_rate']['decay_rate']**(DeePMDCls.deepmdarg.data['training']['stop_batch']//DeePMDCls.deepmdarg.data['learning_rate']['decay_steps'])
        if DeePMDCls.deepmdarg.data['model']['descriptor']['type'] != 'loc_frame':
            DeePMDCls.deepmdarg.data['model']['descriptor']['sel'] = [self.natom+1]*len(DeePMDCls.deepmdarg.data["model"]["type_map"])
        else:
            DeePMDCls.deepmdarg.data['model']['descriptor']['sel_a'] = [self.natom+1]*len(DeePMDCls.deepmdarg.data["model"]["type_map"])
            DeePMDCls.deepmdarg.data['model']['descriptor']['sel_r'] = [self.natom+1]*len(DeePMDCls.deepmdarg.data["model"]["type_map"])
            try:
                del DeePMDCls.deepmdarg.data['model']['descriptor']['sel'] 
            except: pass

        if not self.ygradxyzfile:
            DeePMDCls.deepmdarg.data['loss']['limit_pref_f']=0
            DeePMDCls.deepmdarg.data['loss']['start_pref_f']=0
        if not self.yfile:
            DeePMDCls.deepmdarg.data['loss']['limit_pref_e']=0
            DeePMDCls.deepmdarg.data['loss']['start_pref_e']=0



class DeePMDCls(object):
    deepmdarg=AttributeDict()
    @classmethod
    def load(cls):
        loaded=False
        if not loaded:
            try:
                DeePMDdir = os.environ['DeePMDkit']
            except:
                print('please set $DeePMDkit')
            DeePMDbin = DeePMDdir+'/dp'
            
            globals()['DeePMDdir'] = DeePMDdir
            globals()['DeePMDbin'] = DeePMDbin

            loaded=True
    def __init__(self, argsDeePMD = sys.argv[1:]):
        print(' ___________________________________________________________\n\n%s' % __doc__)

    @classmethod
    def createMLmodel(cls, argsDeePMD, subdatasets):
        cls.load()
        args=Args()
        args.parse(argsDeePMD)
        # data conversion
        print('\n Converting data...\n\n')
        prefix = ''
        if args.learningcurve: prefix = '../'
        cls.convertdata('coord', 'subtrain', prefix+'xyz.dat_subtrain',args)
        cls.convertdata('coord', 'validate', prefix+'xyz.dat_validate',args)
        if args.yfile:
            cls.convertdata('en', 'subtrain', prefix+'y.dat_subtrain',args)
            cls.convertdata('en', 'validate', prefix+'y.dat_validate',args)
        if args.ygradxyzfile:
            cls.convertdata('force', 'subtrain', prefix+'grad.dat_subtrain',args)
            cls.convertdata('force', 'validate', prefix+'grad.dat_validate',args)
        # write dp input json
        with open("deepmdargs.json","w") as f:
            json.dump(iterdict(AttributeDict.normal_dict(cls.deepmdarg)), f, indent=4)
        
        if os.path.exists(cls.deepmdarg.data['training']['disp_file']):
            os.system('rm '+ cls.deepmdarg.data['training']['disp_file']+' '+args.mlmodelout)
        
        # run dp train
        FNULL = open(os.devnull, 'w')
        starttime = time.time()
        print('\n\n> %s train deepmdargs.json' % DeePMDbin)
        sys.stdout.flush()

        proc = subprocess.Popen([DeePMDbin,"train","deepmdargs.json"], stdout=subprocess.PIPE ,stderr=FNULL)
        for line in iter(proc.stdout.readline, b''):
            print(line.decode('ascii').replace('\n',''))
            if args.deepmd.earlystopping.enable:
                try:
                    lastline=subprocess.check_output(['tail', '-1', cls.deepmdarg.data['training']['disp_file']],stderr=FNULL).split()
                    loss = float(lastline[1])
                    nbatch = int(lastline[0])
                    sys.stdout.flush()
                    if earlyStop(nbatch, loss, patience = args.deepmd.earlystopping.earpatience, threshold=args.deepmd.earlystopping.threshold):
                        print('met early-stopping conditions')
                        proc.terminate()
                except:
                        pass
            sys.stdout.flush()
        proc.stdout.close()

        print('\n ___________________________________________________________\n\n Learning curve:\n')
        sys.stdout.flush()
        os.system('cat '+cls.deepmdarg.data['training']['disp_file'])
        sys.stdout.flush()
        # save MLmodel
        print('\n\n> %s freeze -o %s' % (DeePMDbin, args.mlmodelout))
        sys.stdout.flush()
        subprocess.call([DeePMDbin,"freeze","-o",args.mlmodelout],stdout=FNULL,stderr=FNULL)
        if os.path.exists(args.mlmodelout):
            print('model saved in %s' % args.mlmodelout)
        FNULL.close()

        endtime = time.time()
        wallclock = endtime - starttime
        return wallclock

    @classmethod
    def useMLmodel(cls, argsDeePMD, subdatasets):
        cls.load()
        args=Args()
        args.parse(argsDeePMD)
        cls.convertdata('coord', 'test', args.xyzfile, args)
        
        starttime = time.time()

        FNULL = open(os.devnull, 'w')
        subprocess.call([DeePMDdir+"/python", filedir+"/DP_inference.py", 'testset/coord.npy', args.mlmodelin,  args.yestfile, args.ygradxyzestfile],stdout=FNULL , stderr=FNULL)
        FNULL.close()
        
        # if os.path.exists(args.yestfile) and os.path.exists(args.ygradxyzestfile):
        #     print('estimated values saved in '+args.yestfile+' and '+args.ygradxyzestfile)

        endtime = time.time()
        wallclock = endtime - starttime
        return wallclock
        
    @classmethod
    def convertdata(cls, datatype, dataset, filein, args):
        
        if dataset=='subtrain':
            outdir = 'set.000'
        elif dataset=='validate':
            outdir = 'set.001'
        elif dataset=='test':
            outdir = 'testset'
        
        if not os.path.isdir(outdir):
            os.system('mkdir '+outdir)

        # convert to coord.npy box.npy type.raw
        if datatype=='coord':
            dic = {cls.deepmdarg.data["model"]["type_map"][i]:i for i in range(len(cls.deepmdarg.data["model"]["type_map"]))}
            index = [dic[i] for i in args.atype]
            with open('type.raw','w') as ff:
                for i in index:
                    ff.writelines("%d " % i)

            with open(filein,'r') as fi:
                data = np.array([])
                for i, line in enumerate(fi):
                    if i%(args.natom+2) > 1:  
                        data = np.append(data,np.array(line.split()[-3:]).astype('float'))
                data = data.reshape(-1,3*args.natom)

            with open(outdir+'/coord.npy','wb') as fo:
                np.save(fo, data)

            with open(outdir+'/box.npy','wb') as fo:
                np.save(fo, np.repeat(np.diag(64 * np.ones(3)).reshape([1, -1]),len(data), axis=0))

        # convert to force.npy
        elif datatype=='force':
            with open(filein,'r') as fi:
                data = np.array([])
                for i, line in enumerate(fi):
                    if i%(args.natom+2) > 1:  
                        data = np.append(data,-1*np.array(line.split()[-3:]).astype('float'))
                data = data.reshape(-1,3*args.natom)

            with open(outdir+'/force.npy','wb') as fo:
                np.save(fo, data)

        # conver to energy.npy
        elif datatype=='en':
            with open(filein,'r') as fi:
                data = np.array([])
                for line in fi: 
                    data = np.append(data,np.array(line).astype('float'))

            with open(outdir+'/energy.npy','wb') as fo:
                np.save(fo, data)    
# home-made early stopping for dp
def earlyStop(nbatch, loss, bestloss=[1000], bestbatch=[0], patience = 2, threshold = 1.0001):
    stop = False
    if loss < (1 - threshold)*bestloss[0]:
        bestloss[0] = loss
        bestbatch[0]=nbatch
    if (nbatch - bestbatch[0])/DeePMDCls.deepmdarg.data['training']['disp_freq'] > patience:
        stop = True
    return stop

# function for modifying args in dp input json
def mapdict(dic,arg):
    try:
        key,value=arg.split('.',1)[1].split("=")
        subdic=dic
        for i in key.split(".")[:-1]:
            subdic = subdic[i.lower()]
        #exec 'subdic[key.split(".")[-1].lower()]'
        subdic[key.split(".")[-1].lower()]=json.loads(value)
    except:
        pass

def iterdict(d):
    for k, v in d.items():
        if isinstance(v, dict):
            iterdict(v)
        else:
            if type(v) == str:
                if v[0]=='[' and v[-1]==']':
                    v=json.loads(v)
            d.update({k: v})
    return d

def printHelp():
    helpText = __doc__ + '''
  To use Interface_DeePMDkit, please define environmental variable $DeePMDkit
  to where dp binary is located (e.g "/home/xxx/deepmd-kit-1.2/bin").

  Arguments with their default values:
    MLprog=DeePMD-kit          enables this interface
    MLmodelType=S              requests model S
      DeepPot-SE               [defaut]
      DPMD
      
    deepmd.xxx.xxx=X           specify arguments for DeePMD,
                               follows DeePMD-kit's json input file structure
      deepmd.training.stop_batch=4000000        
                               number of batches to be trained before stopping       
      deepmd.training.batch_size=32 
                               size of each batch
      deepmd.learning_rate.start_lr=0.001
                               initial learning rate
      deepmd.learning_rate.decay_steps=4000
                               number of batches for one decay
      deepmd.learning_rate.decay_rate=0.95
                               decay rate of each decay 
      deepmd.model.descriptor.rcut=6.0        
                               cutoff radius for local environment
      deepmd.model.fitting_net.neuron=80,80,80
                               NN structure of fitting network
        
    deepmd.input=S             file S with DeePMD input parameters
                               in json format (as a template)

  Cite DeePMD-kit:
    H. Wang, L. Zhang, J. Han, W. E, Comput. Phys. Commun. 2018, 228, 178
    
  Cite DeepPot-SE method, if you use it:
    L.F. Zhang, J.Q. Han, H. Wang, W.A. Saidi, R. Car, W.N. E,
    Adv. Neural. Inf. Process. Syst. 2018, 31, 4436
    
  Cite DPMD method, if you use it:
    L. Hang, J. Han, H. Wang, R. Car, W. E, Phys. Rev. Lett. 2018, 120, 143001
'''
    print(helpText)

if __name__ == '__main__':
    DeePMDCls()
