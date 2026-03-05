"""Small game entities: Wall, Decoy, Teleporter, KeyItem, HidingSpot."""

import pygame

from config import BLACK, BLUE, DARK_GRAY, ORANGE


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
