import os

import torch
import torch.optim as optim
from sysflow.utils.common_utils.file_utils import dump, load, make_dir 
import wandb

from neuralsampler.networks import SmallMLP, resnet, net_fn
from neuralsampler.utils import *
from scipy.interpolate import griddata
from tqdm.autonotebook import trange
import math
import torch.nn as nn
import torch.nn.functional as F
from copy import deepcopy 
import collections
from prettytable import PrettyTable

class neuralsampler: 
    def __init__(self, args, exp_dir, logger): 
        # save the params 
        device = torch.device("cuda:" + str(0) if torch.cuda.is_available() else "cpu")

        #region unpack the params
        niters = args.niters
        batch_size = args.batch_size
        lr = args.lr
        weight_decay = args.weight_decay
        critic_weight_decay = args.critic_weight_decay
        viz_freq = args.viz_freq
        d_iters = args.d_iters
        g_iters = args.g_iters
        l2 = args.l2
        lr_D = args.lr_D
        hid_dim = args.hid_dim
        n_depth = args.n_depth
        use_resnet_G = args.use_resnet_G
        use_resnet_D = args.use_resnet_D
        physys = args.physys
        dim = args.dim
        G_path = args.G_path
        D_path = args.D_path
        use_spectrum = args.use_spectrum
        clip_D = args.clip_D
        clip_value = args.clip_value
        loss_A = args.loss_A
        mmd_ratio_in = args.mmd_ratio_in
        mmd_two_sample = args.mmd_two_sample
        mmd_beta = args.mmd_beta
        G_loss = args.G_loss
        disc_zero = args.disc_zero
        log_freq = args.log_freq
        max_lr_G = args.max_lr_G
        total_steps_G = args.total_steps_G
        warmup_pct_G = args.warmup_pct_G
        step_decay_factor_G = args.step_decay_factor_G
        step_decay_patience_G = args.step_decay_patience_G
        max_lr_D = args.max_lr_D
        total_steps_D = args.total_steps_D
        warmup_pct_D = args.warmup_pct_D
        step_decay_factor_D = args.step_decay_factor_D
        step_decay_patience_D = args.step_decay_patience_D
        decay_type = args.decay_type
        decay_power = args.decay_power
        loss_coeff = args.loss_coeff
        multiple_step_type = args.multiple_step_type
        #endregion

        #region define and init the networks or load the weights
        # ATTENTION (Sat 09/04/2021 16:51)
        # why not period here? 
        D = net_fn(dim, n_hid=hid_dim, n_depth=n_depth, n_out=1, UseSpectral=use_spectrum, use_resnet=use_resnet_D, period= physys.startswith('period'))
        G = net_fn(dim, n_hid=hid_dim, n_depth=n_depth, n_out=1, UseSpectral=use_spectrum, use_resnet=use_resnet_G, period= physys.startswith('period'))
        # D = net_fn(dim, n_hid=hid_dim, n_depth=n_depth, n_out=1, UseSpectral=use_spectrum, use_resnet=use_resnet_D)
        # G = net_fn(dim, n_hid=hid_dim, n_depth=n_depth, n_out=1, UseSpectral=use_spectrum, use_resnet=use_resnet_G)


        D.to(device)
        G.to(device)

        # load model 
        # pretrained model
        if G_path: 
            G_params = torch.load(G_path)
            G.load_state_dict(G_params)
        if D_path: 
            D_params = torch.load(D_path)
            D.load_state_dict(D_params)

        print()
        params_info = PrettyTable()
        params_info.field_names = ["", "Generator", "Discriminator"]
        params_info.add_row(["params counts", count_parmas(G), count_parmas(D)])
        print(params_info)

        logger.info(D)
        logger.info(G)
        #endregion

        #region define the optimizer and learning rate schedule
        G_optimizer = optim.Adam(
            G.parameters(), lr=lr, weight_decay=weight_decay, 
            # betas=(0.5, 0.9)
            betas=(0.9, 0.999)
        )

        D_optimizer = optim.Adam(
            D.parameters(),
            lr=lr_D,
            # betas=(0.5, 0.9),
            betas=(0.9, 0.999),
            weight_decay=critic_weight_decay,
        )

        G_scheduler1 = torch.optim.lr_scheduler.OneCycleLR(
            G_optimizer,
            div_factor=max_lr_G/lr, 
            max_lr=max_lr_G,
            total_steps=total_steps_G, 
            pct_start=warmup_pct_G,  # Warm up for 2% of the total training time
            final_div_factor=1
            )

        D_scheduler1 = torch.optim.lr_scheduler.OneCycleLR(
            D_optimizer,
            div_factor=max_lr_D/lr_D, 
            max_lr=max_lr_D, 
            total_steps=total_steps_D, 
            pct_start=warmup_pct_D,  # Warm up for 2% of the total training time
            final_div_factor=1
            )

        # other learning rate schedule 
        # algebraic learning rate decay 
        # or you can make this into a class 
        # TODO: one choice to wrap the above into a lr_schedule class 

        if decay_type == 'exp': 
            G_scheduler2 = optim.lr_scheduler.ReduceLROnPlateau(
                G_optimizer, factor=step_decay_factor_G, patience=step_decay_patience_G, verbose=True)
            D_scheduler2 = optim.lr_scheduler.ReduceLROnPlateau(
                D_optimizer, factor=step_decay_factor_D, patience=step_decay_patience_D, verbose=True)
        elif decay_type == 'algebraic': 
            # TODO: the coefficient before need to think about
            if decay_power == 1:
                lambda_schedule = lambda epoch: 1 / ( int(epoch/100) + 1)
                G_scheduler2 = optim.lr_scheduler.LambdaLR(G_optimizer, lr_lambda=lambda_schedule)
                D_scheduler2 = optim.lr_scheduler.LambdaLR(D_optimizer, lr_lambda=lambda_schedule)
            elif decay_power == 1/2: 
                lambda_schedule = lambda epoch: 1 / math.sqrt( int(epoch/100) + 1)
                G_scheduler2 = optim.lr_scheduler.LambdaLR(G_optimizer, lr_lambda=lambda_schedule)
                D_scheduler2 = optim.lr_scheduler.LambdaLR(D_optimizer, lr_lambda=lambda_schedule)
            else: 
                raise NotImplementedError("This algebraic decay power -- {} is not implemented".format(decay_power))
        else: 
            raise NotImplementedError("This decay type -- {} is not implemented".format(decay_type))
        #endregion
            
        #region pack the params
        self.device = device
        self.D = D
        self.G = G
        self.G_optimizer = G_optimizer
        self.D_optimizer = D_optimizer
        self.G_scheduler1 = G_scheduler1
        self.G_scheduler2 = G_scheduler2
        self.total_steps_G = total_steps_G
        self.total_steps_D = total_steps_D
        self.D_scheduler1 = D_scheduler1 
        self.D_scheduler2 = D_scheduler2
        self.logger = logger
        self.exp_dir = exp_dir
        self.niters = niters
        self.batch_size = batch_size
        self.lr = lr
        self.weight_decay = weight_decay
        self.critic_weight_decay = critic_weight_decay
        self.viz_freq = viz_freq
        self.d_iters = d_iters
        self.g_iters = g_iters
        self.l2 = l2
        self.lr_D = lr_D
        self.hid_dim = hid_dim
        self.physys = physys
        self.dim = dim
        self.G_path = G_path
        self.D_path = D_path
        self.use_spectrum = use_spectrum
        self.clip_D = clip_D
        self.clip_value = clip_value
        self.loss_A = loss_A
        self.mmd_ratio_in = mmd_ratio_in
        self.mmd_two_sample = mmd_two_sample
        self.mmd_beta = mmd_beta
        self.G_loss = G_loss
        self.disc_zero = disc_zero
        self.log_freq = log_freq
        self.decay_type = decay_type
        self.loss_coeff = loss_coeff
        #endregion


    def train(self): 
        #region unpack the params
        niters = self.niters
        batch_size = self.batch_size
        viz_freq = self.viz_freq
        d_iters = self.d_iters
        g_iters = self.g_iters
        l2 = self.l2
        physys = self.physys
        dim = self.dim
        device = self.device
        D = self.D
        G = self.G
        G_optimizer = self.G_optimizer
        D_optimizer = self.D_optimizer
        G_scheduler1 = self.G_scheduler1 
        G_scheduler2 = self.G_scheduler2 
        total_steps_G = self.total_steps_G 
        total_steps_D = self.total_steps_D 
        D_scheduler1 = self.D_scheduler1 
        D_scheduler2 = self.D_scheduler2 
        exp_dir = self.exp_dir
        clip_D = self.clip_D
        clip_value = self.clip_value
        loss_A = self.loss_A
        mmd_ratio_in = self.mmd_ratio_in
        mmd_two_sample = self.mmd_two_sample
        mmd_beta = self.mmd_beta
        G_loss = self.G_loss
        disc_zero = self.disc_zero
        log_freq = self.log_freq
        decay_type = self.decay_type
        loss_coeff = self.loss_coeff
        #endregion

        # swa average the weights
        N_avg_model = 20
        avg_freq = 10000
        avg_start = 1000
        G_avg_list = [torch.optim.swa_utils.AveragedModel(G) for i in range(N_avg_model)]

        G.train()
        D.train()

        #region get the data via the path (physys and dim)
        fname = "{}_d{}.pkl".format(physys, dim)
        fname = os.path.join("./dataset/traj", fname)        
        # add back (Sat 09/04/2021 16:36)
        data_dict = load(fname)

        # hack (Fri 08/27/2021 13:42)
        # fname = '/media/jimmy/TITAN1/StreamLine/neuralsampler/gen_dataset/period/period_alpha0.1_d3.pkl'
        # data_dict = load(fname)
        # remove the hack (Sat 09/04/2021 16:36)

        X, Y = data_dict['x'], data_dict['y']
        X = X[:int(1e7), :]

        # hack (Fri 08/27/2021 13:42)
        # Y = Y[-5:]
        # rm the hack (Sat 09/04/2021 16:36)

        # here can be changed to other case 
        Y = np.stack(Y, 1)
        Y = Y[:int(1e7),:]
        #endregion

        #region prepare for the visualization
        
        # number of samples to be visualized
        N_vis = 10000
        N_vis_sqrt = int(math.sqrt(N_vis))
        # load the data for the plots 
        if physys.startswith('dw'): 
            # TODO: change this to the init data 
            grid_x = np.linspace(-5.0, 5.0, N_vis_sqrt)
            grid_y = np.linspace(-5.0, 5.0, N_vis_sqrt)

            grid_x_2d, grid_y_2d = np.meshgrid(grid_x, grid_y)
            assert grid_x_2d.reshape(-1).shape[0] == N_vis

            assert dim >= 2

            x_vis_np = np.concatenate([grid_x_2d.reshape(-1, 1), grid_y_2d.reshape(-1, 1),  np.zeros((N_vis, dim -2))], axis=1)
            assert x_vis_np.shape[0] == N_vis and x_vis_np.shape[1] == dim

            grid_interpolate_map = lambda data_np: data_np.reshape((N_vis_sqrt, N_vis_sqrt))

        elif physys.startswith('mb'): 
            grid_x = np.linspace(-2, 1, N_vis_sqrt)
            grid_y = np.linspace(-0.5, 2.5, N_vis_sqrt)

            fname = "{}_d{}.pkl".format(physys, 2)
            # hack temporarily (Sun 09/05/2021 15:53)
            fname = os.path.join("./dataset/traj", fname)
            x_data = load(fname)
            x_vis_np = x_data["x"][:N_vis]

            xi_vis = x_vis_np[:, 0]
            yi_vis = x_vis_np[:, 1]
        
            assert dim >= 2

            x_vis_np = np.concatenate([x_vis_np, np.zeros((N_vis, dim-2))], axis=1)
            assert x_vis_np.shape[0] == N_vis and x_vis_np.shape[1] == dim

            grid_interpolate_map = lambda data_np: griddata((xi_vis, yi_vis), data_np, (grid_x[None,:], grid_y[:,None]), method='cubic')

        elif physys.startswith('period') or physys.startswith('period2'): 
            grid_x = np.linspace(-2.0, 2.0, N_vis_sqrt)
            grid_y = np.linspace(0.0, 1.0, N_vis_sqrt)

            grid_x_2d, grid_y_2d = np.meshgrid(grid_x, grid_y)
            assert grid_x_2d.reshape(-1).shape[0] == N_vis

            assert dim >= 2
            x_vis_np = np.concatenate([grid_x_2d.reshape(-1, 1), grid_y_2d.reshape(-1, 1),  np.zeros((N_vis, dim -2))], axis=1)
            assert x_vis_np.shape[0] == N_vis and x_vis_np.shape[1] == dim

            grid_interpolate_map = lambda data_np: data_np.reshape((N_vis_sqrt, N_vis_sqrt))

        elif physys.startswith('GL'): 
            fname = "{}_d{}.pkl".format(physys, dim)
            # change the init (Sun 09/05/2021 17:40)
            # the difference is the dimension here
            # fname = os.path.join("./dataset/init", fname)
            fname = os.path.join("./dataset/traj", fname)
            x_vis_np = load(fname)

            # TODO: this need to change
            # changed (Sun 09/05/2021 21:30)
            if isinstance(x_vis_np, dict):
                x_vis_np = x_vis_np['x'] 

            x_vis_np = x_vis_np[:N_vis, :]

        assert isinstance(x_vis_np, np.ndarray)
        x_vis_pt = torch.from_numpy(x_vis_np).requires_grad_(True).float().to(device)

        # vis directary
        vis_dir = os.path.join(exp_dir, "vis")
        make_dir(vis_dir)
        vis_fname = "{}_d{}.pkl".format(physys, dim)

        # for visualization
        X_list = []
        Y_list = []
        Impsamp_ratio_list = []
        Impsamp_ratio_i_list = []
        D_list = []
        #endregion

        # trainer the network
        for itr in trange(niters):
            G_optimizer.zero_grad()
            D_optimizer.zero_grad()
            
            #region sample 
            idx = np.random.choice(len(X), batch_size)
            x = X[idx]
            y = Y[idx]
            x = torch.tensor(x, requires_grad=True).float().to(device)
            y = torch.tensor(y, requires_grad=True).float().to(device)
            #endregion

            # loss: Σ exp(G(xi))/ Z delta_xi, Σ exp(G(xi))/ Z delta_yi
            potential = G(x)
            ratio = torch.exp( potential ) 
            ratio = ratio / ratio.mean()
            if y.shape[1] == 1: 
                D_diff = ratio * ( D(x) - D(y) )
            else: 
                D_diff = ratio.unsqueeze(-1) * ( D(x).unsqueeze(-1) - D(y) )

            loss_int = D_diff.mean(0)
            loss = D_diff.mean() 

            # lipschitz for Discriminator (gradient penalty)
            D_grad = keep_grad(  D(x).sum(), x)

            # two way for the l2 penalty 
            # zero or one 
            if disc_zero: 
                l2_penalty = (D_grad * D_grad).sum(1).mean() * l2  # penalty to enforce f \in F
            else: 
                l2_penalty = ( torch.norm(D_grad, dim=1) -1  ).square().mean() * l2  # penalty to enforce f \in F

            # adversarial training! (back prop)
            if d_iters > 0 and itr % (g_iters + d_iters) < d_iters : 
                (-1.0 * loss + l2_penalty).backward()
                D_optimizer.step()

                if clip_D: 
                    # Clip weights of discriminator
                    for p in D.parameters():
                        p.data.clamp_(-clip_value, clip_value)
                    
            else:
                loss.backward()
                G_optimizer.step()

                if itr > avg_start: 
                    num_model = itr // avg_freq
                    for i in range(num_model + 1): 
                        G_avg_list[i].update_parameters(G)
            
                if itr < total_steps_G: 
                    G_scheduler1.step()
                else: 
                    G_scheduler2.step(loss)

                if itr < total_steps_D: 
                    D_scheduler1.step()
                else: 
                    D_scheduler2.step(-1.0 * loss + l2_penalty)

            #region logging via wandb
            new_dict = { 
                'Discriminator': tc( -1.0 * loss + l2_penalty ), 
                'Generator (loss)': tc(loss), 
                'loss': tc(loss_int), 
                'l2 penalty': tc(l2_penalty), 
                'lr_D': D_optimizer.param_groups[0]["lr"],
                'lr_G': G_optimizer.param_groups[0]["lr"], 
            }

            wandb.log(new_dict)
            #endregion

            if itr % viz_freq == 0:

                # compute the importance weight for the instantaneous weights 
                potential_pt = G(x_vis_pt)
                potential_np = tc(potential_pt)
                impsamp_ratio_np = np.exp( potential_np )
                impsamp_ratio_np = impsamp_ratio_np / impsamp_ratio_np.mean() 
                if not physys.startswith('GL'):
                    impsamp_ratio_np = grid_interpolate_map(impsamp_ratio_np)

                # compute the importance sampling weight for the moving average weights 
                impsamp_ratio_i_list = []
                for i in range(20): 
                    impsamp_ratio_i_pt =  G_avg_list[i](x_vis_pt) 
                    impsamp_ratio_i_np = tc(impsamp_ratio_i_pt)
                    impsamp_ratio_i_np = np.exp( impsamp_ratio_i_np )
                    impsamp_ratio_i_np = impsamp_ratio_i_np / impsamp_ratio_i_np.mean() 
                    if not physys.startswith('GL'):
                        impsamp_ratio_i_np = grid_interpolate_map(impsamp_ratio_i_np)
                    impsamp_ratio_i_list.append(impsamp_ratio_i_np)

                # discriminator
                discr_pt = D(x_vis_pt)
                discr_np = tc(discr_pt)
                if not physys.startswith('GL'):
                    discr_np = grid_interpolate_map(discr_np)

                # store the data in the list
                if physys.startswith('GL'):
                    X_list.append([])
                    Y_list.append([])
                else:
                    X_list.append(grid_x)
                    Y_list.append(grid_y)

                Impsamp_ratio_list.append(impsamp_ratio_np)
                Impsamp_ratio_i_list.append(impsamp_ratio_i_list)
                D_list.append(discr_np)
                                        
            if itr % log_freq == 0: 
                # log the nn checkpoint 
                model_path = os.path.join(exp_dir, 'model')
                make_dir(model_path)
                torch.save(G.state_dict(), os.path.join(model_path, 'G.pt'))
                torch.save(D.state_dict(), os.path.join(model_path, 'D.pt'))
                
                # log the animation
                new_dict = { 
                    'X': X_list, 
                    'Y': Y_list, 
                    'Impsamp_ratio_list': Impsamp_ratio_list,
                    'Impsamp_ratio_i_list': Impsamp_ratio_i_list,
                    'D': D_list
                }

                # vis directary
                vis_dir = os.path.join(exp_dir, "vis")
                make_dir(vis_dir)
                fname = "{}_d{}.pkl".format(physys, dim)
                dump(new_dict, os.path.join(vis_dir, fname))

        # dump the data 
        new_dict = { 
            'X': X_list, 
            'Y': Y_list, 
            'Impsamp_ratio_list': Impsamp_ratio_list,
            'Impsamp_ratio_i_list': Impsamp_ratio_i_list,
            'D': D_list
        }
        dump(new_dict, os.path.join(vis_dir, vis_fname))
