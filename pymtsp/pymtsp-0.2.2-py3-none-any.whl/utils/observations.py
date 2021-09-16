def default_obs_func(env):
    manager = env.manager
    obs = dict(
        depot=manager.depot,
        cities=manager.cities,
        salesmen=manager.salesmen)
    return obs

