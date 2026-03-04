"""
Camouflage: Advanced Stealth Game
==================================
A stealth-based puzzle game built with Pygame where players navigate
through enemy territory while avoiding detection by changing shape
to blend in with the environment.

Features:
    - Shape-shifting camouflage mechanic
    - Sprint / stamina system
    - Decoy deployment
    - Teleporters
    - Wall obstacles with collision
    - Multiple enemies per level
    - Scoring system (time + efficiency)
"""

import pygame
import math
import asyncio
import traceback
import time as time_module

# --- CONFIGURATION ---
WIDTH, HEIGHT = 800, 600
FPS = 60

# Color Palette
WHITE     = (240, 240, 240)
BLACK     = (20, 20, 20)
RED       = (200, 50, 50)
GREEN     = (50, 200, 50)
BLUE      = (50, 100, 255)
YELLOW    = (255, 200, 0)
ORANGE    = (255, 165, 0)
CYAN      = (0, 255, 255)
GRAY      = (150, 150, 150)
DARK_GRAY = (80, 80, 80)
GOLD      = (255, 215, 0)
LIGHT_GREEN = (144, 238, 144)
DARK_RED  = (139, 0, 0)

# --- CLASSES ---

class Wall:
    """An impassable obstacle that blocks player and enemy movement.

    Walls form the maze-like structure of each level, forcing
    the player to navigate carefully around enemies.

    Attributes:
        rect: Pygame rectangle defining the wall's position and size.
    """

    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, surface):
        """Draw the wall as a dark filled rectangle with a border."""
        pygame.draw.rect(surface, DARK_GRAY, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)


class Player:
    """The player-controlled character that can shift shapes to hide.

    The player can sprint (consuming stamina), deploy decoys to
    distract enemies, and change shape to match hiding spots.

    Attributes:
        pos: Current position as a Vector2.
        shape_type: Current shape ('square' or 'circle').
        has_key: Whether the player has collected the level key.
        stamina: Current sprint energy (0-100).
        decoys_left: Remaining decoy charges.
    """

    def __init__(self, start_pos):
        self.pos = pygame.math.Vector2(start_pos)
        self.rect = pygame.Rect(0, 0, 30, 30)
        self.rect.center = self.pos
        self.shape_type = "square"
        self.base_speed = 4
        self.speed = 4
        self.has_key = False

        # Sprint System
        self.stamina = 100
        self.max_stamina = 100
        self.is_sprinting = False

        # Decoy System
        self.decoys_left = 3

    def move(self, keys, walls=None):
        """Move the player based on pressed keys, respecting wall collisions.

        Args:
            keys: Pygame key state from pygame.key.get_pressed().
            walls: Optional list of Wall objects for collision detection.
        """
        if walls is None:
            walls = []

        vel = pygame.math.Vector2(0, 0)
        if keys[pygame.K_LEFT]:  vel.x = -1
        if keys[pygame.K_RIGHT]: vel.x = 1
        if keys[pygame.K_UP]:    vel.y = -1
        if keys[pygame.K_DOWN]:  vel.y = 1

        # Sprint Logic
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            if self.stamina > 0:
                self.is_sprinting = True
                self.speed = self.base_speed * 1.8
                self.stamina -= 1
            else:
                self.is_sprinting = False
                self.speed = self.base_speed * 0.5  # Tired!
        else:
            self.is_sprinting = False
            self.speed = self.base_speed
            if self.stamina < self.max_stamina:
                self.stamina += 0.5  # Recharge

        if vel.length() > 0:
            vel = vel.normalize() * self.speed

            # Move on X axis, then check collision
            self.pos.x += vel.x
            self.rect.center = self.pos
            for wall in walls:
                if self.rect.colliderect(wall.rect):
                    if vel.x > 0:
                        self.rect.right = wall.rect.left
                    elif vel.x < 0:
                        self.rect.left = wall.rect.right
                    self.pos.x = self.rect.centerx

            # Move on Y axis, then check collision
            self.pos.y += vel.y
            self.rect.center = self.pos
            for wall in walls:
                if self.rect.colliderect(wall.rect):
                    if vel.y > 0:
                        self.rect.bottom = wall.rect.top
                    elif vel.y < 0:
                        self.rect.top = wall.rect.bottom
                    self.pos.y = self.rect.centery

        # Clamp to screen bounds
        self.pos.x = max(20, min(WIDTH - 20, self.pos.x))
        self.pos.y = max(20, min(HEIGHT - 20, self.pos.y))
        self.rect.center = self.pos

    def draw(self, surface):
        """Render the player and their stamina bar."""
        if self.shape_type == "square":
            pygame.draw.rect(surface, BLACK, self.rect)
        elif self.shape_type == "circle":
            center = (int(self.pos.x), int(self.pos.y))
            pygame.draw.circle(surface, BLACK, center, 15)

        # Draw Stamina Bar (Above Player)
        bar_width = 30
        fill = (self.stamina / self.max_stamina) * bar_width
        pygame.draw.rect(surface, GRAY, (self.pos.x - 15, self.pos.y - 25, bar_width, 4))
        color = BLUE if self.stamina > 25 else RED
        pygame.draw.rect(surface, color, (self.pos.x - 15, self.pos.y - 25, fill, 4))

        # Key indicator
        if self.has_key:
            pygame.draw.circle(surface, GOLD, (int(self.pos.x), int(self.pos.y - 32)), 4)


