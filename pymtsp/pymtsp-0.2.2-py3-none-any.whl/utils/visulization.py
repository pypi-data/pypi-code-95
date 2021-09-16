import matplotlib.pyplot as plt

from pymtsp.engine.city import CityStatus
from pymtsp.engine.manager import mTSPManager


def get_color(city):
    status = city.status
    if status == CityStatus.IDLE:
        color = 'gray'
    elif status == CityStatus.ASSIGNED:
        color = 'C{}'.format(city.assigned_by)
    elif status == CityStatus.INACTIVE:
        color = 'C{}'.format(city.assigned_by)
    else:
        raise RuntimeError("Not defined status")
    return color


def visualize_solution(manager_or_env):
    if isinstance(manager_or_env, mTSPManager):
        manager = manager_or_env
    else:
        manager = manager_or_env.manager

    x = manager.coords[:, 0]
    y = manager.coords[:, 1]

    city_clrs = [get_color(city) for city in manager.cities.values()]

    fig, ax = plt.subplots(1, 1, figsize=(5, 5))
    ax.scatter(x[1:], y[1:], c=city_clrs,
               label='city')
    ax.scatter(x[0], y[0], c='C2',
               marker='^', label='depot')

    for idx, sm in manager.salesmen.items():
        tour_x, tour_y = x[sm.tour_idx], y[sm.tour_idx]
        ax.plot(tour_x, tour_y,
                color='C{}'.format(idx))

        ax.scatter(sm.loc[0], sm.loc[1],
                   label='Agent {}'.format(idx),
                   marker='*',
                   color='C{}'.format(idx))

        # visualizing current tour
        if sm.next_city is not None:
            cur_city_loc = sm.cur_city.loc
            next_city_loc = sm.next_city.loc
            cur_loc = sm.loc
            ax.plot([cur_city_loc[0], next_city_loc[0]],
                    [cur_city_loc[1], next_city_loc[1]],
                    ls='--', color='gray')
            ax.plot([cur_city_loc[0], cur_loc[0]],
                    [cur_city_loc[1], cur_loc[1]],
                    color='C{}'.format(sm.idx))

    plt.legend(loc='best')
    ax.legend()
