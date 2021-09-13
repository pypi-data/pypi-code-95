from gym.wrappers import TimeLimit
from stable_baselines3.common.vec_env import SubprocVecEnv
# noinspection PyUnresolvedReferences
import pogema
import gym
from stable_baselines3 import PPO

import wandb

from pogema import GridConfig
from pogema.wrappers.reward_wrappers import TrueRewardWrapper, PrimalRewardWrapper
from pogema.wrappers.seed_wrapper import SeedWrapper


def make(config):
    env = gym.make("SingleAgentPogema-v0", config=config)
    env = TimeLimit(env, 16)
    return env


def run_sb3(config, use_wandb=False):
    policy_kwargs = dict(net_arch=[512, 512])
    project_name = 'pogema-sb3'
    if use_wandb:
        wb = wandb.init(project=project_name, sync_tensorboard=True, config=config)
    else:
        wb = None
    grid_config = GridConfig(num_agents=1, obs_radius=5, density=0.3, size=8)
    seeds = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    eval_env = SeedWrapper(gym.make("SingleAgentPogema-v0", config=grid_config), seeds=seeds)
    num_proc = 16

    if config['reward'] == 'true':
        env = SubprocVecEnv([lambda: TrueRewardWrapper(make(grid_config)) for _ in range(num_proc)])
    elif config['reward'] == 'success_rate':
        env = SubprocVecEnv([lambda: make(grid_config) for _ in range(num_proc)])
    elif config['reward'] == 'primal':
        env = SubprocVecEnv([lambda: PrimalRewardWrapper(make(grid_config)) for _ in range(num_proc)])
    else:
        raise KeyError

    agent = PPO('MlpPolicy', env, verbose=1, policy_kwargs=policy_kwargs,
                tensorboard_log='./pogema-sb3-2' + config['reward'])
    agent.learn(2000000, eval_env=eval_env, eval_freq=1000, n_eval_episodes=len(seeds))
    
    if wb:
        wb.finish()


def main():
    for reward in ['true', 'success_rate', 'primal']:
        config = {'reward': reward}
        run_sb3(config)


if __name__ == '__main__':
    main()
