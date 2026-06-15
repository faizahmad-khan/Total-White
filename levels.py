"""Level definitions and loader utility."""

import pygame

from config import ORANGE, CYAN
from player import Player
from enemy import Enemy
from entities import Wall, Teleporter, KeyItem, HidingSpot


# Each level supports multiple enemies via "enemies" key (list of dicts)
# and walls via "walls" key (list of (x, y, w, h) tuples).
LEVELS = [
    {
        "id": 1,
        "name": "The Courtyard",
        "start": (50, 300),
        "key_pos": (400, 300),
        "goal": (720, 300),
        "enemies": [
            {"path": [(200, 50), (600, 50), (600, 550), (200, 550)], "speed": 2.5},
        ],
        "spots": [
            (200, 150, "circle"), (600, 150, "circle"),
            (200, 450, "square"), (600, 450, "square"),
        ],
        "walls": [
            (380, 100, 15, 150),   # Top center wall
            (380, 350, 15, 150),   # Bottom center wall
        ],
        "teleporters": [],
    },
    {
        "id": 2,
        "name": "The Gatehouse",
        "start": (50, 50),
        "key_pos": (700, 50),
        "goal": (720, 550),
        "enemies": [
            {"path": [(400, 100), (400, 500), (100, 300), (700, 300)], "speed": 3.0},
            {"path": [(600, 50), (600, 550)], "speed": 2.0},
        ],
        "spots": [
            (150, 150, "square"), (650, 150, "circle"),
            (400, 300, "circle"), (650, 450, "square"),
        ],
        "walls": [
            (280, 0, 15, 200),     # Top-left vertical
            (280, 300, 15, 200),   # Bottom-left vertical
            (500, 100, 15, 200),   # Top-right vertical
            (500, 400, 15, 150),   # Bottom-right vertical
        ],
        "teleporters": [((100, 550), (700, 100))],
    },
    {
        "id": 3,
        "name": "The Fortress",
        "start": (400, 550),
        "key_pos": (400, 300),
        "goal": (400, 50),
        "enemies": [
            {"path": [(100, 100), (700, 100), (700, 500), (100, 500)], "speed": 3.5},
            {"path": [(250, 200), (550, 200), (550, 400), (250, 400)], "speed": 3.0},
        ],
        "spots": [
            (200, 200, "square"), (600, 200, "square"),
            (200, 400, "circle"), (600, 400, "circle"),
        ],
        "walls": [
            (150, 140, 200, 12),   # Top-left horizontal
            (450, 140, 200, 12),   # Top-right horizontal
            (150, 450, 200, 12),   # Bottom-left horizontal
            (450, 450, 200, 12),   # Bottom-right horizontal
            (395, 200, 12, 80),    # Center vertical
        ],
        "teleporters": [((50, 300), (750, 300))],
    },
    {
        "id": 4,
        "name": "The Labyrinth",
        "start": (50, 50),
        "key_pos": (750, 550),
        "goal": (400, 300),
        "enemies": [
            {"path": [(200, 150), (600, 150), (600, 450), (200, 450)], "speed": 3.5},
            {"path": [(100, 300), (700, 300)], "speed": 2.5},
            {"path": [(400, 50), (400, 550)], "speed": 4.0},
        ],
        "spots": [
            (100, 150, "circle"), (700, 150, "square"),
            (100, 450, "square"), (700, 450, "circle"),
            (400, 500, "circle"),
        ],
        "walls": [
            (200, 0, 12, 220),     # Left vertical top
            (200, 320, 12, 280),   # Left vertical bottom
            (400, 100, 12, 160),   # Center vertical top
            (400, 380, 12, 120),   # Center vertical bottom
            (600, 0, 12, 220),     # Right vertical top
            (600, 320, 12, 280),   # Right vertical bottom
            (250, 260, 120, 12),   # Left horizontal
            (430, 260, 140, 12),   # Right horizontal
        ],
        "teleporters": [((50, 550), (750, 50))],
    },
    {
        "id": 5,
        "name": "The Gauntlet",
        "start": (50, 300),
        "key_pos": (400, 50),
        "goal": (750, 300),
        "enemies": [
            {"path": [(200, 100), (200, 500)], "speed": 3.0},
            {"path": [(400, 500), (400, 100)], "speed": 3.5},
            {"path": [(600, 100), (600, 500)], "speed": 4.0},
        ],
        "spots": [
            (100, 100, "circle"), (100, 500, "square"),
            (300, 300, "square"), (500, 300, "circle"),
            (700, 100, "circle"), (700, 500, "square"),
        ],
        "walls": [
            (150, 50, 12, 200),    # Lane 1 top
            (150, 350, 12, 200),   # Lane 1 bottom
            (350, 50, 12, 180),    # Lane 2 top
            (350, 370, 12, 180),   # Lane 2 bottom
            (550, 50, 12, 200),    # Lane 3 top
            (550, 350, 12, 200),   # Lane 3 bottom
        ],
        "teleporters": [((50, 100), (750, 500)), ((50, 500), (750, 100))],
    },
    {
        "id": 6,
        "name": "The Citadel",
        "start": (60, 540),
        "key_pos": (400, 300),
        "goal": (740, 60),
        "enemies": [
            {
                "path": [(120, 80), (680, 80), (680, 520), (120, 520)],
                "speed": 4.0,
            },
            {
                "path": [(260, 300), (400, 180), (540, 300), (400, 420)],
                "speed": 4.2,
            },
            {"path": [(80, 460), (720, 460)], "speed": 3.6},
            {"path": [(660, 120), (660, 520)], "speed": 3.8},
        ],
        "spots": [
            (100, 120, "circle"), (100, 520, "square"),
            (300, 120, "square"), (500, 120, "circle"),
            (300, 520, "circle"), (500, 520, "square"),
            (400, 320, "circle"), (700, 300, "square"),
        ],
        "walls": [
            (180, 0, 14, 220),      # Left vertical top
            (180, 320, 14, 280),    # Left vertical bottom
            (380, 80, 14, 220),     # Center vertical top
            (380, 380, 14, 220),    # Center vertical bottom
            (580, 0, 14, 220),      # Right vertical top
            (580, 320, 14, 200),    # Right vertical bottom
            (240, 260, 120, 14),    # Mid-left horizontal
            (420, 260, 120, 14),    # Mid-right horizontal
            (240, 460, 120, 14),    # Lower-left horizontal
            (420, 460, 120, 14),    # Lower-right horizontal
        ],
        "teleporters": [((60, 300), (740, 300)), ((60, 60), (740, 540))],
    },
     {
        "id": 7,
        "name": "The Crossfire",
        # Player starts bottom-left, key is top-right, goal is center
        "start": (50, 550),
        "key_pos": (730, 50),
        "goal": (400, 300),
        "enemies": [
            # Horizontal sweeper, full width — blocks key approach
            {"path": [(50, 100), (750, 100)], "speed": 4.5},
            # Vertical sweeper, full height — cuts off center
            {"path": [(400, 50), (400, 550)], "speed": 4.8},
            # Diagonal-ish: top-left ↔ bottom-right cross
            {"path": [(100, 150), (700, 450)], "speed": 4.2},
            # Diagonal-ish: top-right ↔ bottom-left cross
            {"path": [(700, 150), (100, 450)], "speed": 4.2},
            # Tight center patrol — guards the goal directly
            {"path": [(300, 250), (500, 250), (500, 350), (300, 350)], "speed": 5.0},
        ],
        "spots": [
            (100, 80,  "circle"),
            (700, 80,  "square"),
            (100, 520, "square"),
            (700, 520, "circle"),
            (400, 420, "circle"),
        ],
        "walls": [
            (240, 0,   12, 180),   # Left-center vertical top
            (240, 300, 12, 300),   # Left-center vertical bottom
            (560, 0,   12, 180),   # Right-center vertical top
            (560, 300, 12, 300),   # Right-center vertical bottom
            (260, 280, 290, 12),   # Center horizontal — forces detour
        ],
        "teleporters": [
            ((50, 300), (750, 300)),   # Mid-left ↔ mid-right (risky shortcut)
            ((50, 50),  (750, 550)),   # Corner swap
        ],
    },
     {
        "id": 8,
        "name": "The Gauntlet II",
        # Start top-left, key bottom-center, goal top-right
        "start": (50, 50),
        "key_pos": (400, 530),
        "goal": (740, 50),
        "enemies": [
            # Fast horizontal at mid-height — splits arena
            {"path": [(50, 300), (750, 300)], "speed": 5.0},
            # Vertical left lane
            {"path": [(150, 50), (150, 550)], "speed": 4.5},
            # Vertical right lane, opposite phase (starts bottom)
            {"path": [(650, 550), (650, 50)], "speed": 4.5},
            # Box patrol around the key
            {"path": [(300, 430), (500, 430), (500, 570), (300, 570)], "speed": 4.8},
            # Diagonal harasser through the center
            {"path": [(200, 100), (600, 500), (200, 500), (600, 100)], "speed": 4.0},
        ],
        "spots": [
            (80,  150, "circle"),
            (720, 150, "square"),
            (80,  450, "square"),
            (720, 450, "circle"),
            (400, 200, "circle"),
        ],
        "walls": [
            (200, 0,   12, 240),   # Left vertical top
            (200, 360, 12, 240),   # Left vertical bottom
            (600, 0,   12, 240),   # Right vertical top
            (600, 360, 12, 240),   # Right vertical bottom
            (212, 260, 176, 12),   # Mid-left horizontal
            (420, 260, 180, 12),   # Mid-right horizontal
            (370, 390, 12, 120),   # Key cage left wall
            (430, 390, 12, 120),   # Key cage right wall
        ],
        "teleporters": [
            ((50, 550),  (750, 50)),   # Bottom-left ↔ top-right shortcut
            ((400, 50),  (400, 300)),  # Top-center drops into danger zone
        ],
    },
]