class Decoy:
    """A throwable distraction that lures enemies away from the player.

    Decoys appear as hollow squares and attract nearby enemies for
    a limited duration before disappearing.

    Attributes:
        pos: Position of the decoy.
        life: Remaining frames before the decoy expires.
    """

    def __init__(self, x, y):
        self.pos = pygame.math.Vector2(x, y)
        self.rect = pygame.Rect(0, 0, 30, 30)
        self.rect.center = self.pos
        self.life = 180  # Lasts 3 seconds (60fps * 3)

    def update(self):
        """Decrease remaining lifetime by one frame."""
        self.life -= 1

    def draw(self, surface):
        """Render the decoy as a hollow square with a pulse effect."""
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        # Pulsing "!" indicator
        if self.life % 20 < 15:
            pygame.draw.line(surface, BLACK,
                             (self.pos.x, self.pos.y - 5),
                             (self.pos.x, self.pos.y + 5), 2)


class Teleporter:
    """A portal that transports the player to a linked teleporter.

    Teleporters come in pairs. Entering one instantly moves the
    player to its partner, with a cooldown to prevent oscillation.

    Attributes:
        color: Visual color of this teleporter.
        cooldown: Frames remaining before this portal can be used again.
    """

    def __init__(self, x, y, color, is_exit=False):
        self.rect = pygame.Rect(0, 0, 40, 40)
        self.rect.center = (x, y)
        self.color = color
        self.is_exit = is_exit
        self.cooldown = 0

    def update(self):
        """Decrease cooldown timer."""
        if self.cooldown > 0:
            self.cooldown -= 1

    def draw(self, surface):
        """Draw the teleporter with animated concentric circles."""
        pygame.draw.circle(surface, self.color, self.rect.center, 20, 2)
        inner = 10 + (self.cooldown % 5)
        pygame.draw.circle(surface, self.color, self.rect.center, inner)


class KeyItem:
    """A collectible key required to unlock the level exit.

    The player must pick up the key before the goal zone activates.

    Attributes:
        active: Whether the key is still on the map (not yet collected).
    """

    def __init__(self, x, y):
        self.rect = pygame.Rect(0, 0, 20, 20)
        self.rect.center = (x, y)
        self.active = True

    def draw(self, surface):
        """Draw the key as a rotating diamond shape."""
        if self.active:
            cx, cy = self.rect.center
            p1 = (cx, cy - 10)
            p2 = (cx + 10, cy)
            p3 = (cx, cy + 10)
            p4 = (cx - 10, cy)
            pygame.draw.polygon(surface, BLUE, [p1, p2, p3, p4])
            pygame.draw.polygon(surface, BLACK, [p1, p2, p3, p4], 2)


