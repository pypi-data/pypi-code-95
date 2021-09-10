import itertools
import numpy as np
import navigation_mdp as NvMDP
"""
Guacamole
"""

class DiscreteLfDWorld2D:
    ''' Discrete World specification class '''

    def __init__(self, discrete_state_space, phi_spec, r_spec, slip_prob=0.,
                 s_lst_lst=None, a_lst_lst=None, class_ids=None):
        self.S = discrete_state_space
        self.phi_spec = phi_spec
        self.r_spec = r_spec
        self.class_ids = class_ids
        self.T = NvMDP.dynamics.XYDynamics(self.S, slip_prob=slip_prob)
        self.s_lst_lst = []
        self.a_lst_lst = []
        self.tau_lst = []
        self.attach_classes(class_ids)
        self.attach_feature_spec(phi_spec)
        self.attach_reward_spec(r_spec)
        self.add_trajectories(s_lst_lst, a_lst_lst)

    def attach_classes(self, class_ids):
        self.class_ids = class_ids
        self.S.attach_classes(class_ids)

    def clear_feature_spec(self):
        self.S.clear_feature_spec()

    def attach_feature_spec(self, phi_spec):
        self.phi_spec = phi_spec
        if isinstance(phi_spec, list):
            for __phi_spec in phi_spec:
                assert isinstance(__phi_spec, NvMDP.features.AbstractStateFeatureSpec), \
                    "Invalid feature spec. Supported type: {}".format(NvMDP.features.AbstractStateFeatureSpec)
                self.S.attach_feature_spec(__phi_spec)
        else:
            assert isinstance(phi_spec, NvMDP.features.AbstractStateFeatureSpec), \
                "Invalid feature spec. Supported type: {}".format(NvMDP.features.AbstractStateFeatureSpec)
            self.S.attach_feature_spec(phi_spec)

    def clear_reward_spec(self):
        self.S.clear_reward_spec()

    def attach_reward_spec(self, r_spec):
        self.r_spec = r_spec
        if isinstance(r_spec, list):
            for __r_spec in r_spec:
                assert isinstance(__r_spec, NvMDP.reward.AbstractStateRewardSpec), \
                    "Invalid reward spec. Supported type: {}".format(NvMDP.reward.AbstractStateRewardSpec)
                self.S.attach_reward_spec(__r_spec)
        else:
            assert isinstance(r_spec, NvMDP.reward.AbstractStateRewardSpec), \
                "Invalid reward spec. Supported type: {}".format(NvMDP.reward.AbstractStateRewardSpec)
            self.S.attach_reward_spec(r_spec)

    def state_space(self):
        return self.S

    def features(self, loc=None, idx=None, gridded=False, numpyize=True, key=None):
        return self.S.features(loc=loc, idx=idx, gridded=gridded, numpyize=numpyize, key=key)

    def dim_features(self, key=None):
        return self.S[0].get_features(key=key).shape

    def actions(self):
        return self.dynamics().actions()

    def rewards(self, numpyize=True, gridded=False, key=None):
        return self.S.rewards(numpyize=numpyize, gridded=gridded, key=key)

    def dynamics(self):
        return self.T

    def trajectories(self, s_a_zipped=False):
        if s_a_zipped:
            return self.tau_lst
        else:
            return self.s_lst_lst, self.a_lst_lst

    def clear_trajectories(self):
        self.s_lst_lst = []
        self.a_lst_lst = []
        self.tau_lst = []

    def _update_tau_lst(self):
        self.tau_lst = self._get_tau_lst(self.s_lst_lst, self.a_lst_lst)

    def _get_tau_lst(self, s_lst_lst, a_lst_lst):
        return [list(zip(s_lst_lst[i], a_lst_lst[i])) for i in range(len(s_lst_lst))]

    def add_trajectory(self, s_lst, a_lst=None):
        if s_lst is not None:
            if a_lst is None:
                a_lst = self.T.loc_lst_to_a_lst(s_lst)
            self.s_lst_lst.append(s_lst)
            self.a_lst_lst.append(a_lst)
            self._update_tau_lst()

    def add_trajectories(self, s_lst_lst, a_lst_lst=None):
        if s_lst_lst is not None:
            if a_lst_lst is None:
                a_lst_lst = []
                for s_lst in s_lst_lst:
                    a_lst_lst.append(self.T.loc_lst_to_a_lst(s_lst))
            for s_lst, a_lst in zip(s_lst_lst, a_lst_lst):
                self.s_lst_lst.append(s_lst)
                self.a_lst_lst.append(a_lst)
            self._update_tau_lst()

    def to_grid(self, values):
        return self.S._organize_to_grid(values)

    def state_dims(self):
        return self.S.shape()

    def get_feture_shape(self, key):
        return self.S[0].get_features(key=key).shape

    def get_reward_model(self, key):
        return self.S[0].get_reward_spec(key).r_model

    def reward(self, state, key):
        return self.S[0].get_reward_spec(key)(state)

    def preprocess(self, features, reward_key):
        return self.S[0].get_reward_spec(reward_key).preprocess(features)

    def preprocessed_features_lst(self, f_key, r_key):
        return self.preprocess(
            self.features(numpyize=False, key=f_key), r_key)

    def postprocess(self, rewards, reward_key):
        return self.S[0].get_reward_spec(reward_key).postprocess(rewards)