def load_level(idx):
    """Load all entities for the given level index.

    Args:
        idx: Index into the LEVELS list.

    Returns:
        Tuple of (player, enemies_list, key_item, spots, teleporters, goal_rect, walls).
    """
    data = LEVELS[idx]
    p = Player(data["start"])

    # Multiple enemies
    e_list = []
    for e_data in data["enemies"]:
        e_list.append(Enemy(e_data["path"], speed=e_data["speed"]))

    k = KeyItem(data["key_pos"][0], data["key_pos"][1])

    s_list = []
    for s_data in data["spots"]:
        s_list.append(HidingSpot(s_data[0], s_data[1], s_data[2]))

    t_list = []
    if "teleporters" in data:
        for pair in data["teleporters"]:
            t1 = Teleporter(pair[0][0], pair[0][1], ORANGE)
            t2 = Teleporter(pair[1][0], pair[1][1], CYAN)
            t_list.append((t1, t2))

    # Walls
    w_list = []
    if "walls" in data:
        for w_data in data["walls"]:
            w_list.append(Wall(w_data[0], w_data[1], w_data[2], w_data[3]))

    g_rect = pygame.Rect(0, 0, 60, 60)
    g_rect.center = data["goal"]
    return p, e_list, k, s_list, t_list, g_rect, w_list
