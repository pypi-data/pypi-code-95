def default_reward_func(env):
    # makespan reward (a.k.a completion time)
    makespan = 0 if not env.done else env.manager.time
    reward = -1.0 * makespan
    return reward


def dt_reward(env):
    prev_time = env.prev_event_time
    cur_time = env.manager.time
    dt = cur_time - prev_time
    reward = -1.0 * dt
    return reward
