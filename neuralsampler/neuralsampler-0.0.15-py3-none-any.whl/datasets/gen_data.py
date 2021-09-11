# langevin to generate the short range dynamics
import copy
import os

import gdown
import numpy as np
from sysflow.utils.common_utils.file_utils import dump, load, make_dir
from tqdm import trange
from neuralsampler.mcmc.langevin import langevin

# probably can merged into a class
def generate_traj(args, gen=False):
    # generate short trajectories

    # choice: gaussian, dw, mb

    #region unpack the params
    model = args.physys
    dim = args.dim
    gen_thres_eng = args.gen_thres_eng
    #endregion

    if gen:
        # mcmc parameters
        # TODO: make them as a new param
        delta_t = 1e-3
        t = 0.4
        N_mc = int(t / delta_t)

        fname = "{}_d{}.pkl".format(model, dim)
        fname = os.path.join("./dataset/init", fname)

        x_data = load(fname)
        x = x_data["x"]
        xx = copy.deepcopy(x)

        N_dataset = x.shape[0]

        mala = langevin(delta_t, model, N_dataset, dim)

        # change this from the mcmc 
        # initialize the model there 
        for i in trange(N_mc):
            # TODO: dim
            # because later we want to make a gaussian dummy there

            if model == "mb":
                x = mala.restrict_step( x, thres_eng=100)
            else:
                x = mala.step(x)

        my_dict = {"x": xx, "y": x}

        # create a folder and dump the data
        make_dir("./dataset")
        make_dir("./dataset/traj")
        fname = "{}_d{}.pkl".format(model, dim)
        dump(my_dict, os.path.join("./dataset/traj", fname))

    else:
        # the google drive dataset link
        URL = {
            "GL": {50: "1Kt9sdW22n_0DuC3KtmiVQueuwwRn4QAp"},
            "dw": {
                10: "1118WX5AzsD0nt_SP9jhGsA_3O1FIHVgs",
                2: "1e27kOF-9nl_5KcU7xA1xJDJYPTZC539W",
                3: "182uo1hToBsmCZdjf0RIFliNw_H_tr9nK",
            },
            "mb": {
                10: "1JfhvevSyJF4TLRtrS3DjuxLR04Nsk0vY",
                2: "1GHhO0WUmvmhUnWmQG8gj9RejOjv88YUx",
                3: "1C2JCxLBsDQ_0wQ6cGRH8_uh8vYm4Sosy",
            },
            "period": {
                10: "1lUDyaMXV_6qs6j2lds7hixvaWw1PxUQG",
                2: "1JL3iIhFQg-M1Ch8mrvgE19GvURb5vt6f",
                3: "1u0Q9opLvJek-loVWJW82Q-8aq-A4E6QS",
            },
            "period2": {
                10: "1GdtsfoW4vPlX2tghZGGVxscWUPooa70U",
                2: "1H40aWlaBwW51W7jjnxfYeL79rhjAonOm",
                3: "1Udg40RTeC-QtLRQRRpAkU9w1OpdXH1sT",
            },
        }

        url = "https://drive.google.com/uc?id={}".format(URL[model][dim])
        make_dir("./dataset")
        make_dir("./dataset/traj")
        fname = "{}_d{}.pkl".format(model, dim)
        fname = os.path.join("./dataset/traj", fname)
        gdown.download(url, fname, quiet=False)

        # here are for the auxiliary dataset in the anima
        # TODO: change for better
        AUX_URL = {
            "period2": "1nP7xDdjttgPyHZrpHj7EhXPg1DcWXZmc",
            "period": "1-YshIHr5RCSeKnn_oPq9IHqXv58dqSGa",
            "GL": "1Hy75U0Ki1VK7fmZy9tAH-s16oVIC2OYe",
        }

        AUX_FNAME = {
            'period': 'mcmc-ex1-s3909999.pkl', 
            'period2': 'mcmc-ex1-s469999.pkl', 
            'GL': 'traj-{}.pkl'.format(19999999)
        }
        
        if model in AUX_FNAME: 
            url = "https://drive.google.com/uc?id={}".format(AUX_URL[model])

            fname = AUX_FNAME[model]

            fname = os.path.join("./", fname)
            gdown.download(url, fname, quiet=False)
