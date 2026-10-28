import gymnasium as gym
from gymnasium import spaces
import pygame
import numpy as np

class HideAndSeekEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 10} 

    def __init__(self, grid_size=10, num_blocks=3, prep_phase_steps=50, render_mode=None):
        super().__init__()
        
        # Environment parameters
        self.grid_size = grid_size
        self.num_blocks = num_blocks
        self.prep_phase_steps = prep_phase_steps
        self.render_mode = render_mode
        
        
        self.window_size = 500
        self.window = None
        self.clock = None
        
        # Actions: 0:Up, 1:Down, 2:Left, 3:Right, 4:Grab, 5:Drop, 6:Lock, 7:Unlock
        self.action_space = spaces.Discrete(8)
        
        # State tracking variables
        self.current_step = 0
        self.phase = 0 # 0 = Prep, 1 = Chase
        self.hider_pos = np.zeros(2, dtype=int)
        self.seeker_pos = np.zeros(2, dtype=int)
        
        # Blocks need to track: [X, Y, is_grabbed (0/1), is_locked (0/1)]
        self.blocks = np.zeros((self.num_blocks, 4), dtype=int)
        
        # Observation Space Definition
        self.observation_space = spaces.Dict({
            "hider": spaces.MultiDiscrete([self.grid_size, self.grid_size]),
            "seeker": spaces.MultiDiscrete([self.grid_size, self.grid_size]),
            "phase": spaces.Discrete(2),
            # Each block has [X, Y, grabbed, locked]
            "blocks": spaces.MultiDiscrete([
                [self.grid_size, self.grid_size, 2, 2] for _ in range(self.num_blocks)
            ])
        })


    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = 0
        self.phase = 0

        # Spawns players at random.
        self.hider_pos = self.np_random.integers(0, self.grid_size, size=2)
        self.seeker_pos = self.np_random.integers(0, self.grid_size, size=2)

        # Prevents players from spawning on top of each other.
        while np.array_equal(self.hider_pos, self.seeker_pos):
            self.seeker_pos = self.np_random.integers(0, self.grid_size, size=2)

        # Initialize blocks
        for i in range(self.num_blocks):
            valid_spawn = False
            while not valid_spawn:
                # Prevents blocks from spawning on players.
                block_pos = self.np_random.integers(0, self.grid_size, size=2)
                if not (np.array_equal(block_pos, self.hider_pos) and not np.array_equal(block_pos, self.seeker_pos)):
                    valid_spawn = True
            # [X, Y, grabbed, locked]
            self.blocks[i] = [block_pos[0], block_pos[1], 0, 0]

        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self.render()

        return observation, info
    

    def step(self, action):
        self.current_step += 1
        reward = -0.01 # Base penalty.

        # Hider Movement.
        if action < 4:
            moves = {
                0: np.array([0, -1]),  # Up
                1: np.array([-1, 0]),   # Left
                2: np.array([0, 1]),  # Down
                3: np.array([1, 0])    # Right
            }
            target_pos = self.hider_pos + moves[action]

            if self._is_valid_position(target_pos):
                self.hider_pos = target_pos

                for block in self.blocks:
                    if block[2] == 1: # Grabbed
                        block[0], block[1] = self.hider_pos[0], self.hider_pos[1]

        # Hider Interactions.
            # Grab.
        elif action == 4:
            if not any(b[2] == 1 for b in self.blocks):
                for block in self.blocks:
                    if np.array_equal(self.hider_pos, block[:2]) and block[3] == 0:
                        block[2] = 1
                        break

            # Drop.
        elif action == 5:
            for block in self.blocks:
                if block[2] == 1:
                    block[2] = 0

            # Lock.
        elif action == 6:
            for block in self.blocks:
                if block[2] == 1:
                    block[3] = 1
                    block[2] = 0

            # Unlock.
        elif action == 7:
            for block in self.blocks:
                if block[3] == 1:
                    dist = np.linalg.norm(self.hider_pos - block[:2])
                    if dist <= 1.0:
                        block[3] = 0

        # Phase Management & Seeker Logic
        if self.current_step > self.prep_phase_steps:
            self.phase = 1
            reward += 1.0 # Reward for each step in chase.

            seeker_move = np.zeros(2, dtype=int)
            if self.seeker_pos[0] < self.hider_pos[0]: 
                seeker_move[0] = 1
            elif self.seeker_pos[0] > self.hider_pos[0]: seeker_move[0] = -1
            elif self.seeker_pos[1] < self.hider_pos[1]: seeker_move[1] = 1
            elif self.seeker_pos[1] > self.hider_pos[1]: seeker_move[1] = -1

            seeker_target = self.seeker_pos + seeker_move
            if self._is_valid_position(seeker_target):
                self.seeker_pos = seeker_target

        # Termination & Rewards
        terminated = False
        truncated = False

        if np.array_equal(self.hider_pos, self.seeker_pos) and self.phase == 1:
            terminated = True
            reward -= 10.0 # Penalty for being caught.

        if self.current_step >= 200:
            truncated = True
            reward += 100.0 # Reward for surviving the chase.

        if self.render_mode == "human":
            self.render()

        return self._get_obs(), reward, terminated, truncated, self._get_info()


    def _is_valid_position(self, pos):
        # Helper to check if a position is within bounds and not blocked/occupied.
        if pos[0] < 0 or pos[0] >= self.grid_size or pos[1] < 0 or pos[1] >= self.grid_size:
            return False
        for block in self.blocks:
            if block[3] == 1:
                if np.array_equal(pos, block[:2]):
                    return False

        return True

    
    def render(self):
        

        # Pygame initialization.
        if self.window is None:
            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode((self.window_size, self.window_size))
            pygame.display.set_caption("Justin's Hide and Seek!")
        if self.clock is None:
            self.clock = pygame.time.Clock()
        
        canvas = pygame.Surface((self.window_size, self.window_size))
        canvas.fill((255, 255, 255))  # White background.
        pix_square_size = self.window_size / self.grid_size

        for block in self.blocks:
            x, y, is_grabbed, is_locked = block
            rect = pygame.Rect(
                x * pix_square_size, 
                y * pix_square_size, 
                pix_square_size, 
                pix_square_size
            )
            
            if is_locked == 1:
                # Locked barricade: Dark Gray
                pygame.draw.rect(canvas, (80, 80, 80), rect)
            elif is_grabbed == 1:
                # Grabbed block: Gold/Yellow (Draws slightly smaller to see Hider under it)
                grab_rect = pygame.Rect(
                    x * pix_square_size + 10, 
                    y * pix_square_size + 10, 
                    pix_square_size - 20, 
                    pix_square_size - 20
                )
                pygame.draw.rect(canvas, (255, 215, 0), grab_rect)
            else:
                # Free block: Brown (Wood)
                pygame.draw.rect(canvas, (139, 69, 19), rect)

        # Hider (Blue Circle)
        pygame.draw.circle(
            canvas,
            (0, 0, 255),
            (self.hider_pos + 0.5) * pix_square_size,
            pix_square_size / 3,
        )

        # Seeker (Red Circle)
        pygame.draw.circle(
            canvas,
            (255, 0, 0),
            (self.seeker_pos + 0.5) * pix_square_size,
            pix_square_size / 3,
        )

        # Draw Grid Lines.
        for x in range(self.grid_size + 1):
            pygame.draw.line(
                canvas,
                (200, 200, 200),
                (0, pix_square_size * x),
                (self.window_size, pix_square_size * x),
            )
            pygame.draw.line(
                canvas,
                (200, 200, 200),
                (pix_square_size * x, 0),
                (pix_square_size * x, self.window_size),
            )

        # Apply Phase Visuals (Optional visual feedback for testing).
        if self.phase == 0:
            # Draw a subtle green border during Preparation Phase
            pygame.draw.rect(canvas, (0, 255, 0), canvas.get_rect(), 5)
        else:
            # Draw a subtle red border during Chase Phase
            pygame.draw.rect(canvas, (255, 0, 0), canvas.get_rect(), 5)

        # Render to screen.
        self.window.blit(canvas, canvas.get_rect())
        pygame.event.pump()
        pygame.display.update()
        
        # Lock framerate to the value set in __init__ metadata
        self.clock.tick(self.metadata["render_fps"])
        
    def close(self):
        # Gym standard cleanup function
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()


    def _get_obs(self):
        # Helper to package current state variables into observation format.
        return {
            "hider": self.hider_pos.copy(),
            "seeker": self.seeker_pos.copy(),
            "phase": self.phase,
            "blocks": self.blocks.copy()
        }

    def _get_info(self):
        # Helper to return debugging & metrics.
        return {"current_step": self.current_step}