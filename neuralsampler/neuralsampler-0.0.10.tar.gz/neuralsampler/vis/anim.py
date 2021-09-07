# create the animation to show the learning process
import os

# plots the animation
import numpy as np
# del plt 
# del matplotlib
import matplotlib 
matplotlib.use('Agg')
from matplotlib import pyplot as plt
plt.rcParams["image.cmap"] = 'viridis'
plt.rcParams["text.usetex"] = 'False'
from celluloid import Camera
from pylab import meshgrid
from sysflow.utils.common_utils.file_utils import load, make_dir
from tqdm.contrib import tzip
from tqdm import tqdm
from scipy import stats
import seaborn as sns 
from neuralsampler.physys.dw import Doublewell
from neuralsampler.physys.gaussian import Gaussian
from neuralsampler.physys.mb import MuellerPotential
from neuralsampler.utils import naturalsize
# physical system
PHYSYS = {"mb": MuellerPotential, "dw": Doublewell, "gaussian": Gaussian}

# TODO shall we do the small function for each model here?


def generate_anim(args):
    # generate animation of the learning process
    # choice: gaussian, dw, mb

    #region unpack the params
    physys = args.physys
    dim = args.dim
    G_loss = args.G_loss
    exp_dir = args.exp_dir
    viz_freq = args.viz_freq
    niters = args.niters
    #endregion

    # process the name 
    if physys.endswith('multistep'): 
        _physys = physys.split('_')[0]
    else: 
        _physys = physys 

    # prepare the reference measure
    if physys.startswith('mb'): 
        # plot the reference
        d = 2

        md = PHYSYS[_physys](dim=d)

        xmin = -2
        xmax = 1
        ymin = -0.5
        ymax = 2.5

        dx = 0.04
        x = np.arange(xmin, xmax, dx)
        y = np.arange(ymin, ymax, dx)
        nx = x.shape[0]
        ny = y.shape[0]

        X, Y = meshgrid(x, y)  # grid of point

        X_Y_vec = np.stack([np.reshape(X, (nx * ny)), np.reshape(Y, (nx * ny))], axis=1)
        Eng_ref = np.reshape(md.energy(X_Y_vec), (ny, nx))

        X_ref = x
        Y_ref = y
        Impsamp_ref = np.exp(-Eng_ref)
    
    elif physys.startswith('GL'): 
        # loading the data

        #TODO: change these hard code parts!
        # do u want to unify this? 
        _x_new = load('/home/jimmy/Downloads/colab_paritition/traj_p00000/traj-{}.pkl'.format(19999999))
        data_gt = _x_new['y']
        react_coord_gt = np.mean(data_gt, axis=1)
    
        # this is for the init measure, delete this 
        X_init = load('/media/jimmy/TITAN1/ScratchGym/neuralsampler_all_in_one/dataset/init/{}_d{}.pkl'.format(physys, dim))
        if isinstance(X_init, dict):
            X_init = X_init['xx']

        X_init=X_init[:10000, :]
        X_marginal = X_init.mean(1)
        
    elif physys.startswith('period'):
        # load the data

        #TODO: change these hard code parts!
        if physys == 'period': 
            X_history = load('/media/jimmy/TITAN1/ScratchGym/neuralsampler_period/example1/mcmc-ex1-s3909999.pkl')
        else: 
            X_history = load('/media/jimmy/TITAN1/ScratchGym/neuralsampler_period/example2/data/mcmc-ex1-s469999.pkl')

        data_gt = np.concatenate(X_history[-10000:], 0)

        # Generate some test data
        x_ref = data_gt[:, 0]
        y_ref = data_gt[:, 1]

        Impsamp_ratio = np.vstack([x_ref, y_ref])

        # show the heatmap of the data 
        # heatmap, xedges, yedges = np.histogram2d(_x, _y, bins=100)
        # extent = [-1, 0.8, 0, 1]

        # this is for the plot, restricting the range 
        xmin = -2.0
        xmax = 2
        ymin = 0.0
        ymax = 1.0

        # this is for the interpolation 
        grid_x_2d, grid_y_2d = np.mgrid[xmin:xmax:100j, ymin:ymax:100j]
        grid_x_y_vec = np.vstack([grid_x_2d.ravel(), grid_y_2d.ravel()])
        Impsamp_ratio_ref = np.vstack([x_ref, y_ref])

        Impsamp_ratio_kernel = stats.gaussian_kde(Impsamp_ratio_ref)

        Impsamp_ratio_interpolation_ref = np.reshape(Impsamp_ratio_kernel(grid_x_y_vec).T, grid_x_2d.shape)

    elif physys.startswith('dw'):
        # this is for the double well potential 
        grid_x = np.linspace(-5.0, 5.0, 100)
        grid_y = np.linspace(-5.0, 5.0, 100)

        grid_x_2d, grid_y_2d = np.meshgrid(grid_x, grid_y)
        X_ref = grid_x
        Y_ref = grid_y
        Impsamp_ref = np.exp( - 0.045 * grid_x_2d ** 4 + grid_x_2d ** 2 - 0.5 * grid_y_2d ** 2)


    # vis directory
    vis_dir = os.path.join(exp_dir, "vis")
    fname = "{}_d{}.pkl".format(physys, dim)
    fname = os.path.join(vis_dir, fname)
    sample_dict = load(fname)

    if not physys.startswith('GL'):
        # we use the camera 
        fig, axes = plt.subplots(1, 3, figsize=(6.4 * 3, 4.8))
        camera = Camera(fig)

    # unpack the data
    Impsamp_ratio_list = sample_dict["Impsamp_ratio_list"]
    Impsamp_ratio_i_list = sample_dict["Impsamp_ratio_i_list"]
    D_list = sample_dict["D"]
    X_list = sample_dict["X"]
    Y_list = sample_dict["Y"]


    # Begin to plot 
    if physys.startswith('GL'): 

        fname = "{}_d{}.mp4".format(physys, dim)
        fname = os.path.join(vis_dir, fname)

        vis_fig_dir = os.path.join(vis_dir, 'figs')
        make_dir(vis_fig_dir)

        # because of the memory issue 
        def animate(i):
            plt.cla() 
            impsamp_ratio = Impsamp_ratio_list[i] 
            impsamp_ratio = impsamp_ratio / impsamp_ratio.mean()
            sns.distplot(react_coord_gt, bins=500, color='green')
            plt.hist(react_coord_gt, bins=500, align='left', density=True, label='ground truth')
            plt.hist(X_marginal, bins=500, align='left', weights=impsamp_ratio, density=True, label='weighted avg.')
            plt.legend(loc='upper right')
            ax.text(0.05, 0.9, 'iter: {}/{}'.format( naturalsize(i * viz_freq) , naturalsize(niters) ), transform=ax.transAxes)
            plt.ylim(0.0, 3.2)
            plt.grid()

            plt.savefig('{}/hist_{:03d}.png'.format(vis_fig_dir, i+1))

        fig, ax = plt.subplots()

        line, = ax.plot([], [], lw=2)
        # init function
        def init():
            return line,

        import matplotlib.animation as animation
        anim = animation.FuncAnimation(fig, animate, init_func=init, frames=tqdm(np.arange(len(Impsamp_ratio_list))))
        anim.save(fname, fps=15)

    else: 
        if _physys == 'mb' or _physys == 'dw': 
            for X, Y, Impsamp_ratio, D in tzip(X_list, Y_list, Impsamp_ratio_list, D_list):
            # for X, Y, Impsamp_i_ratio, D in tzip(X_list, Y_list, Impsamp_ratio_i_list, D_list):

                # Impsamp_ratio = Impsamp_i_ratio[0]
                # show the generated importance ratio
                ax = axes[0]
                ax.contourf(X, Y, Impsamp_ratio)

                # show the reference importance ratio
                ax = axes[1]
                ax.contourf(X_ref, Y_ref, Impsamp_ref)

                # show the discriminator
                ax = axes[2]
                ax.contourf(X, Y, D)
                
                camera.snap()

        elif _physys == 'period': 
            # this is for the period case 
            for X, Y, Impsamp_ratio, D in tzip(X_list, Y_list, Impsamp_ratio_list, D_list):
                ax = axes[0]
                cs = ax.contourf(X, Y, Impsamp_ratio, extent=[xmin, xmax, ymin, ymax],  extend='both')

                ax.contour(cs, colors='k')

                ax.set_xlim(xmin, xmax)
                ax.set_ylim(ymin, ymax)
                ax.grid(c='k', ls='-', alpha=0.3)

                ax = axes[1]
                ax.imshow(np.rot90(Impsamp_ratio_interpolation_ref), 
                    extent=[xmin, xmax, ymin, ymax], aspect="auto")

                ax.set_xlim(xmin, xmax)
                ax.set_ylim(ymin, ymax)
                ax.grid(c='k', ls='-', alpha=0.3)


                ax = axes[2]
                cs = ax.contourf(X, Y, D,extent=[xmin, xmax, ymin, ymax],  extend='both')

                ax.contour(cs, colors='k')
                ax.set_xlim(xmin, xmax)
                ax.set_ylim(ymin, ymax)
                ax.grid(c='k', ls='-', alpha=0.3)

                camera.snap()

        else: 
            raise NotImplementedError("Not implemented for other physics systems ")

        animation = camera.animate()
        fname = "{}_d{}.mp4".format(physys, dim)
        fname = os.path.join(vis_dir, fname)
        animation.save(fname)



  