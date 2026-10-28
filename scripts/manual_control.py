import gymnasium as gym
import pygame
import sys
import os

pygame.init() 
os.environ['SDL_VIDEO_WINDOW_POS'] = "100,100"

# Adds parent directory to path so import envs works
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import envs

print("1. Making environment...")
env = gym.make("HideAndSeek-v0", render_mode="human")

print("2. Resetting environment...")
observation, info = env.reset()

print("3. Forcing initial render...")
env.render()

action_map = {
    pygame.K_w: 0,  # Up
    pygame.K_a: 1,  # Left 
    pygame.K_s: 2,  # Down 
    pygame.K_d: 3,  # Right
    pygame.K_g: 4,  # Grab Block
    pygame.K_h: 5,  # Drop Block 
    pygame.K_l: 6,  # Lock Block
    pygame.K_u: 7   # Unlock Block
}

print("4. Starting game loop...")
running = True
clock = pygame.time.Clock()

while running: 
    
    # ADD THIS LINE: Forces the game window to draw continuously 
    env.render() 
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key in action_map:
                action = action_map[event.key]
                observation, reward, terminated, truncated, info = env.step(action)
                if terminated or truncated:
                    print(f"Episode Ended! Reward: {reward}")
                    observation, info = env.reset()

env.close()
pygame.quit()