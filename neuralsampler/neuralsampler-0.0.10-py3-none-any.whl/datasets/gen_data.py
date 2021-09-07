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
    model = args.model
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
        URL = {
            "mb": {2: "1Y52BXL-rbEFcjNTAHwIn7S6FNtYRyVXv",
                   3: "1-UW5nRZcMTUx8yqkvr2KYZpERiVxmz-F",
                   10: "1yvzrLXkbs_8DyTZRNnZDGcYnaSSk26FY"},
            "dw": {2: "1QGvp94Wtrg_HgwnFGnhyf1vYjB-Ctw6P",
                   3: "1-pVVd1KPUS84AvNKoQbp9Q1P3ZnmF0Yd",
                   10: "1bxrHyUHYAE4ILjWuJzbt5TGuMh3TwwMY"},
        }

        url = "https://drive.google.com/uc?id={}".format(URL[model][dim])
        make_dir("./dataset")
        make_dir("./dataset/traj")
        fname = "{}_d{}.pkl".format(model, dim)
        fname = os.path.join("./dataset/traj", fname)
        gdown.download(url, fname, quiet=False)