class HidingSpot:
    """A designated area where the player can change shape to hide.

    When standing on a hiding spot and pressing SPACE, the player
    adopts the spot's shape type, becoming invisible to enemies
    if the shapes match.

    Attributes:
        shape_type: The shape of this spot ('square' or 'circle').
    """

    def __init__(self, x, y, shape_type):
        self.rect = pygame.Rect(0, 0, 40, 40)
        self.rect.center = (x, y)
        self.shape_type = shape_type

    def draw(self, surface):
        """Draw the hiding spot as an outlined shape."""
        if self.shape_type == "square":
            pygame.draw.rect(surface, BLACK, self.rect, 3)
        elif self.shape_type == "circle":
            pygame.draw.circle(surface, BLACK, self.rect.center, 20, 3)


class Enemy:
    """A patrolling guard with a vision cone that detects the player.

    Enemies follow predefined patrol routes. They can be distracted
    by decoys and will chase the player when alerted.

    Attributes:
        points: List of patrol waypoints.
        speed: Current movement speed.
        vision_length: Range of the vision cone in pixels.
        alerted: Whether the enemy is actively chasing the player.
        distracted: Whether the enemy is chasing a decoy.
    """

    def __init__(self, patrol_points, speed=2.5):
        self.points = patrol_points
        self.current_point_index = 0
        self.pos = pygame.math.Vector2(self.points[0])
        self.base_speed = speed
        self.speed = speed
        self.vision_length = 160
        self.vision_angle = 0
        self.alerted = False
        self.distracted = False
        self.target_decoy = None

    def update(self, player_pos, active_decoys):
        """Update enemy position, chasing decoys/player or patrolling.

        Args:
            player_pos: Current player position as Vector2.
            active_decoys: List of active Decoy objects on the map.
        """
        # 1. Check for Decoys
        self.distracted = False
        self.target_decoy = None

        for decoy in active_decoys:
            dist = self.pos.distance_to(decoy.pos)
            if dist < 200:
                self.distracted = True
                self.target_decoy = decoy.pos
                break

        # 2. Determine Target
        if self.distracted:
            target = self.target_decoy
            self.speed = self.base_speed * 1.5
        elif self.alerted:
            target = player_pos
            self.speed = self.base_speed * 1.5
        else:
            target = pygame.math.Vector2(self.points[self.current_point_index])
            self.speed = self.base_speed

        # 3. Move
        direction = target - self.pos
        dist = direction.length()

        if not self.alerted and not self.distracted and dist < 5:
            self.current_point_index = (self.current_point_index + 1) % len(self.points)
        elif dist > 1:
            direction = direction.normalize()
            self.pos += direction * self.speed
            self.vision_angle = math.degrees(math.atan2(-direction.y, direction.x))

    def can_see(self, player):
        """Check if the player is within this enemy's vision cone.

        Args:
            player: The Player object to check visibility for.

        Returns:
            True if the player is visible, False otherwise.
        """
        if self.distracted:
            return False

        vec_to_player = player.pos - self.pos
        dist = vec_to_player.length()
        if dist < self.vision_length:
            angle_to_player = math.degrees(math.atan2(-vec_to_player.y, vec_to_player.x))
            angle_diff = (angle_to_player - self.vision_angle + 180) % 360 - 180
            if abs(angle_diff) < 35:
                return True
        return False

    def draw(self, surface):
        """Render the enemy triangle and its vision cone lines."""
        color = YELLOW if (self.alerted or self.distracted) else RED
        angle_rad = math.radians(self.vision_angle)
        left_angle = math.radians(self.vision_angle + 35)
        right_angle = math.radians(self.vision_angle - 35)

        # Vision cone (semi-transparent fill)
        p1 = (int(self.pos.x), int(self.pos.y))
        p2 = (int(self.pos.x + math.cos(left_angle) * self.vision_length),
              int(self.pos.y - math.sin(left_angle) * self.vision_length))
        p3 = (int(self.pos.x + math.cos(right_angle) * self.vision_length),
              int(self.pos.y - math.sin(right_angle) * self.vision_length))

        # Draw filled vision cone (semi-transparent)
        cone_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        cone_color = (255, 200, 0, 40) if self.alerted else (200, 50, 50, 30)
        pygame.draw.polygon(cone_surface, cone_color, [p1, p2, p3])
        surface.blit(cone_surface, (0, 0))

        # Vision border lines
        pygame.draw.line(surface, color, p1, p2, 2)
        pygame.draw.line(surface, color, p1, p3, 2)
        pygame.draw.line(surface, color, p2, p3, 1)

        # Body triangle
        tip = (int(self.pos.x + math.cos(angle_rad) * 20),
               int(self.pos.y - math.sin(angle_rad) * 20))
        left = (int(self.pos.x + math.cos(angle_rad + 2.5) * 15),
                int(self.pos.y - math.sin(angle_rad + 2.5) * 15))
        right = (int(self.pos.x + math.cos(angle_rad - 2.5) * 15),
                 int(self.pos.y - math.sin(angle_rad - 2.5) * 15))

        pygame.draw.polygon(surface, RED, [tip, left, right])
        pygame.draw.polygon(surface, BLACK, [tip, left, right], 1)

        # "!" if distracted or alerted
        if self.distracted:
            pygame.draw.circle(surface, ORANGE, (int(self.pos.x), int(self.pos.y - 30)), 6)
            # Small "?" text
        elif self.alerted:
            pygame.draw.circle(surface, RED, (int(self.pos.x), int(self.pos.y - 30)), 6)


