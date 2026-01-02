# Camouflage: Advanced Stealth Game

A stealth-based puzzle game built with Pygame where players must navigate through enemy territory while avoiding detection by changing their shape to blend in with the environment.

# Camouflage: Stealth Game



[![Play on itch.io](https://img.shields.io/badge/Play_on-itch.io-fa5c5c?style=for-the-badge&logo=itch.io&logoColor=white)](https://cypher0101.itch.io/camouflage-stealth)



A stealth puzzle game built with Python. Avoid the guards, shift shapes, and escape!

## Table of Contents
- [Game Overview](#game-overview)
- [How to Play](#how-to-play)
- [Game Mechanics](#game-mechanics)
- [Controls](#controls)
- [Requirements](#requirements)
- [Installation](#installation)

## Game Overview

In Camouflage, you play as a stealth agent trying to reach the safe zone without being detected by patrolling enemies. The unique twist is that you can change your shape to blend in with designated hiding spots, making you invisible to enemy vision cones when you match the shape of your surroundings.

## Game Screenshots

Here are screenshots showing what you'll play in Camouflage:

![Camouflage Gameplay Screenshot 1](images/Screenshot%202026-01-02%20at%2010.59.46%E2%80%AFPM.png)
*Screenshot 1: Player avoiding enemy patrols*

![Camouflage Gameplay Screenshot 2](images/Screenshot%202026-01-02%20at%2010.59.57%E2%80%AFPM.png)
*Screenshot 2: Player changing shape to match environment*

![Camouflage Gameplay Screenshot 3](images/Screenshot%202026-01-02%20at%2011.00.45%E2%80%AFPM.png)
*Screenshot 3: Player navigating to the goal zone*

## How to Play

1. Navigate your character (a black square or circle) using arrow keys
2. Find hiding spots (black outlined squares and circles) scattered around the map
3. Press the SPACE key when on a hiding spot to change your shape to match it
4. Stay hidden when enemies are looking in your direction
5. Reach the green goal zone without being detected to win
6. Avoid getting caught by the red enemy patrols with vision cones

## Game Mechanics

- **Shape Matching**: You must match the shape of a hiding spot (square or circle) to become invisible to enemies
- **Vision Cones**: Enemies have limited fields of vision (shown as red transparent cones) - you'll be detected if you're in an enemy's vision cone while not properly hidden
- **Patrol Patterns**: Enemies follow predetermined patrol paths and look in the direction they're moving
- **Detection**: You'll be caught if you're moving while in an enemy's vision cone OR if you're not in a matching hiding spot when an enemy sees you

## Controls

- **Arrow Keys**: Move your character (up, down, left, right)
- **Space Bar**: Change your shape to match the current hiding spot you're standing on
- **Close Window**: Quit the game

## Requirements

- Python 3.x
- Pygame library

## Installation

1. Make sure you have Python installed on your system
2. Install Pygame by running:
   ```
   pip install pygame
   ```
3. Run the game:
   ```
   python camouflage.py
   ```

## Game Elements

- **Player**: Black square or circle that you control
- **Hiding Spots**: Black outlined squares and circles where you can change your shape
- **Enemy**: Red triangular shape that patrols the area
- **Vision Cone**: Red transparent area showing what the enemy can see
- **Goal Zone**: Green rectangle - reach this to win the game

## Tips

- Always match your shape to the hiding spot before an enemy comes into view
- Plan your route carefully to avoid being caught between patrol patterns
- Use hiding spots strategically to break line of sight with enemies
- The game ends if you're detected by an enemy while not properly hidden

## License

This game is created for educational and entertainment purposes.