import numpy as np
# Navigation Views
import navigation_vis.Raster as NavGridView
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib import cm as cm, pyplot as plt, colors as mplotcolors


def plot_grid_data_helper(data, ann=None, ann_sz=12, ann_col="black", title=None, grid=None, cmap=cm.viridis, **kwargs):
    p = NavGridView.Raster(data, ax=plt.gca()).render(cmap=cmap, **kwargs).ticks(minor=False)
    if ann is not None:
        p.show_cell_text(ann, fontsize=ann_sz, color_cb=lambda x: ann_col)
    if grid is not None:
        p.grid()
    if title is not None:
        p.title(title)
    return p

def highlight_cell(x, y, ax=None, **kwargs):
    rect = plt.Rectangle((x-.5, y-.5), 1, 1, fill=False, **kwargs)
    ax = ax or plt.gca()
    ax.add_patch(rect)
    return rect

def plot_irl_world(S, s_lst_lst=[], titles=["States", "Classes", "Features", "Rewards"],
                   figsize=(18, 12), cbar_pad=1.0, cbar_size="10%",
                   r_key=None, phi_key=None, r_round_to=3, clean_title=False,
                   v_range=[None, None, None, None]):
    state_title, class_title, feature_title, reward_title = titles
    v_range = [(None, None) if v is None else v for v in v_range]
    state_range, class_range, feature_range, reward_range = v_range
    if not clean_title:
        feature_title += "(type={})".format(phi_key)
        reward_title += "(type={})".format(r_key)

    plt.figure(figsize=figsize)
    p = NavGridViewPlotter(S, r_key=r_key, phi_key=phi_key)
    plt.subplot(2, 2, 1)
    p.plot_states(
        cmap=cm.viridis, ann_col="white",
        title=state_title, vmin=state_range[0], vmax=state_range[1]).colorbar(
        where="left", pad=cbar_pad, size=cbar_size).grid().add_pixel_trajectories(
        s_lst_lst, arrow_props={"lw": 3, "color": "black", "shrinkB": 10, "shrinkA": 10})
    plt.subplot(2, 2, 2)
    p.plot_classes(
        cmap=cm.viridis, ann_col="white",
        title=class_title, vmin=class_range[0], vmax=class_range[1]).colorbar(
        where="right", pad=cbar_pad, size=cbar_size).grid()
    plt.subplot(2, 2, 3)
    p.plot_features(
        ann=S.idxs.flatten(), cmap=None, ann_col="white",
        title=feature_title, vmin=feature_range[0], vmax=feature_range[1]).colorbar(
        where="left", pad=cbar_pad, size=cbar_size).grid().add_trajectories(
        s_lst_lst, arrow_props={"lw": 3, "color": "black", "shrinkB": 10, "shrinkA": 10})
    plt.subplot(2, 2, 4)
    p.plot_array(
        S.rewards(numpyize=True, key=r_key).round(r_round_to),
        cmap=cm.Blues_r, title=reward_title, vmin=reward_range[0], vmax=reward_range[1]).colorbar(
        where="right", pad=cbar_pad, size=cbar_size)
    plt.tight_layout()


def plot_irl_results(S, s_lst_lst, values, loglik_hist,
                     titles=["States", "Features", "Rewards", "Values", "Training Performance"],
                     figsize=(24, 24), cbar_pad=1.0, cbar_size="10%",
                     r_key=None, phi_key=None, r_round_to=3, clean_title=False,
                     v_range=[None, None, None, None, None], learned_lst_lst=[]):
    state_title, feature_title, reward_title, value_title, perf_title = titles
    v_range = [(None, None) if v is None else v for v in v_range]
    state_range, feature_range, reward_range, value_range, _ = v_range
    if not clean_title:
        feature_title += "(type={})".format(phi_key)
        reward_title += "(type={})".format(r_key)

    plt.figure(figsize=figsize)
    p = NavGridViewPlotter(S, r_key=r_key, phi_key=phi_key)
    plt.subplot(3, 2, 1)
    p.plot_states(
        cmap=cm.viridis, ann_col="white",
        title=state_title, vmin=state_range[0], vmax=state_range[1]).colorbar(
        where="left", pad=cbar_pad, size=cbar_size).grid().add_pixel_trajectories(
        s_lst_lst, arrow_props={"lw": 3, "color": "black", "shrinkB": 10, "shrinkA": 10})
    plt.subplot(3, 2, 2)
    p.plot_features(
        ann=S.idxs.flatten(), cmap=cm.viridis, ann_col="white",
        title=feature_title, vmin=feature_range[0], vmax=feature_range[1]).colorbar(
        where="right", pad=cbar_pad, size=cbar_size).grid().add_trajectories(
        s_lst_lst, arrow_props={"lw": 3, "color": "black", "shrinkB": 10, "shrinkA": 10})
    plt.subplot(3, 2, 3)
    p.plot_array(
        S.rewards(numpyize=True, key=r_key).round(r_round_to),
        cmap=cm.Blues_r, title=reward_title, vmin=reward_range[0], vmax=reward_range[1]).colorbar(
        where="left", pad=cbar_pad, size=cbar_size).add_pixel_trajectories(
        learned_lst_lst, arrow_props={"lw": 3, "color": "black", "shrinkB": 10, "shrinkA": 10})
    plt.subplot(3, 2, 4)
    p.plot_array(
        values, cmap=cm.Blues_r, title=value_title, vmin=value_range[0], vmax=value_range[1]).colorbar(
        where="right", pad=cbar_pad, size=cbar_size).add_pixel_trajectories(
        learned_lst_lst, arrow_props={"lw": 3, "color": "black", "shrinkB": 10, "shrinkA": 10})
    plt.subplot(3, 2, 5)
    plt.plot(list(range(len(loglik_hist))), loglik_hist)
    plt.xlabel("Iteration")
    plt.ylabel("Likelihood")
    plt.title(perf_title)
    plt.tight_layout()