class ScoreTracker:
    """Tracks the player's performance across a full game run.

    Calculates a final score based on time taken, decoys used,
    and number of times caught.

    Attributes:
        level_times: List of seconds taken per level.
        total_decoys_used: Total decoys deployed across all levels.
        total_deaths: Number of times caught by enemies.
    """

    def __init__(self):
        self.level_start_time = 0
        self.level_times = []
        self.total_decoys_used = 0
        self.total_deaths = 0
        self.decoys_at_level_start = 3

    def start_level(self, decoy_count):
        """Record the start time of a new level."""
        self.level_start_time = time_module.time()
        self.decoys_at_level_start = decoy_count

    def finish_level(self, decoys_remaining):
        """Record level completion and calculate decoys used."""
        elapsed = time_module.time() - self.level_start_time
        self.level_times.append(elapsed)
        self.total_decoys_used += (self.decoys_at_level_start - decoys_remaining)

    def record_death(self):
        """Increment the death counter."""
        self.total_deaths += 1

    def get_total_time(self):
        """Get total time across all completed levels."""
        return sum(self.level_times)

    def get_final_score(self):
        """Calculate the final score (higher is better).

        Formula: base 10000 - (time penalty) - (decoy penalty) - (death penalty)
        Minimum score is 0.

        Returns:
            Integer score value.
        """
        base = 10000
        time_penalty = int(self.get_total_time() * 15)
        decoy_penalty = self.total_decoys_used * 200
        death_penalty = self.total_deaths * 1500
        return max(0, base - time_penalty - decoy_penalty - death_penalty)

    def get_rank(self):
        """Return a letter rank based on the final score."""
        score = self.get_final_score()
        if score >= 8000:
            return "S"
        elif score >= 6000:
            return "A"
        elif score >= 4000:
            return "B"
        elif score >= 2000:
            return "C"
        else:
            return "D"

    def reset(self):
        """Reset all tracking data for a new game."""
        self.level_times = []
        self.total_decoys_used = 0
        self.total_deaths = 0
        self.decoys_at_level_start = 3
        self.level_start_time = 0


# --- LEVEL DATA ---
# Each level now supports multiple enemies via "enemies" key (list of dicts)
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
]


