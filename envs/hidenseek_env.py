import gymnasium as gym
from gymnasium import spaces
import numpy as np

class HideAndSeekEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4} 

    def __init__(self, render_mode=None):
        super().__init__()
        self.render_mode = render_mode

        self.action_space = spaces.Discrete(8)

        #To do: Define observation space. Should track hider, seeker, phase, and block states.

        self.current_step = 0
        self.phase = 0 # 0 is preparation phase, 1 is the chase phase

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = 0
        self.phase = 0

        # To do: Reset Hider, Seeker, and Block coordinates to start positions
        # To do: Reset all block statuses (unlocked, ungrabbed)

        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self.render()

        return observation, info

    def step(self, action):
        self.current_step += 1

        # To do: Update hider position or grab/lock based on action
        # To do: check if current step is greater than prep phase limit to trigger phase change
        # To do: If in chase phase, move seeker one step towards hider.
        # To do: Calculate sparse rewards
        # To do: Check termination (Caught or max steps reached)

        reward = 0.0
        terminated = False
        truncated = False

        if self.render_mode == "human":
            self.render()

        return self._get_obs(), reward, terminated, truncated, self._get_info()

    def render(self):
        if self.render_mode == "human":
            # Pygame drawing logic
            pass

    def _get_obs(self):
        # helper to package current state variables into observation format
        return {}

    def _get_info(self):
        # helper to return debugging info
        return {}