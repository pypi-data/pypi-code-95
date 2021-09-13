from copy import deepcopy

import numpy as np

from pymtsp.engine.manager import mTSPManager
from pymtsp.utils.generate_coords import get_uniform_coords
from pymtsp.utils.observations import default_obs_func
from pymtsp.utils.process_tour_dict import process_tour_info
from pymtsp.utils.rewards import default_reward_func


class mTSPenv:
    """
    Single depot-returning mTSP environment.
    """

    def __init__(self,
                 m: int,
                 n: int = None,
                 coords: np.array = None,
                 allow_early_return: bool = True,
                 observation_func=default_obs_func,
                 reward_func=default_reward_func,
                 endgame_strategy: str = 'min_tourlen_incr',
                 verbose: bool = False):

        """
        :param m: (int) Number of salesmen. >= 1
        :param n: (int) Number of cities including the depot
        :param coords: (np.array) 2D coordinates of cities; [n x 2]
        :param allow_early_return: (bool) whether to allow salesmen return to the depot before visiting all cities.
        :param observation_func: (a callable function) observation function; f(self) -> observation
        :param reward_func: (a callable function) reward function; f(self) -> reward
        :param endgame_strategy: (str) The MDP termination heuristics. supports 'min_tourlen_incr' and 'none'.
        - 'min_tourlen_incr' considers the state with "two" unvisited cities as the previous state of the terminal state.
           Once the assigment for one of the two cities are made, the remaining city is automatically assigned to the
           agents that doesn't return the depot and minimally increase the tour length.
        - 'none' do not use any endgame strategy. In this mode, the previous state of the terminal state becomes the state
           where only one city is unvisited.
        :param verbose: (bool)
        """

        assert n is not None or coords is not None, "Required to specify 'n' or 'coords'"
        assert endgame_strategy in ['min_tourlen_incr', 'none']

        self.m = m
        self.n = coords.shape[0] if n is None else n
        self.coords = get_uniform_coords(n) if coords is None else coords

        self.allow_early_return = allow_early_return
        self.verbose = verbose
        self.observation_func = default_obs_func if observation_func is None else observation_func
        self.reward_func = default_reward_func if reward_func is None else reward_func
        self.endgame_strategy = endgame_strategy

        self.manager = None
        self.event_counter = 0
        self.done = False

        self.prev_event_time = 0.0
        _ = self.reset()

    def step(self, action):
        if self.verbose:
            print(
                "[Event {}] | Assigning City {} to Salesman {}".format(self.event_counter,
                                                                       action,
                                                                       self.target_agent))
        self.manager.set_next_city(self.target_agent, action)
        self.event_counter += 1

        # check "all assigned" and
        # if "all assigned" transit the simulator state until the next event
        if len(self.manager.get_idle_agents()) == 0:
            if self.verbose:
                print("[Event {}] | Simulate Tour(s)".format(self.event_counter))
            self.manager.transit()

        if self.check_last_state():
            self.manager.transit_last(self.endgame_strategy)
            self.done = True
        else:
            self.manager.set_target_agent()
            self.done = False

        reward = self.reward_func(self)
        obs = self.observation_func(self)
        done = self.done

        self.prev_event_time = self.manager.time  # update simulation time
        return obs, reward, done

    def check_last_state(self):
        if self.endgame_strategy == 'min_tourlen_incr':
            is_last_state = True if len(self.manager.get_active_cities()) == 1 else False
        elif self.endgame_strategy == 'none':
            is_last_state = True if len(self.manager.get_active_cities()) == 0 else False
        else:
            raise RuntimeError("Not Implemented endgame strategy")
        return is_last_state

    def get_action_space(self):
        action_space = self.manager.get_active_cities()
        if self.allow_early_return:
            # check whether "early returning is actually possible"
            # if not all agents except the target agent are already depot-returning
            early_returning_cond = len(self.manager.get_depot_returning_agents()) != self.m - 1
            zero_tour_cond = self.manager.salesmen[self.manager.target_agent].tour_length > 0.0
            if early_returning_cond and zero_tour_cond:
                action_space += [0]
        return action_space

    @property
    def target_agent(self):
        return self.manager.target_agent

    def reset(self):
        self.manager = mTSPManager(self.m, self.coords)
        self.event_counter = 0
        self.prev_event_time = 0.0
        self.manager.set_target_agent()
        self.done = False

        # TODO: state -> observation function
        state = self.observation_func(self)
        return state

    def state_dict(self):
        state_dict = {
            'm': self.m,
            'n': self.n,
            'allow_early_return': self.allow_early_return,
            'endgame_strategy': self.endgame_strategy,
            'manager_state': self.manager.state_dict(),
            'verbose': self.verbose,
            'event_counter': self.event_counter,
            'done': self.done,
            'prev_event_time': self.prev_event_time
        }
        return state_dict

    @classmethod
    def from_state_dict(cls, state, observation_func=None, reward_func=None):
        state = deepcopy(state)
        env = cls(m=state['m'],
                  n=state['n'],
                  coords=state['manager_state']['coords'],
                  allow_early_return=state['allow_early_return'],
                  endgame_strategy=state['endgame_strategy'],
                  observation_func=observation_func,
                  reward_func=reward_func,
                  verbose=state['verbose'])
        env.manager = mTSPManager.from_state_dict(state['manager_state'])
        env.event_counter = state['event_counter']
        env.done = state['done']
        env.prev_event_time = state['prev_event_time']
        return env

    def get_summary(self):
        info = dict()
        info['n'] = int(self.n)
        info['m'] = int(self.m)
        info['coords'] = self.coords

        if self.done:
            info['solve'] = True
        else:
            info['solve'] = False

        tour_dict = {idx: sm.tour_idx for idx, sm in self.manager.salesmen.items()}
        tl_dict, amp, ttl, n_inact = process_tour_info(tour_dict, self.coords)
        info['tours'] = tour_dict
        info['amplitude'] = amp
        info['total_length'] = ttl
        info['tour_length'] = tl_dict
        info['n_inactive'] = n_inact
        info['utilization'] = (self.m - n_inact) / self.m
        info['obj_val'] = max(tl_dict.values())

        return info
