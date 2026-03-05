"""Enemy guard with patrol AI and vision cone detection."""

import math

import pygame

from config import BLACK, ORANGE, RED, YELLOW, WIDTH, HEIGHT


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
        elif self.alerted:
            pygame.draw.circle(surface, RED, (int(self.pos.x), int(self.pos.y - 30)), 6)
