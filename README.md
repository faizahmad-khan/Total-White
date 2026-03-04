# Camouflage: Advanced Stealth Game

A stealth-based puzzle game built with Pygame where players must navigate through enemy territory while avoiding detection by changing their shape to blend in with the environment.

[![Play on itch.io](https://img.shields.io/badge/Play_on-itch.io-fa5c5c?style=for-the-badge&logo=itch.io&logoColor=white)](https://cypher0101.itch.io/camouflage-stealth)

## Table of Contents
- [Game Overview](#game-overview)
- [Features](#features)
- [How to Play](#how-to-play)
- [Game Mechanics](#game-mechanics)
- [Controls](#controls)
- [Scoring System](#scoring-system)
- [Requirements](#requirements)
- [Installation](#installation)

## Game Overview

In Camouflage, you play as a stealth agent trying to reach the safe zone without being detected by patrolling enemies. The unique twist is that you can change your shape to blend in with designated hiding spots, making you invisible to enemy vision cones when you match the shape of your surroundings.

## Features

- **5 Unique Levels** — Each with a distinct name, layout, and escalating difficulty
- **Wall Obstacles** — Maze-like structures that block movement and force strategic routing
- **Multiple Enemies Per Level** — Up to 3 guards patrolling simultaneously
- **Shape-Shifting Camouflage** — Morph into squares or circles to blend with hiding spots
- **Sprint & Stamina System** — Burst of speed at the cost of energy
- **Decoy Deployment** — Throw distractions to lure enemies away
- **Teleporters** — Portal pairs for cross-map movement
- **Scoring System** — Performance-based score with S/A/B/C/D ranks
- **Semi-Transparent Vision Cones** — See exactly where enemies are looking
- **Web Deployment** — Playable in browser via Pygbag (itch.io)

## Game Screenshots

![Camouflage Gameplay Screenshot 1](images/Screenshot%202026-01-02%20at%2010.59.46%E2%80%AFPM.png)
*Screenshot 1: Player avoiding enemy patrols*

![Camouflage Gameplay Screenshot 2](images/Screenshot%202026-01-02%20at%2010.59.57%E2%80%AFPM.png)
*Screenshot 2: Player changing shape to match environment*

![Camouflage Gameplay Screenshot 3](images/Screenshot%202026-01-02%20at%2011.00.45%E2%80%AFPM.png)
*Screenshot 3: Player navigating to the goal zone*

## How to Play

1. Navigate your character (a black square or circle) using arrow keys
2. Collect the **blue diamond key** to unlock the exit
3. Find hiding spots (outlined squares and circles) scattered around the map
4. Press **SPACE** when on a hiding spot to change your shape to match it
5. Avoid the patrolling enemies and their vision cones
6. Navigate around **walls** — they block your movement!
7. Use **decoys** (Z key) and **sprint** (SHIFT) strategically
8. Reach the **green goal zone** (turns green once you have the key)

## Game Mechanics

- **Shape Matching**: Match the shape of a hiding spot (square or circle) to become invisible to enemies
- **Vision Cones**: Enemies have semi-transparent vision cones — you'll be detected if you're in one while not properly hidden
- **Patrol Patterns**: Enemies follow predetermined patrol paths and look in the direction they're moving
- **Wall Collision**: Walls block both player movement, creating maze-like challenges
- **Detection**: You'll be caught if you're moving in a vision cone OR not in a matching hiding spot
- **Multiple Enemies**: Later levels feature 2-3 enemies with overlapping patrol routes
- **Sprint/Stamina**: Hold SHIFT to sprint (1.8x speed) but stamina drains — when exhausted, you slow to 0.5x
- **Decoys**: Press Z to drop a decoy that distracts nearby enemies for 3 seconds (3 per level)
- **Teleporters**: Step on an orange or cyan portal to warp to its partner

## Controls

| Key | Action |
|-----|--------|
| **Arrow Keys** | Move (up, down, left, right) |
| **SPACE** | Change shape at hiding spots |
| **SHIFT** | Sprint (drains stamina) |
| **Z** | Deploy decoy |
| **ESC / Close** | Quit game |

## Scoring System

Your performance is scored at the end of all 5 levels:

| Factor | Impact |
|--------|--------|
| **Time** | -15 points per second |
| **Decoys Used** | -200 points per decoy |
| **Deaths** | -1500 points per death |

**Ranks**: S (8000+) > A (6000+) > B (4000+) > C (2000+) > D

## Levels

| # | Name | Enemies | Key Feature |
|---|------|---------|-------------|
| 1 | The Courtyard | 1 | Introduction — learn the basics |
| 2 | The Gatehouse | 2 | Teleporters + wall corridors |
| 3 | The Fortress | 2 | Inner/outer patrol routes |
| 4 | The Labyrinth | 3 | Complex maze with narrow gaps |
| 5 | The Gauntlet | 3 | Lane-based obstacle course |

## Requirements

- Python 3.x
- Pygame library

## Installation

1. Make sure you have Python installed on your system
2. Install Pygame:
   ```
   pip install pygame
   ```
3. Run the game:
   ```
   python main.py
   ```

## Project Structure

```
Total-White/
├── main.py           # All game logic, classes, and levels
├── README.md         # This file
├── CONTRIBUTING.md   # Contribution guidelines
├── LICENSE           # License information
├── images/           # Game screenshots
└── build/
    ├── version.txt   # Pygbag version
    └── web/          # Browser-deployable build
```

## Tips

- Always match your shape to the hiding spot **before** an enemy comes into view
- Plan your route through wall gaps to avoid dead ends
- Sprint only when you have a clear path — getting exhausted near an enemy is dangerous
- Save decoys for the hardest sections with overlapping patrol routes
- Teleporters are great for escaping tight situations
- Aim for **S Rank** — complete all levels quickly with zero deaths and no decoys!

## License

This game is created for educational and entertainment purposes.