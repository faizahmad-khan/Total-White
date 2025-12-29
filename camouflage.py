import pygame
import sys
import math

# --- CONFIGURATION ---
WIDTH, HEIGHT = 800, 600
WHITE = (240, 240, 240) # Slightly off-white for realism
BLACK = (20, 20, 20)    # Soft black
RED   = (200, 50, 50)   # Enemy Color
GREEN = (50, 200, 50)   # Win Zone
VISION_COLOR = (255, 0, 0, 60) # Transparent Red

# --- SETUP ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Camouflage: Advanced Stealth")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24, bold=True)

# --- CLASSES ---

class Player:
    def __init__(self):
        self.pos = pygame.math.Vector2(50, 300)
        self.rect = pygame.Rect(0, 0, 30, 30)
        self.rect.center = self.pos
        self.shape_type = "square"
        self.speed = 4
        self.angle = 0

    def move(self, keys):
        # Vector based movement for smoother feel
        vel = pygame.math.Vector2(0, 0)
        if keys[pygame.K_LEFT]:  vel.x = -1
        if keys[pygame.K_RIGHT]: vel.x = 1
        if keys[pygame.K_UP]:    vel.y = -1
        if keys[pygame.K_DOWN]:  vel.y = 1

        # Normalize diagonal speed
        if vel.length() > 0:
            vel = vel.normalize() * self.speed
            self.pos += vel

        # Screen Constraints
        self.pos.x = max(20, min(WIDTH - 20, self.pos.x))
        self.pos.y = max(20, min(HEIGHT - 20, self.pos.y))
        
        self.rect.center = self.pos

    def draw(self, surface):
        if self.shape_type == "square":
            pygame.draw.rect(surface, BLACK, self.rect)
        elif self.shape_type == "circle":
            pygame.draw.circle(surface, BLACK, (int(self.pos.x), int(self.pos.y)), 15)

class HidingSpot:
    def __init__(self, x, y, shape_type):
        self.rect = pygame.Rect(0, 0, 40, 40)
        self.rect.center = (x, y)
        self.shape_type = shape_type 

    def draw(self, surface):
        # Draw thicker, cleaner lines
        if self.shape_type == "square":
            pygame.draw.rect(surface, BLACK, self.rect, 3)
        elif self.shape_type == "circle":
            pygame.draw.circle(surface, BLACK, self.rect.center, 20, 3)

class Enemy:
    def __init__(self, patrol_points):
        self.points = patrol_points # List of (x,y) coordinates
        self.current_point_index = 0
        self.pos = pygame.math.Vector2(self.points[0])
        self.speed = 2.5
        self.vision_length = 150
        self.vision_angle = 0 # Degrees

    def update(self):
        # 1. Target the next point in the list
        target = pygame.math.Vector2(self.points[self.current_point_index])
        direction = target - self.pos
        dist = direction.length()

        if dist < 5:
            # Reached waypoint, go to next one
            self.current_point_index = (self.current_point_index + 1) % len(self.points)
        else:
            # Move towards target
            direction = direction.normalize()
            self.pos += direction * self.speed
            
            # Calculate angle for looking
            # math.atan2 returns radians, we convert to degrees
            self.vision_angle = math.degrees(math.atan2(-direction.y, direction.x))

    def can_see(self, player):
        # 1. Check Distance
        vec_to_player = player.pos - self.pos
        dist = vec_to_player.length()
        
        if dist < self.vision_length:
            # 2. Check Angle (Are they within the cone?)
            angle_to_player = math.degrees(math.atan2(-vec_to_player.y, vec_to_player.x))
            
            # Normalize angles to handle the -180/180 jump
            angle_diff = (angle_to_player - self.vision_angle + 180) % 360 - 180
            
            # If within 45 degrees field of view
            if abs(angle_diff) < 30: 
                return True
        return False

    def draw(self, surface):
        # 1. Draw Vision Cone (Using a transparent surface)
        cone_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        # Calculate cone triangle points
        angle_rad = math.radians(self.vision_angle)
        left_angle = math.radians(self.vision_angle + 30)
        right_angle = math.radians(self.vision_angle - 30)
        
        p1 = self.pos
        p2 = self.pos + pygame.math.Vector2(math.cos(left_angle), -math.sin(left_angle)) * self.vision_length
        p3 = self.pos + pygame.math.Vector2(math.cos(right_angle), -math.sin(right_angle)) * self.vision_length
        
        pygame.draw.polygon(cone_surface, VISION_COLOR, [p1, p2, p3])
        surface.blit(cone_surface, (0,0))

        # 2. Draw Enemy Body (Triangle shape to show direction)
        # Pointing tip
        tip = self.pos + pygame.math.Vector2(math.cos(angle_rad), -math.sin(angle_rad)) * 20
        # Back corners
        left_wing = self.pos + pygame.math.Vector2(math.cos(angle_rad + 2.5), -math.sin(angle_rad + 2.5)) * 15
        right_wing = self.pos + pygame.math.Vector2(math.cos(angle_rad - 2.5), -math.sin(angle_rad - 2.5)) * 15
        
        pygame.draw.polygon(surface, RED, [tip, left_wing, right_wing])

