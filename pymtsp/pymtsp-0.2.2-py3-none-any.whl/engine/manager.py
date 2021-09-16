import operator

import numpy as np

from pymtsp.engine.city import City
from pymtsp.engine.depot import Depot
from pymtsp.engine.salesman import calc_dist, Salesman
from pymtsp.engine.status import CityStatus, SalesmanStatus


def filter_dict(info: dict, status, return_idx=True):
    ret = dict(filter(lambda elem: elem[1].status == status, info.items()))
    if return_idx:
        ret = list(ret.keys())
    return ret


class mTSPManager:

    def __init__(self,
                 m: int,
                 coords: np.array):
        super(mTSPManager, self).__init__()

        self.n = coords.shape[0]
        self.n_cities = coords.shape[0] - 1
        self.m = m
        self.coords = coords

        self.depot = Depot(idx=0, loc=coords[0])
        self.cities = {_n + 1: City(idx=_n + 1, loc=coords[_n + 1]) for _n in range(self.n_cities)}
        self.salesmen = {_m: Salesman(idx=_m, first_city=self.depot) for _m in range(self.m)}
        self.time = 0.0
        self.target_agent = None

    def get_idle_agents(self, return_idx=True):
        return filter_dict(self.salesmen, SalesmanStatus.IDLE, return_idx)

    def get_assigned_agents(self, return_idx=True):
        return filter_dict(self.salesmen, SalesmanStatus.ASSIGNED, return_idx)

    def get_inactive_agents(self, return_idx=True):
        return filter_dict(self.salesmen, SalesmanStatus.INACTIVE, return_idx)

    def get_active_cities(self, return_idx=True):
        return filter_dict(self.cities, CityStatus.IDLE, return_idx)

    def get_inactive_cities(self, return_idx=True):
        return filter_dict(self.cities, CityStatus.INACTIVE, return_idx)

    def get_non_depot_returning_agents(self):
        return dict(filter(lambda elem: elem[1].is_returning == False, self.salesmen.items()))

    def get_depot_returning_agents(self):
        return dict(filter(lambda elem: elem[1].is_returning == True, self.salesmen.items()))

    def set_target_agent(self):
        idle_agents = self.get_idle_agents()
        assert len(idle_agents) >= 1

        if self.target_agent is not None:
            self.salesmen[self.target_agent].is_target = False

        target_idx = np.random.choice(idle_agents)
        self.salesmen[target_idx].is_target = True
        self.target_agent = target_idx

    def set_next_city(self, agent_idx, next_city_idx):
        if next_city_idx == 0:  # when salesmen choose to early depot return
            self.salesmen[agent_idx].set_next_city(self.depot)
        else:
            self.salesmen[agent_idx].set_next_city(self.cities[next_city_idx])

    def transit(self):
        # check all agents are not idle
        assert len(self.get_idle_agents()) == 0

        # find event-triggering time and simulate
        # while loop is introduced since the event-triggering time
        # can be for the depot-retuning
        dt = 0.0
        while len(self.get_idle_agents()) == 0:
            assigned_agents = self.get_assigned_agents(False)
            _dt = min([v.remaining_distance for v in assigned_agents.values()])
            for agent in assigned_agents.values():
                agent.simulate(_dt)
            dt += _dt

        self.time += dt

    def transit_last(self, endgame_strategy):
        if endgame_strategy == 'min_tourlen_incr':
            self.transit_last_min_tourlen_incr()
        elif endgame_strategy == 'none':
            self.transit_last_none()

    def transit_last_none(self):
        # needs_to_return_agents = self.get_assigned_agents(return_idx=False)
        non_depot_returning_agents = self.get_non_depot_returning_agents()

        # agents that are already on the way to depot.
        depot_returning_agent = self.get_assigned_agents(False)
        non_depot_returning_agents.update(depot_returning_agent)

        need_to_return_completion_time = -float('inf')
        for agent in non_depot_returning_agents.values():
            dt = 0.0
            if agent.status == SalesmanStatus.ASSIGNED:
                dt += agent.remaining_distance
                agent.simulate(agent.remaining_distance)

            if agent.status != SalesmanStatus.INACTIVE:
                agent.set_next_city(self.depot)
                dt += agent.remaining_distance
                agent.simulate(agent.remaining_distance)

            if dt >= need_to_return_completion_time:
                need_to_return_completion_time = dt

        self.time += need_to_return_completion_time

    def transit_last_min_tourlen_incr(self):
        # remaining only one unvisited city and may have multiple salesmen
        # therefore, this state-action selection is not subject of learning
        # "apply heuristics that minimally increase makespan"

        assert len(self.get_active_cities(return_idx=True)) == 1
        remaining_city = self.cities[self.get_active_cities(return_idx=True)[0]]
        non_depot_returning_agents = self.get_non_depot_returning_agents()

        def calc_remaining_cost(agent):
            finish_sub_tour = agent.remaining_distance  # to finish current subtour
            next_loc = agent.loc if finish_sub_tour == 0.0 else agent.next_city.loc
            additional_tour = calc_dist(next_loc, remaining_city.loc)  # to tour next city -> remaining city
            depot_returning = calc_dist(remaining_city.loc, self.depot.loc)  # returning to the depot
            return finish_sub_tour + additional_tour + depot_returning

        remain_cost = {k: calc_remaining_cost(v) for k, v in non_depot_returning_agents.items()}
        agent_idx = min(remain_cost.items(), key=operator.itemgetter(1))[0]

        # finish current tour and return to the depot
        remain_completion_time = - float('inf')
        for agent in non_depot_returning_agents.keys():
            dt = 0.0
            # finish current tour if required
            if self.salesmen[agent].status == SalesmanStatus.ASSIGNED:
                dt += self.salesmen[agent].remaining_distance
                self.salesmen[agent].simulate(self.salesmen[agent].remaining_distance)

            if agent == agent_idx:
                self.salesmen[agent].set_next_city(remaining_city)
                dt += self.salesmen[agent].remaining_distance
                self.salesmen[agent].simulate(self.salesmen[agent].remaining_distance)

            # append depot
            self.salesmen[agent].set_next_city(self.depot)
            dt += self.salesmen[agent].remaining_distance
            self.salesmen[agent].simulate(self.salesmen[agent].remaining_distance)

            if dt >= remain_completion_time:
                remain_completion_time = dt

        # finish tours of already depot returning agents if needed.
        # Kinda not best design choice but still works!!!!!
        # the logic is as follows:
        # 1. we already complete the tours of the salesmen those were not decided to visit the depot
        # 2. However, there might be salesmen who are not come back to depot yet.
        #    Those are the salesmen who already on their way to depot, when we firstly calculate remaining costs
        # Here, we finish the tours of those salesmen if needed. And update the simulator time accordingly.

        needs_to_return_agents = self.get_assigned_agents(return_idx=False)
        if len(needs_to_return_agents) > 0:
            need_to_return_completion_time = -float('inf')
            for agent in needs_to_return_agents.values():
                dt = agent.remaining_distance
                agent.simulate(agent.remaining_distance)

                if dt >= need_to_return_completion_time:
                    need_to_return_completion_time = dt

            remain_completion_time = max(remain_completion_time, need_to_return_completion_time)

        self.time += remain_completion_time

    def state_dict(self):

        # static states
        state_dict = dict()
        state_dict['n'] = self.n
        state_dict['n_cities'] = self.n_cities
        state_dict['m'] = self.m
        state_dict['coords'] = self.coords

        # dynamic states
        state_dict['depot'] = self.depot.state_dict()
        state_dict['cities'] = {k: v.state_dict() for k, v in self.cities.items()}
        state_dict['salesmen'] = {k: v.state_dict() for k, v in self.salesmen.items()}

        state_dict['time'] = self.time
        state_dict['target_agent'] = self.target_agent

        return state_dict

    @classmethod
    def from_state_dict(cls, state_dict):
        manager = cls(m=state_dict['m'],
                      coords=state_dict['coords'])
        manager.depot = Depot.from_state_dict(state_dict['depot'])
        manager.cities = {k: City.from_state_dict(v) for k, v in state_dict['cities'].items()}

        salesmen = dict()
        for sm_idx, state in state_dict['salesmen'].items():
            cur_city_idx = state['cur_city_idx']
            cur_city = manager.depot if cur_city_idx == 0 else manager.cities[cur_city_idx]

            next_city_idx = state['next_city_idx']
            if next_city_idx is not None:
                next_city = manager.depot if next_city_idx == 0 else manager.cities[next_city_idx]
            else:
                next_city = None
            salesmen[sm_idx] = Salesman.from_state_dict(state, cur_city, next_city)
        manager.salesmen = salesmen

        manager.time = state_dict['time']
        manager.target_agent = state_dict['target_agent']
        return manager
