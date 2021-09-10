#!/usr/bin/env python3
'''

  !---------------------------------------------------------------------------!
  !                                                                           !
  !     MLatom: a Package for Atomistic Simulations with Machine Learning     !
  !                               Version 2.0                                 !
  !                           http://mlatom.com/                              !
  !                                                                           !
  !                  Copyright (c) 2013-2021 Pavlo O. Dral                    !
  !                           http://dr-dral.com/                             !
  !                                                                           !
  ! All rights reserved. This work is licensed under the                      !
  ! Attribution-NonCommercial-NoDerivatives 4.0 International                 ! 
  ! (http://creativecommons.org/licenses/by-nc-nd/4.0/) license.              !
  ! See LICENSE.CC-BY-NC-ND-4.0.                                              !
  !                                                                           !
  ! The above copyright notice and this permission notice shall be included   !
  ! in all copies or substantial portions of the Software.                    !
  !                                                                           !
  ! The software is provided "as is", without warranty of any kind, express   !
  ! or implied, including but not limited to the warranties of                !
  ! merchantability, fitness for a particular purpose and noninfringement. In !
  ! no event shall the authors or copyright holders be liable for any claim,  !
  ! damages or other liability, whether in an action of contract, tort or     !
  ! otherwise, arising from, out of or in connection with the software or the !
  ! use or other dealings in the software.                                    !
  !                                                                           !
  !                                Cite as:                                   !
  ! Pavlo O. Dral, J. Comput. Chem. 2019, 40, 2339-2347                       !
  ! Pavlo O. Dral, Fuchun Ge, Bao-Xin Xue, Yi-Fan Hou, Max Pinheiro Jr,       !
  ! Jianxing Huang, Mario Barbatti, Top. Curr. Chem. 2021, 379, 27            !
  !                                                                           !
  ! Pavlo O. Dral, Bao-Xin Xue, Fuchun Ge, Yi-Fan Hou, Max Pinheiro Jr,       !
  ! MLatom: A Package for Atomistic Simulations with Machine Learning         !
  ! version 2.0, Xiamen University, Xiamen, China, 2013-2021                  !
  !                                                                           !  
  !---------------------------------------------------------------------------!

'''

import os, sys, subprocess, time, shutil, re, copy
import sliceData, stopper
import MLtasks, sliceData, stopper
import interface_MLatomF
import header
from args_class import ArgsBase
from doc import Doc

class MLatomMainCls(object):
    def __init__(self):
        starttime = time.time()
        
        print(__doc__)
        
        print(' %s ' % ('='*78))
        print(time.strftime(" MLatom started on %d.%m.%Y at %H:%M:%S", time.localtime()))
        print('        with the following options:')
        argsstr = '        '
        for arg in sys.argv:
            argsstr += arg + ' '
        print(argsstr.rstrip())
        if len(sys.argv[1:]) == 1:
            if os.path.exists(sys.argv[1]):
                print('\n        Input file content:')
                print(' %s ' % ('_'*78))
                with open(sys.argv[1], 'r') as finp:
                    for line in finp:
                        print(line.rstrip())
                print(' %s ' % ('_'*78))
        args = Args()
        args.parse(sys.argv[1:])
        print(' %s ' % ('='*78))
        header.printHeader(args)
        sys.stdout.flush()

        # Set the number of threads
        if args.nthreads:
            os.environ["OMP_NUM_THREADS"] = str(args.nthreads)
            os.environ["MKL_NUM_THREADS"] = str(args.nthreads)
            os.environ["OMP_PROC_BIND"]   = 'true'
        
        # Perform requested task
        if args.XYZ2X or args.sample or args.analyze:
            interface_MLatomF.ifMLatomCls.run(args.args2pass)
            pass
        elif args.slice or args.sampleFromSlices or args.mergeSlices:
            sliceData.sliceDataCls(argsSD = args.args2pass)
        elif (args.useMLmodel    or args.createMLmodel or
              args.estAccMLmodel or args.learningCurve or
              args.MLNEA):
            MLtasks.MLtasksCls(argsMLtasks = args.args2pass)
        
        endtime = time.time()
        wallclock = endtime - starttime
        print(' %s ' % ('='*78))
        print(' Wall-clock time: %.2f s (%.2f min, %.2f hours)\n' % (wallclock, wallclock / 60.0, wallclock / 3600.0))
        print(time.strftime(" MLatom terminated on %d.%m.%Y at %H:%M:%S", time.localtime()))
        print(' %s ' % ('='*78))
        sys.stdout.flush()

class Args(ArgsBase):
    def __init__(self):
        super().__init__()
        self.task_list = [
            'XYZ2X', 'analyze', 'sample', 'sampleFromSlices', 'mergeSlices','slice',
            'useMLmodel', 'createMLmodel', 'estAccMLmodel', 'learningCurve', 
            'crossSection'
        ]
        self.add_default_dict_args(self.task_list, bool)
        self.add_default_dict_args([
            'useMLmodel', 'createMLmodel', 'estAccMLmodel', 'learningCurve','deltaLearn','selfCorrect','MLmodelType'
            ],
            bool
        )
        self.add_default_dict_args([
            'MLprog'
            ],
            ''
        )
        self.add_default_dict_args([
            'Yb', 'Yt', 'YestT', 'YestFile','XYZfile', 'XfileIn', 'Yfile', 'YgradXYZfile', 'absXfileIn', 'absXYZfile', 'absYfile', 'absYgradXYZfile', 'YgradXYZestFile', 'Ntrain', 'Nsubtrain', 'Nvalidate', 'Ntest', 'iTrainIn', 'iTestIn', 'iSubtrainIn', 'iValidateIn', 'sampling', 'MLmodelIn', 'MLmodelOut',
            'molDescriptor', 'kernel'
            ],
            ''
        )
        self.add_dict_args({'MLmodelType': '', 'nthreads': None})
        self.set_keyword_alias('crossSection', ['ML-NEA', 'ML_NEA', 'crossSection', 'cross-section', 'cross_section','MLNEA'])
        self.args2pass = []

    def parse(self, argsraw):
        if len(argsraw) == 0:
            Doc.printDoc({})
            stopper.stopMLatom('At least one option should be provided')
        elif len(argsraw) == 1:
            if os.path.exists(argsraw[0]):
                self.parse_input_file(argsraw[0])
            else:
                self.parse_input_content(argsraw[0])
            self.args2pass = self.args_string_list(['', None])
        elif len(argsraw) >= 2:
            self.parse_input_content(argsraw)
            self.args2pass = self.args_string_list(['', None])
        self.checkArgs()

    def checkArgs(self):
        Ntasks = eval(' + '.join(map(lambda s: 'self.' + s, self.task_list)))
        if Ntasks == 0:
            Doc.printDoc({})
            stopper.stopMLatom('At least one task should be requested')

if __name__ == '__main__':
    MLatomMainCls()