# --- GAME LOOP ---

def main():
    player = Player()
    
    # Hiding spots scattered around
    spots = [
        HidingSpot(200, 150, "circle"),
        HidingSpot(400, 300, "square"),
        HidingSpot(150, 450, "square"),
        HidingSpot(600, 150, "circle"),
        HidingSpot(500, 500, "square"),
    ]

    # --- ENEMY PATROL PATH ---
    # These are the coordinates the enemy will walk to in order
    patrol_path = [
        (200, 50),
        (600, 50),
        (600, 550),
        (200, 550),
        (400, 300) # Goes to middle then restarts
    ]
    enemy = Enemy(patrol_path)

    goal_rect = pygame.Rect(720, 280, 60, 80)

    running = True
    game_state = "PLAYING" # PLAYING, WON, LOST

    while running:
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if game_state == "PLAYING":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        shifted = False
                        for spot in spots:
                            # Using colliderect with a small offset for leniency
                            if player.rect.colliderect(spot.rect):
                                player.shape_type = spot.shape_type
                                shifted = True
                        if shifted:
                            print(f"Shifted to {player.shape_type}")

        # 2. Logic Updates
        if game_state == "PLAYING":
            keys = pygame.key.get_pressed()
            player.move(keys)
            enemy.update()

            # WIN CHECK
            if player.rect.colliderect(goal_rect):
                game_state = "WON"

            # CAUGHT CHECK
            if enemy.can_see(player):
                # Caught logic:
                is_moving = (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or 
                             keys[pygame.K_UP] or keys[pygame.K_DOWN])
                
                safe_spot = False
                for spot in spots:
                    # Check if center is close enough (better than rect collision)
                    dist = player.pos.distance_to(pygame.math.Vector2(spot.rect.center))
                    if dist < 20 and player.shape_type == spot.shape_type:
                        safe_spot = True
                
                if is_moving or not safe_spot:
                    game_state = "LOST"

        # 3. Drawing
        screen.fill(WHITE)

        # Draw Goal
        pygame.draw.rect(screen, GREEN, goal_rect)
        
        # Draw Spots
        for spot in spots:
            spot.draw(screen)

        # Draw Enemy
        enemy.draw(screen)

        # Draw Player
        player.draw(screen)

        # Draw UI based on state
        if game_state == "LOST":
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(150)
            overlay.fill(RED)
            screen.blit(overlay, (0,0))
            text = font.render("SEEN! Game Over.", True, WHITE)
            screen.blit(text, (WIDTH//2 - 100, HEIGHT//2))
            
        elif game_state == "WON":
            text = font.render("ESCAPED! You Win!", True, GREEN)
            screen.blit(text, (WIDTH//2 - 100, HEIGHT//2))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()