# --- MAIN GAME ---
async def main():
    """Main game loop handling state transitions, input, updates, and rendering."""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Camouflage: Advanced Stealth Game")
    clock = pygame.time.Clock()

    # Fonts
    font_big = pygame.font.SysFont("Arial", 48, bold=True)
    font_med = pygame.font.SysFont("Arial", 32, bold=True)
    font_small = pygame.font.SysFont("Arial", 24)
    font_tiny = pygame.font.SysFont("Arial", 18)

    # Score Tracker
    score_tracker = ScoreTracker()

    state = "MENU"
    current_level_idx = 0
    active_decoys = []
    level_timer = 0  # Frames elapsed in current level

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

    player, enemies, key_item, spots, teleporters, goal_rect, walls = load_level(0)

    running = True

    try:
        while running:
            clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if state == "MENU":
                        if event.key == pygame.K_SPACE:
                            state = "PLAYING"
                            current_level_idx = 0
                            active_decoys = []
                            level_timer = 0
                            score_tracker.reset()
                            player, enemies, key_item, spots, teleporters, goal_rect, walls = load_level(current_level_idx)
                            score_tracker.start_level(player.decoys_left)

                    elif state == "PLAYING":
                        if event.key == pygame.K_SPACE:
                            for spot in spots:
                                if player.rect.colliderect(spot.rect):
                                    player.shape_type = spot.shape_type

                        # DECOY LOGIC (Press Z)
                        if event.key == pygame.K_z:
                            if player.decoys_left > 0:
                                player.decoys_left -= 1
                                active_decoys.append(Decoy(player.pos.x, player.pos.y))

                    elif state in ["GAME_OVER", "LEVEL_DONE"]:
                        if event.key == pygame.K_SPACE:
                            active_decoys = []
                            level_timer = 0
                            if state == "LEVEL_DONE":
                                current_level_idx += 1
                                if current_level_idx >= len(LEVELS):
                                    state = "ALL_COMPLETE"
                                else:
                                    player, enemies, key_item, spots, teleporters, goal_rect, walls = load_level(current_level_idx)
                                    score_tracker.start_level(player.decoys_left)
                                    state = "PLAYING"
                            else:
                                score_tracker.record_death()
                                player, enemies, key_item, spots, teleporters, goal_rect, walls = load_level(current_level_idx)
                                score_tracker.start_level(player.decoys_left)
                                state = "PLAYING"

                    elif state == "ALL_COMPLETE":
                        if event.key == pygame.K_SPACE:
                            state = "MENU"

            # --- UPDATES ---
            if state == "PLAYING":
                keys = pygame.key.get_pressed()
                player.move(keys, walls)
                level_timer += 1

                # Decoy Update
                for d in active_decoys[:]:
                    d.update()
                    if d.life <= 0:
                        active_decoys.remove(d)

                # Teleporter Logic
                for t_pair in teleporters:
                    t1, t2 = t_pair
                    t1.update()
                    t2.update()

                    if player.rect.colliderect(t1.rect) and t1.cooldown == 0:
                        player.pos = pygame.math.Vector2(t2.rect.center)
                        t2.cooldown = 60
                    elif player.rect.colliderect(t2.rect) and t2.cooldown == 0:
                        player.pos = pygame.math.Vector2(t1.rect.center)
                        t1.cooldown = 60

                if key_item.active and player.rect.colliderect(key_item.rect):
                    key_item.active = False
                    player.has_key = True

                if player.rect.colliderect(goal_rect):
                    if player.has_key:
                        score_tracker.finish_level(player.decoys_left)
                        state = "LEVEL_DONE"

                # Check ALL enemies for vision & collision
                is_moving = any([keys[pygame.K_LEFT], keys[pygame.K_RIGHT],
                                 keys[pygame.K_UP], keys[pygame.K_DOWN]])
                safe_spot = False
                for spot in spots:
                    dist = player.pos.distance_to(pygame.math.Vector2(spot.rect.center))
                    if dist < 20 and player.shape_type == spot.shape_type:
                        safe_spot = True

                for enemy in enemies:
                    seen = enemy.can_see(player)
                    if seen and (is_moving or not safe_spot):
                        enemy.alerted = True
                    else:
                        enemy.alerted = False

                    enemy.update(player.pos, active_decoys)

                    # Death Check per enemy
                    dist_to_enemy = player.pos.distance_to(enemy.pos)
                    if dist_to_enemy < 25:
                        state = "GAME_OVER"

            # --- DRAWING ---
            screen.fill(WHITE)

            if state == "MENU":
                # Title
                txt_title = font_big.render("CAMOUFLAGE", True, BLACK)
                screen.blit(txt_title, (WIDTH // 2 - txt_title.get_width() // 2, 140))

                # Subtitle
                txt_sub = font_small.render("Advanced Stealth Game", True, RED)
                screen.blit(txt_sub, (WIDTH // 2 - txt_sub.get_width() // 2, 200))

                # Decorative line
                pygame.draw.line(screen, GRAY, (200, 240), (600, 240), 2)

                # Level count
                txt_levels = font_small.render(f"{len(LEVELS)} Levels | Score System | Wall Obstacles", True, DARK_GRAY)
                screen.blit(txt_levels, (WIDTH // 2 - txt_levels.get_width() // 2, 260))

                # Controls section
                controls_header = font_med.render("Controls", True, BLACK)
                screen.blit(controls_header, (WIDTH // 2 - controls_header.get_width() // 2, 320))

                control_lines = [
                    "Arrow Keys = Move",
                    "SHIFT = Sprint  |  SPACE = Change Shape",
                    "Z = Deploy Decoy  |  Portals = Teleport",
                ]
                for i, line in enumerate(control_lines):
                    txt = font_tiny.render(line, True, DARK_GRAY)
                    screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, 365 + i * 28))

                # Start prompt (blinking)
                if (pygame.time.get_ticks() // 500) % 2 == 0:
                    txt_start = font_med.render("Press SPACE to Start", True, BLUE)
                    screen.blit(txt_start, (WIDTH // 2 - txt_start.get_width() // 2, 490))

            elif state == "PLAYING" or state == "GAME_OVER":
                # Draw walls first (background layer)
                for wall in walls:
                    wall.draw(screen)

                # Goal zone
                goal_color = GREEN if player.has_key else RED
                pygame.draw.rect(screen, goal_color, goal_rect)
                pygame.draw.rect(screen, BLACK, goal_rect, 2)

                # Exit label
                if player.has_key:
                    exit_txt = font_tiny.render("EXIT", True, BLACK)
                    screen.blit(exit_txt, (goal_rect.centerx - exit_txt.get_width() // 2,
                                           goal_rect.centery - exit_txt.get_height() // 2))

                for spot in spots:
                    spot.draw(screen)

                for t_pair in teleporters:
                    t_pair[0].draw(screen)
                    t_pair[1].draw(screen)

                key_item.draw(screen)

                for d in active_decoys:
                    d.draw(screen)

                for enemy in enemies:
                    enemy.draw(screen)

                if state == "PLAYING":
                    player.draw(screen)

                if state == "GAME_OVER":
                    # Darken overlay
                    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 100))
                    screen.blit(overlay, (0, 0))

                    txt_caught = font_big.render("CAUGHT!", True, RED)
                    screen.blit(txt_caught, (WIDTH // 2 - txt_caught.get_width() // 2, HEIGHT // 2 - 60))
                    txt_restart = font_small.render("Press SPACE to Retry", True, WHITE)
                    screen.blit(txt_restart, (WIDTH // 2 - txt_restart.get_width() // 2, HEIGHT // 2 + 10))

                # --- HUD ---
                # Level name
                level_data = LEVELS[current_level_idx]
                level_name = level_data.get("name", f"Level {level_data['id']}")
                hud_level = font_tiny.render(f"Level {level_data['id']}: {level_name}", True, BLACK)
                screen.blit(hud_level, (10, 8))

                # Timer
                elapsed_sec = level_timer // FPS
                elapsed_min = elapsed_sec // 60
                elapsed_sec = elapsed_sec % 60
                timer_txt = font_tiny.render(f"Time: {elapsed_min:02d}:{elapsed_sec:02d}", True, BLACK)
                screen.blit(timer_txt, (WIDTH - timer_txt.get_width() - 10, 8))

                # Decoys
                decoy_txt = font_tiny.render(f"Decoys: {player.decoys_left}", True, BLACK)
                screen.blit(decoy_txt, (10, 574))

                # Key status
                key_status = "KEY" if player.has_key else "Find Key"
                key_color = GOLD if player.has_key else GRAY
                key_txt = font_tiny.render(key_status, True, key_color)
                screen.blit(key_txt, (WIDTH - key_txt.get_width() - 10, 574))

                # Deaths this run
                if score_tracker.total_deaths > 0:
                    death_txt = font_tiny.render(f"Deaths: {score_tracker.total_deaths}", True, RED)
                    screen.blit(death_txt, (WIDTH // 2 - death_txt.get_width() // 2, 574))

            elif state == "LEVEL_DONE":
                # Level complete screen with score preview
                screen.fill(WHITE)

                txt_escaped = font_big.render("LEVEL CLEAR!", True, GREEN)
                screen.blit(txt_escaped, (WIDTH // 2 - txt_escaped.get_width() // 2, 120))

                level_data = LEVELS[current_level_idx]
                level_name = level_data.get("name", f"Level {level_data['id']}")
                name_txt = font_small.render(level_name, True, DARK_GRAY)
                screen.blit(name_txt, (WIDTH // 2 - name_txt.get_width() // 2, 185))

                pygame.draw.line(screen, GRAY, (200, 220), (600, 220), 2)

                # Level stats
                if score_tracker.level_times:
                    last_time = score_tracker.level_times[-1]
                    time_txt = font_small.render(f"Level Time: {last_time:.1f}s", True, BLACK)
                    screen.blit(time_txt, (WIDTH // 2 - time_txt.get_width() // 2, 250))

                progress = f"Level {current_level_idx + 1} / {len(LEVELS)} Complete"
                prog_txt = font_small.render(progress, True, BLUE)
                screen.blit(prog_txt, (WIDTH // 2 - prog_txt.get_width() // 2, 300))

                if current_level_idx + 1 < len(LEVELS):
                    next_txt = font_small.render("Press SPACE for Next Level", True, BLACK)
                else:
                    next_txt = font_small.render("Press SPACE to See Final Score!", True, GOLD)
                screen.blit(next_txt, (WIDTH // 2 - next_txt.get_width() // 2, 400))

            elif state == "ALL_COMPLETE":
                # Final victory screen with scoring
                screen.fill(BLACK)

                # Title
                txt_victory = font_big.render("MISSION COMPLETE", True, GOLD)
                screen.blit(txt_victory, (WIDTH // 2 - txt_victory.get_width() // 2, 60))

                pygame.draw.line(screen, GRAY, (150, 120), (650, 120), 2)

                # Stats
                total_time = score_tracker.get_total_time()
                final_score = score_tracker.get_final_score()
                rank = score_tracker.get_rank()

                stats = [
                    (f"Total Time: {total_time:.1f}s", WHITE),
                    (f"Decoys Used: {score_tracker.total_decoys_used}", WHITE),
                    (f"Times Caught: {score_tracker.total_deaths}", RED if score_tracker.total_deaths > 0 else WHITE),
                    (f"Levels Cleared: {len(LEVELS)}", GREEN),
                ]

                for i, (text, color) in enumerate(stats):
                    txt = font_small.render(text, True, color)
                    screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, 160 + i * 40))

                # Score
                pygame.draw.line(screen, GRAY, (200, 330), (600, 330), 2)

                score_txt = font_big.render(f"Score: {final_score}", True, GOLD)
                screen.blit(score_txt, (WIDTH // 2 - score_txt.get_width() // 2, 350))

                # Rank
                rank_colors = {"S": GOLD, "A": GREEN, "B": BLUE, "C": ORANGE, "D": RED}
                rank_color = rank_colors.get(rank, WHITE)
                rank_txt = font_big.render(f"Rank: {rank}", True, rank_color)
                screen.blit(rank_txt, (WIDTH // 2 - rank_txt.get_width() // 2, 420))

                # Restart prompt
                restart_txt = font_small.render("Press SPACE to Return to Menu", True, GRAY)
                screen.blit(restart_txt, (WIDTH // 2 - restart_txt.get_width() // 2, 530))

            pygame.display.flip()
            await asyncio.sleep(0)

    except Exception as e:
        print(f"CRASH CAUGHT: {e}")
        traceback.print_exc()
        screen.fill(BLACK)
        err_txt = font_small.render("ERROR!", True, RED)
        err_msg = font_small.render(str(e)[:60], True, WHITE)
        screen.blit(err_txt, (10, 10))
        screen.blit(err_msg, (10, 50))
        pygame.display.flip()
        while True:
            await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())