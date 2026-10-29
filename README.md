# Emergent Defensive Strategies in Multi-Agent Hide & Seek

**Author:** Justin Wiseman  
**Course:** ECE 414 — Reinforcement Learning (Milestone 2: Environment Setup)

## Overview
This repository implements a custom 2D Gymnasium environment (`HideAndSeek-v0`) designed to explore multi-agent reinforcement learning, sparse rewards, and dynamic obstacle manipulation in a $10 \times 10$ grid-world. 

Each episode is divided into two distinct phases:
1. **Preparation Phase (Steps 0–49):** The Seeker agent is frozen in place. The Hider agent can navigate the grid, grab movable blocks, carry them, and lock them into place to build impassable defensive barricades.
2. **Chase Phase (Steps 50–200):** The Seeker wakes up and actively pursues the Hider using greedy Manhattan navigation while respecting locked block collisions.

To prevent unnecessary waiting once a fortress is complete, the environment runs a Breadth-First Search (BFS) reachability check (`_has_path_to_hider()`) on each step and immediately awards a Hider victory if all valid paths between the Seeker and Hider are blocked.

---

## Project Structure
```text
Hide-N-Seek/
├── envs/
│   ├── __init__.py          # Registers the 'HideAndSeek-v0' environment with Gymnasium
│   └── hidenseek_env.py     # Core environment logic (step, reset, render, collision, BFS)
├── scripts/
│   └── manual_control.py    # Interactive Pygame keyboard script for manual testing
├── requirements.txt         # Required Python packages
└── README.md                # Installation and execution documentation
```

---

## Prerequisites & Installation

### 1. Python Version
Ensure **Python 3.10+** is installed on your system (compatible up to Python 3.14 using `pygame-ce`).

### 2. Install Dependencies
Open a terminal in the root `Hide-N-Seek` directory and install the required packages via `requirements.txt`:

```bash
pip install -r requirements.txt
```

Alternatively, you can install the dependencies manually:

```bash
pip install gymnasium numpy pygame-ce
```
*(Note: `pygame-ce` is the drop-in Community Edition fork of Pygame used to support newer Python versions without C++ build issues. If you are using Python 3.11 or 3.12 with standard `pygame` already installed, it will work without changes.)*

---

## Execution Instructions

To launch the Pygame window and manually test the environment mechanics (movement, block grabbing/locking, phase transitions, and BFS barricade detection), run the manual control script from the project root directory:

**Windows (PowerShell / Command Prompt):**
```powershell
python scripts\manual_control.py
```

**macOS / Linux:**
```bash
python scripts/manual_control.py
```

---

## Keyboard Controls

When the Pygame window is active, use the following keys to control the Hider agent:

| Key | Action ID | Action Description |
| :--- | :---: | :--- |
| **W** | `0` | Move Up |
| **S** | `1` | Move Down |
| **A** | `2` | Move Left |
| **D** | `3` | Move Right |
| **G** | `4` | **Grab Block** (attaches an unlocked brown block on your current or adjacent tile) |
| **H** | `5` | **Drop Block** (releases the currently held block onto your current tile) |
| **L** | `6` | **Lock Block** (locks a held or adjacent block into an impassable dark gray obstacle) |
| **U** | `7` | **Unlock Block** (unlocks an adjacent dark gray block back into a movable brown block) |

---

## Environment Visual Guide & Mechanics

### Visual Elements
* **Green Window Border:** Indicates the **Preparation Phase** (Seeker is immobilized).
* **Red Window Border:** Indicates the **Chase Phase** (Seeker actively hunts the Hider).
* **Blue Circle:** Hider Agent (Player / RL Agent).
* **Red Circle:** Seeker Agent (Adversary).
* **Brown Square:** Unlocked, movable block.
* **Yellow Square:** Block currently grabbed and carried by the Hider.
* **Dark Gray Square:** Locked block (acts as an impassable wall for both agents).

### Episode Termination & Reward Structure
The environment automatically resets when an episode ends under any of the following conditions:
* **Barricade Victory (`terminated = True`):** The Hider locks blocks such that the BFS check confirms the Seeker has no valid path to reach the Hider. Awards `+100.0` plus the remaining survival step points.
* **Time-Out Survival (`truncated = True`):** The Hider survives all `200` steps without being caught. Awards `+100.0` survival bonus (in addition to `+1.0` per step survived during the Chase phase).
* **Caught by Seeker (`terminated = True`):** The Seeker moves onto the Hider's tile during the Chase phase. Applies a `-10.0` penalty.
* **Step Penalty:** A `-0.01` penalty is applied each step during the Preparation Phase to encourage efficient barricade construction.