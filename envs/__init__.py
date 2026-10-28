from gymnasium.envs.registration import register
from .hidenseek_env import HideAndSeekEnv

register(
    id='HideAndSeek-v0',
    entry_point='envs.hidenseek_env:HideAndSeekEnv',
    max_episode_steps=200,
)