class NavGridViewPlotter:
    def __init__(self, S, R=None, cartesian=False, r_key=None, phi_key=None):
        self.S = S
        self.R = S.rewards(key=r_key) if R is None else R
        self.PHI_gridded = self.S.features(gridded=True, key=phi_key)
        self.R_grided = self.S._organize_to_grid(self.R)
        self.class_ids_grided = self.S._organize_to_grid(self.S.class_ids)
        self.idxs_gridded = self.S.idxs
        self.cartesian = cartesian
        self.p = None

    def highlight_terminal_states(self):
        for s in self.S.get_terminal_states():
            r, c = s.location
            highlight_cell(c, r, ax=self.p.ax, color="white", linewidth=5)

    def plot_rewards(self, title="Rewards", *args, **kwargs):
        data = self.R_grided[..., np.newaxis, np.newaxis, np.newaxis]
        ann = self.R
        self.p = plot_grid_data_helper(data, ann, title=title, *args, **kwargs)
        if self.cartesian:
            self.p.ax.invert_yaxis()
        return self.p

    def plot_states(self, title="States", *args, **kwargs):
        data = self.idxs_gridded[..., np.newaxis, np.newaxis, np.newaxis]
        ann = self.S.idxs.flatten()
        self.p = plot_grid_data_helper(data, ann, title=title, *args, **kwargs)
        self.highlight_terminal_states()
        if self.cartesian:
            self.p.ax.invert_yaxis()
        return self.p

    def plot_array(self, data, title="Data", *args, **kwargs):
        data = self.S._organize_to_grid(np.asarray(data).flatten())[..., np.newaxis, np.newaxis, np.newaxis]
        ann = data.flatten()
        self.p = plot_grid_data_helper(data, ann, title=title, *args, **kwargs)
        if self.cartesian:
            self.p.ax.invert_yaxis()
        return self.p

    def plot_classes(self, title="Classes", *args, **kwargs):
        data = self.class_ids_grided[..., np.newaxis, np.newaxis, np.newaxis]
        ann = self.S.class_ids
        self.p = plot_grid_data_helper(data, ann, title=title, *args, **kwargs)
        self.highlight_terminal_states()
        if self.cartesian:
            self.p.ax.invert_yaxis()
        return self.p

    def plot_features(self, ann=None, title="Features", *args, **kwargs):
        if self.cartesian:
            data = NavGridView.flip_y_axis(self.PHI_gridded)
        else:
            data = self.PHI_gridded
        n_dim = len(data.shape)
        if n_dim == 3: # one-hot features
            H, W, K = data.shape
            if K < 10:
                data = data[..., np.newaxis, np.newaxis]
            else:
                # k1 = int(np.ceil(np.sqrt(K)))
                # k2 = int(np.ceil(K / k1))
                try:
                    k1 = H
                    k2 = W
                    data = data.reshape(H, W, k1, k2)[..., np.newaxis]
                except:
                    data = data.reshape(H, W, K, 1)[..., np.newaxis]
        elif n_dim == 4:
            data = data[..., np.newaxis]
        elif n_dim == 5:
            pass
        else:
            raise Exception("data dimension {} not supported!".format(n_dim))

        if ann is None:
            ann = self.S.class_ids
        ann = np.asarray(ann).flatten()
        self.p = plot_grid_data_helper(data, ann, title=title, *args, **kwargs)
        if self.cartesian:
            self.p.ax.invert_yaxis()
        return self.p

    def add_colorbar(self, *args, **kwargs):
        self.p.colorbar(*args, **kwargs)
        return self

    def add_trajectories(self, *args, ** kwargs):
        self.p.add_trajectories(*args, **kwargs)
        return self
