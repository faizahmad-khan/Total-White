"""Enemy guard with patrol AI, vision cone detection, and noise reaction."""

import math

import pygame

from config import (
    BLACK, ORANGE, RED, YELLOW,
    ENEMY_VISION_LENGTH, ENEMY_SPRINT_MULTIPLIER, ENEMY_DISTRACTION_RANGE, ENEMY_BASE_SPEED,
    NOISE_ENEMY_HEAR_RADIUS,
    THREAT_MAX, THREAT_DECAY_RATE, THREAT_DETECTION_GAIN
)


class Enemy:
    """A patrolling guard with a vision cone that detects the player.

    Enemies follow predefined patrol routes. They can be distracted
    by decoys, triggered by noise, and will chase the player when alerted.

    Attributes:
        state: One of ('PATROL', 'INVESTIGATE', 'ALERT', 'DISTRACTED').
        threat: 0..THREAT_MAX noise suspicion level.
        noise_target: Position the enemy heard noise from.
        alerted: Whether the enemy is actively chasing the player.
        distracted: Whether the enemy is chasing a decoy.
    """

    def __init__(self, patrol_points, speed=None):
        if speed is None:
            speed = ENEMY_BASE_SPEED
        self.points = patrol_points
        self.current_point_index = 0
        self.pos = pygame.math.Vector2(self.points[0])
        self.base_speed = speed
        self.speed = speed
        self.vision_length = ENEMY_VISION_LENGTH
        self.vision_angle = 0
        self.state = "PATROL"
        self.alerted = False
        self.distracted = False
        self.target_decoy = None
        self.threat = 0
        self.noise_target = None

    def update(self, player_pos, active_decoys, noise_points=None):
        """Update enemy state and movement.

        Args:
            player_pos: Current player position as Vector2.
            active_decoys: List of active Decoy objects on the map.
            noise_points: Optional list of (Vector2, radius) noise sources.
        """
        is_distracted = False
        target_decoy_pos = None

        for decoy in active_decoys:
            dist = self.pos.distance_to(decoy.pos)
            if dist < ENEMY_DISTRACTION_RANGE:
                is_distracted = True
                target_decoy_pos = decoy.pos
                break

        nearest_noise_target = None
        nearest_noise_dist = 999999
        if noise_points:
            for (np, nr) in noise_points:
                d = self.pos.distance_to(np)
                if d < nr + NOISE_ENEMY_HEAR_RADIUS and d < nearest_noise_dist:
                    nearest_noise_dist = d
                    nearest_noise_target = np

        if is_distracted:
            self.state = "DISTRACTED"
            self.target_decoy = target_decoy_pos
            self.distracted = True
            self.noise_target = None
            self.threat = 0
            self.alerted = False
        elif nearest_noise_target and self.threat > 0:
            dist_to_noise = self.pos.distance_to(nearest_noise_target)
            if dist_to_noise < 10:
                self.noise_target = None
                self.threat -= 20
                if self.threat < 0:
                    self.threat = 0
            else:
                self.noise_target = nearest_noise_target
            if self.can_see(player_pos):
                if dist_to_noise > ENEMY_VISION_LENGTH + 120:
                    self.state = "ALERT"
                    self.alerted = True
                    target = player_pos
                    self.speed = self.base_speed * ENEMY_SPRINT_MULTIPLIER
                else:
                    self.state = "INVESTIGATE"
                    if self.threat > 40:
                        self.speed = self.base_speed * ENEMY_SPRINT_MULTIPLIER * 0.85
                    else:
                        self.speed = self.base_speed * 1.25
                    target = self.noise_target
            else:
                self.state = "INVESTIGATE"
                if self.threat > 40:
                    self.speed = self.base_speed * ENEMY_SPRINT_MULTIPLIER * 0.85
                else:
                    self.speed = self.base_speed * 1.25
                target = self.noise_target
        elif nearest_noise_target and self.threat <= 0:
            self.noise_target = nearest_noise_target
            self.threat += 25
            self.state = "INVESTIGATE"
            if self.threat > 40:
                self.speed = self.base_speed * ENEMY_SPRINT_MULTIPLIER * 0.85
            else:
                self.speed = self.base_speed * 1.25
            target = self.noise_target
        elif self.alerted:
            self.state = "ALERT"
            self.noise_target = None
            target = player_pos
            self.speed = self.base_speed * ENEMY_SPRINT_MULTIPLIER
        else:
            self.state = "PATROL"
            self.alerted = False
            self.noise_target = None
            target = pygame.math.Vector2(self.points[self.current_point_index])
            self.speed = self.base_speed

        if self.threat > 0 and not nearest_noise_target:
            self.threat -= THREAT_DECAY_RATE
            if self.threat < 0:
                self.threat = 0

        direction = target - self.pos
        dist = direction.length()

        if self.state == "PATROL" and dist < 5:
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
        """Render the enemy triangle and its vision cone border lines."""
        color = YELLOW if (self.alerted or self.distracted or self.state == "INVESTIGATE") else RED
        angle_rad = math.radians(self.vision_angle)
        left_angle = math.radians(self.vision_angle + 35)
        right_angle = math.radians(self.vision_angle - 35)

        p1 = (int(self.pos.x), int(self.pos.y))
        p2 = (int(self.pos.x + math.cos(left_angle) * self.vision_length),
              int(self.pos.y - math.sin(left_angle) * self.vision_length))
        p3 = (int(self.pos.x + math.cos(right_angle) * self.vision_length),
              int(self.pos.y - math.sin(right_angle) * self.vision_length))

        pygame.draw.line(surface, color, p1, p2, 2)
        pygame.draw.line(surface, color, p1, p3, 2)
        pygame.draw.line(surface, color, p2, p3, 1)

        tip = (int(self.pos.x + math.cos(angle_rad) * 20),
               int(self.pos.y - math.sin(angle_rad) * 20))
        left = (int(self.pos.x + math.cos(angle_rad + 2.5) * 15),
                int(self.pos.y - math.sin(angle_rad + 2.5) * 15))
        right = (int(self.pos.x + math.cos(angle_rad - 2.5) * 15),
                 int(self.pos.y - math.sin(angle_rad - 2.5) * 15))

        pygame.draw.polygon(surface, RED, [tip, left, right])
        pygame.draw.polygon(surface, BLACK, [tip, left, right], 1)

        if self.distracted:
            pygame.draw.circle(surface, ORANGE, (int(self.pos.x), int(self.pos.y - 30)), 6)
        elif self.alerted or self.state == "ALERT":
            pygame.draw.circle(surface, RED, (int(self.pos.x), int(self.pos.y - 30)), 6)
        elif self.state == "INVESTIGATE":
            pygame.draw.circle(surface, YELLOW, (int(self.pos.x), int(self.pos.y - 30)), 6)
            pygame.draw.circle(surface, BLACK, (int(self.pos.x), int(self.pos.y - 30)), 6, 1)

        if self.state in ("INVESTIGATE", "ALERT"):
            bar_width = 40
            fill = min(1.0, self.threat / THREAT_MAX) * bar_width
            pygame.draw.rect(surface, DARK_GRAY if 'DARK_GRAY' in globals() else (80, 80, 80),
                             (self.pos.x - bar_width // 2, self.pos.y - 40, bar_width, 4))
            bar_color = YELLOW if self.state == "INVESTIGATE" else RED
            pygame.draw.rect(surface, bar_color,
                             (self.pos.x - bar_width // 2, self.pos.y - 40, fill, 4))

    def draw_vision_cone(self, cone_surface):
        """Render only the semi-transparent filled cone onto a shared overlay."""
        left_angle = math.radians(self.vision_angle + 35)
        right_angle = math.radians(self.vision_angle - 35)

        p1 = (int(self.pos.x), int(self.pos.y))
        p2 = (int(self.pos.x + math.cos(left_angle) * self.vision_length),
              int(self.pos.y - math.sin(left_angle) * self.vision_length))
        p3 = (int(self.pos.x + math.cos(right_angle) * self.vision_length),
              int(self.pos.y - math.sin(right_angle) * self.vision_length))

        alpha = 55 if self.alerted or self.state == "ALERT" else 35
        cone_color = (255, 200, 0, alpha) if self.alerted or self.state == "INVESTIGATE" else (200, 50, 50, 30)
        pygame.draw.polygon(cone_surface, cone_color, [p1, p2, p3])
