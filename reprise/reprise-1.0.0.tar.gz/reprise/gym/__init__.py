from gym.envs.registration import register

register(
    id='rocketball-v0',
    entry_point='reprise.gym.rocketball:RocketballEnv',
)
