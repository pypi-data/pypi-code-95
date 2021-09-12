import time
def fps(env,steps_per_test=100,episode=10):
    for e in range(episode):
        count=0
        start_t=time.time()
        for i in range(steps_per_test):
            a = env.action_space.sample()  # Sample an action
            obs, reward, done, info = env.step(a)  # Step the environoment with the sampled random action
            if done:
                obs = env.reset()  # Reset environment
            # env.step(env.action_space.sample())
        env.reset() 
        dt=time.time()-start_t
        print("fps = {}".format(steps_per_test/dt))