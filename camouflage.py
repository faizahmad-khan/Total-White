import pygame
import sys

# --- CONFIGURATION ---
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)   # Color for the Enemy
GREEN = (0, 200, 0)   # Color for the Win Zone

# --- SETUP ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Camouflage: Stealth Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)

# --- CLASSES ---

class Player:
    def __init__(self):
        self.rect = pygame.Rect(50, 300, 40, 40)
        self.shape_type = "square"  # Default shape
        self.speed = 5
        self.is_hidden = False

    def move(self, keys):
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:  dx = -self.speed
        if keys[pygame.K_RIGHT]: dx = self.speed
        if keys[pygame.K_UP]:    dy = -self.speed
        if keys[pygame.K_DOWN]:  dy = self.speed
        
        self.rect.x += dx
        self.rect.y += dy
        
        # Keep player on screen
        self.rect.clamp_ip(screen.get_rect())

    def draw(self, surface):
        # Draw the player based on their current shape
        if self.shape_type == "square":
            pygame.draw.rect(surface, BLACK, self.rect)
        elif self.shape_type == "circle":
            pygame.draw.circle(surface, BLACK, self.rect.center, 20)

class HidingSpot:
    def __init__(self, x, y, shape_type):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.shape_type = shape_type 

    def draw(self, surface):
        # Draw outlines of shapes you can hide in
        if self.shape_type == "square":
            pygame.draw.rect(surface, BLACK, self.rect, 2)
        elif self.shape_type == "circle":
            pygame.draw.circle(surface, BLACK, self.rect.center, 20, 2)

class Enemy:
    def __init__(self, start_x, end_x, y):
        self.rect = pygame.Rect(start_x, y, 40, 40)
        self.start_x = start_x
        self.end_x = end_x
        self.direction = 1 # 1 is right, -1 is left
        self.speed = 3
        # Vision cone is a rectangle in front of the enemy
        self.vision_rect = pygame.Rect(start_x, y, 150, 40) 

    def update(self):
        # Patrol logic
        self.rect.x += self.speed * self.direction
        if self.rect.x >= self.end_x or self.rect.x <= self.start_x:
            self.direction *= -1 # Reverse direction

        # Update vision cone position based on direction
        if self.direction == 1: # Looking Right
            self.vision_rect.topleft = self.rect.topright
            self.vision_rect.width = 150
        else: # Looking Left
            self.vision_rect.topright = self.rect.topleft
            self.vision_rect.width = 150
            self.vision_rect.x = self.rect.x - 150

    def draw(self, surface):
        # Draw Enemy (Red Triangle-ish shape)
        pygame.draw.rect(surface, RED, self.rect)
        
        # Draw Vision Cone (Light Grey, semi-transparent)
        s = pygame.Surface((self.vision_rect.width, self.vision_rect.height))
        s.set_alpha(50) # Transparency
        s.fill((255, 0, 0))
        surface.blit(s, (self.vision_rect.x, self.vision_rect.y))

# --- GAME LOOP ---

def main():
    player = Player()
    
    # Create Hiding Spots (Outlines)
    spots = [
        HidingSpot(200, 100, "circle"),
        HidingSpot(300, 400, "square"),
        HidingSpot(500, 200, "circle"),
        HidingSpot(600, 400, "square"),
    ]

    # Create Enemy
    enemy = Enemy(200, 600, 300) # Patrols x=200 to x=600 at y=300

    # Win Zone
    goal_rect = pygame.Rect(700, 280, 50, 80)

    running = True
    game_over = False
    won = False

    while running:
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if not game_over and not won:
                # Shape Shifting Mechanic
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Check if touching a hiding spot
                        shifted = False
                        for spot in spots:
                            if player.rect.colliderect(spot.rect):
                                player.shape_type = spot.shape_type
                                shifted = True
                        if shifted:
                            print(f"Camouflage active: {player.shape_type}")

        # 2. Logic Updates
        if not game_over and not won:
            keys = pygame.key.get_pressed()
            player.move(keys)
            enemy.update()

            # WIN CONDITION
            if player.rect.colliderect(goal_rect):
                won = True

            # LOSE CONDITION (Enemy Vision)
            if player.rect.colliderect(enemy.vision_rect):
                # You are caught UNLESS:
                # 1. You are not moving (we approximate this by not pressing keys)
                is_moving = any(keys)
                
                # 2. You are matching a nearby hiding spot
                safe_spot = False
                for spot in spots:
                    # Are we exactly inside/touching a spot of the same shape?
                    if player.rect.colliderect(spot.rect) and player.shape_type == spot.shape_type:
                        safe_spot = True
                
                # If you are moving OR you aren't in a matching spot -> CAUGHT
                if is_moving or not safe_spot:
                    game_over = True

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

        # Draw UI Text
        if game_over:
            text = font.render("CAUGHT! Game Over. (Close to restart)", True, RED)
            screen.blit(text, (WIDTH//2 - 150, HEIGHT//2))
        elif won:
            text = font.render("ESCAPED! You Win!", True, GREEN)
            screen.blit(text, (WIDTH//2 - 100, HEIGHT//2))
        else:
            inst = font.render("Arrows to Move | SPACE to Shift Shape", True, BLACK)
            screen.blit(inst, (10, 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()