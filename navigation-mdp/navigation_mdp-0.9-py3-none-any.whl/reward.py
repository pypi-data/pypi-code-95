from abc import ABC, abstractmethod
from .state import State, DiscreteStateSpace
import numpy as np
"""
Objective, Utility
"""

class AbstractStateRewardSpec(ABC):

    def __init__(self, key=None, feature_key=None, preprocess_fn=lambda x: x, postprocess_fn=lambda x: x):
        self.key = key
        self.feature_key = key if feature_key is None else feature_key
        self.preprocess_fn = preprocess_fn
        self.postprocess_fn = postprocess_fn

    def __call__(self, x):
        return self.reward(x)

    def get_key(self):
        return self.key

    def get_feature_key(self):
        return self.feature_key

    @abstractmethod
    def compute_state_reward(self, state):
        return

    @abstractmethod
    def compute_state_space_reward(self, discrete_state_space):
        return

    def reward(self, x):
        if isinstance(x, State):
            return self.compute_state_reward(x)
        elif isinstance(x, DiscreteStateSpace):
            return self.compute_state_space_reward(x)
        else:
            raise ValueError("Incorrect input in reward spec: {}".format(type(x)))

    def preprocess(self, features):
        return self.preprocess_fn(features)

    def postprocess(self, reward):
        return self.postprocess_fn(reward)

    def features(self, state):
        return self.preprocess(state.get_features(key=self.get_feature_key()))

    @abstractmethod
    def get_model(self):
        return


class RewardStateScalar(AbstractStateRewardSpec):

    def __init__(self, loc_to_reward_dict, class_id_to_reward_dict, default=0,
                 key=None, feature_key=None, preprocess_fn=lambda x: x, postprocess_fn=lambda x: x):
        super().__init__(key, feature_key, preprocess_fn, postprocess_fn)
        self.loc_to_reward_dict = loc_to_reward_dict
        self.class_id_to_reward_dict = class_id_to_reward_dict
        self.default = default

    def compute_state_reward(self, state):
        # loc_to_reward_dict overrides class_id_to_reward_dict
        if (self.loc_to_reward_dict is not None) and state.location in self.loc_to_reward_dict:
            return self.postprocess_fn(
                self.loc_to_reward_dict[self.preprocess_fn(state.location)]
            )
        elif (self.class_id_to_reward_dict is not None) and state.class_id in self.class_id_to_reward_dict:
            return self.postprocess_fn(
                self.class_id_to_reward_dict[self.preprocess_fn(state.class_id)]
            )
        else:
            return self.postprocess_fn(
                self.preprocess_fn(self.default)
            )

    def get_model(self):
        raise NotImplementedError

    def compute_state_space_reward(self, discrete_state_space):
        rewards = []
        for state in discrete_state_space:
            rewards.append(self.compute_state_reward(state))
        return rewards

class RewardStateFeatureModel(AbstractStateRewardSpec):

    def __init__(self, r_model, key=None, feature_key=None,
                 preprocess_fn=lambda x: x, postprocess_fn=lambda x: x):
        super().__init__(key, feature_key, preprocess_fn, postprocess_fn)
        self.r_model = r_model

    def compute_state_reward(self, state):
        return self.postprocess_fn(
            self.r_model(self.preprocess_fn(state.get_features(key=self.get_feature_key())))
        )

    def get_model(self):
        return self.r_model

    def compute_state_space_reward(self, discrete_state_space):
        PHI = np.asarray(discrete_state_space.features(loc=None, idx=None,
                                                       gridded=False, numpyize=False,
                                                       key=self.get_feature_key()))
        return self.postprocess_fn(
            self.r_model(self.preprocess_fn(PHI))
        )
