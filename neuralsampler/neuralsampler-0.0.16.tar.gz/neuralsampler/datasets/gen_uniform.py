# generate the uniform distribution for the initial distributions
import os

import numpy as np
from neuralsampler.physys.dw import Doublewell
from neuralsampler.physys.gaussian import Gaussian
from neuralsampler.physys.mb import MuellerPotential
from sysflow.utils.common_utils.file_utils import dump, make_dir
from sysflow.utils.common_utils.plt_utils import *
import gdown 
MODEL = {"mb": MuellerPotential, "dw": Doublewell, "gaussian": Gaussian}




def generate_init(args, gen=False):
    # choice: gaussian, dw, mb

    #region unpack the params
    model = args.model
    dim = args.dim
    #endregion
    if gen: 
        # the threshold for generating the trajectories
        gen_thres_eng = args.gen_thres_eng

        N_dataset = int(5e7)
        N_dataset_select = int(1e7)

        if model == "mb":
            # case 1
            # this data is for the plotting;;
            x = np.random.uniform(low=-2, high=1, size=(N_dataset, 1))
            y = np.random.uniform(low=-0.5, high=2.5, size=(N_dataset, 1))

            x_init = np.concatenate([x, y], axis=1)

            # case 2
            x = np.random.uniform(low=-6, high=5, size=(N_dataset, 1))
            y = np.random.uniform(low=-4.5, high=6.5, size=(N_dataset, 1))

            # these `1` are related to the dimensions
            x = np.concatenate([x, y], axis=1)

        else:
            x = np.random.uniform(low=-5, high=5, size=(N_dataset, dim))

        md = MODEL[model](dim=dim)

        if model == "mb":
            # case I
            # after the reject sampling
            x_resam_init = x_init[md.energy(x) < 1]

            # case II
            # after the reject sampling
            x_resam = x[md.energy(x) < gen_thres_eng]

        assert len(x_resam) > N_dataset_select

        # use another files with another functional
        # visualize the samples
        # plt.scatter(x_resam[:1000, 0], x_resam[:1000, 1])
        # plt.show()

        # select 20 % of them
        my_dict = {"x": x_resam[:N_dataset_select]}

        # create a folder and dump the data
        make_dir("./dataset")
        make_dir("./dataset/init")
        fname = "{}_d{}.pkl".format(model, dim)
        dump(my_dict, os.path.join("./dataset/init", fname))

        if model == "mb":
            my_dict = {"x": x_resam_init[:N_dataset_select]}

            fname = "{}_d{}_plot.pkl".format(model, dim)
            dump(my_dict, os.path.join("./dataset/init", fname))
        else:
            # duplicate
            my_dict = {"x": x_resam[:N_dataset_select]}

            fname = "{}_d{}_plot.pkl".format(model, dim)
            dump(my_dict, os.path.join("./dataset/init", fname))


    else: 
        # TO BE filled in
        URL = {
            'mb': 
            {
                2: ['1MCrVSUTFsHag3kxB50kLJHp1lUn89THj', '1LuZI7Zd6HwP_bxZ-bj2bV2xNiuguQIjL', '1qDrihMonvG6Iy9aAC6tMjAsp1akPzE03']
            }, 
            'dw': {
                2: ''
            }
        }

        dim = 2 
        
        if isinstance(URL[model][dim], str): 
            url = 'https://drive.google.com/uc?id={}'.format(URL[model][dim])
            # create a folder and dump the data
            make_dir("./dataset")
            make_dir("./dataset/init")
            fname = "{}_d{}.pkl".format(model, dim)
            fname = os.path.join("./dataset/init", fname)
            gdown.download(url, fname, quiet=False)
        elif isinstance(URL[model][dim], list):
            assert (len(URL[model][dim]) == 3)
            for ur, subfix in zip(URL[model][dim], ['', '_2', '_3']):  
                url = 'https://drive.google.com/uc?id={}'.format(ur)
                # create a folder and dump the data
                make_dir("./dataset")
                make_dir("./dataset/init")
                fname = "{}_d{}{}.pkl".format(model, dim, subfix)
                fname = os.path.join("./dataset/init", fname)
                gdown.download(url, fname, quiet=False)



        # URL = {
        #     'mb': 
        #     {
        #         2: '1ZAGuUDK1uIbKXWi2N81MRJzs2YMZnRkL'
        #     }, 
        #     'dw': {
        #         2: ''
        #     }
        # }

        # url = 'https://drive.google.com/uc?id={}'.format(URL[model][dim])
        # fname = "{}_d{}_plot.pkl".format(model, dim)
        # fname = os.path.join("./dataset/init", fname)
        # gdown.download(url, fname, quiet=False)