"""Player character with shape-shifting, sprint, and decoy mechanics."""

import pygame

from config import (
    BLACK, BLUE, GOLD, GRAY, RED, WIDTH, HEIGHT,
    PLAYER_SIZE, PLAYER_BASE_SPEED, PLAYER_SPRINT_MULTIPLIER,
    PLAYER_MAX_STAMINA, PLAYER_MAX_DECOYS,
    NOISE_MOVE_RADIUS, NOISE_SPRINT_RADIUS, NOISE_SPRINT_INTERVAL
)


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
        self.rect = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)
        self.rect.center = self.pos
        self.shape_type = "square"
        self.base_speed = PLAYER_BASE_SPEED
        self.speed = PLAYER_BASE_SPEED
        self.has_key = False

        # Sprint System
        self.stamina = PLAYER_MAX_STAMINA
        self.max_stamina = PLAYER_MAX_STAMINA
        self.is_sprinting = False

        # Decoy System
        self.decoys_left = PLAYER_MAX_DECOYS
        self.movement_tick = 0

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
                self.speed = self.base_speed * PLAYER_SPRINT_MULTIPLIER
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

    def get_noise(self, is_moving):
        radius = 0
        emitted = False
        if is_moving:
            self.movement_tick += 1
            if self.is_sprinting:
                radius = NOISE_SPRINT_RADIUS
                if self.movement_tick >= NOISE_SPRINT_INTERVAL:
                    emitted = True
                    self.movement_tick = 0
            else:
                radius = NOISE_MOVE_RADIUS
                emitted = True
        return radius, emitted
