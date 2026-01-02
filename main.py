import pygame
import sys
import math
import asyncio
import random
import traceback # To print errors to screen if it crashes

# --- CONFIGURATION ---
WIDTH, HEIGHT = 800, 600
WHITE = (240, 240, 240)
BLACK = (20, 20, 20)
RED   = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE  = (50, 100, 255)
YELLOW = (255, 200, 0)

# --- CLASSES ---

class Player:
    def __init__(self, start_pos):
        self.pos = pygame.math.Vector2(start_pos)
        self.rect = pygame.Rect(0, 0, 30, 30)
        self.rect.center = self.pos
        self.shape_type = "square"
        self.speed = 4
        self.has_key = False
    
    def move(self, keys):
        vel = pygame.math.Vector2(0, 0)
        if keys[pygame.K_LEFT]:  vel.x = -1
        if keys[pygame.K_RIGHT]: vel.x = 1
        if keys[pygame.K_UP]:    vel.y = -1
        if keys[pygame.K_DOWN]:  vel.y = 1

        if vel.length() > 0:
            vel = vel.normalize() * self.speed
            self.pos += vel

        self.pos.x = max(20, min(WIDTH - 20, self.pos.x))
        self.pos.y = max(20, min(HEIGHT - 20, self.pos.y))
        self.rect.center = self.pos

    def draw(self, surface):
        if self.shape_type == "square":
            pygame.draw.rect(surface, BLACK, self.rect)
        elif self.shape_type == "circle":
            center = (int(self.pos.x), int(self.pos.y))
            pygame.draw.circle(surface, BLACK, center, 15)

class KeyItem:
    def __init__(self, x, y):
        self.rect = pygame.Rect(0,0, 20, 20)
        self.rect.center = (x, y)
        self.active = True
    
    def draw(self, surface):
        if self.active:
            # Simple static diamond to prevent math errors
            cx, cy = self.rect.center
            p1 = (cx, cy - 10)
            p2 = (cx + 10, cy)
            p3 = (cx, cy + 10)
            p4 = (cx - 10, cy)
            pygame.draw.polygon(surface, BLUE, [p1, p2, p3, p4])

class HidingSpot:
    def __init__(self, x, y, shape_type):
        self.rect = pygame.Rect(0, 0, 40, 40)
        self.rect.center = (x, y)
        self.shape_type = shape_type 

    def draw(self, surface):
        if self.shape_type == "square":
            pygame.draw.rect(surface, BLACK, self.rect, 3)
        elif self.shape_type == "circle":
            pygame.draw.circle(surface, BLACK, self.rect.center, 20, 3)

class Enemy:
    def __init__(self, patrol_points, speed=2.5):
        self.points = patrol_points
        self.current_point_index = 0
        self.pos = pygame.math.Vector2(self.points[0])
        self.base_speed = speed
        self.speed = speed
        self.vision_length = 160
        self.vision_angle = 0
        self.alerted = False
        
    def update(self, player_pos):
        target = pygame.math.Vector2(self.points[self.current_point_index])
        if self.alerted:
            target = player_pos
            self.speed = self.base_speed * 1.5
        else:
            self.speed = self.base_speed

        direction = target - self.pos
        dist = direction.length()

        if not self.alerted and dist < 5:
            self.current_point_index = (self.current_point_index + 1) % len(self.points)
        elif dist > 1:
            direction = direction.normalize()
            self.pos += direction * self.speed
            self.vision_angle = math.degrees(math.atan2(-direction.y, direction.x))

    def can_see(self, player):
        vec_to_player = player.pos - self.pos
        dist = vec_to_player.length()
        if dist < self.vision_length:
            angle_to_player = math.degrees(math.atan2(-vec_to_player.y, vec_to_player.x))
            angle_diff = (angle_to_player - self.vision_angle + 180) % 360 - 180
            if abs(angle_diff) < 35: 
                return True
        return False

    def draw(self, surface):
        # SIMPLIFIED DRAWING: No transparency, just lines
        color = YELLOW if self.alerted else RED
        angle_rad = math.radians(self.vision_angle)
        left_angle = math.radians(self.vision_angle + 35)
        right_angle = math.radians(self.vision_angle - 35)
        
        # Draw Vision Lines (Wireframe) instead of Polygon
        p1 = (int(self.pos.x), int(self.pos.y))
        p2 = (int(self.pos.x + math.cos(left_angle) * self.vision_length), int(self.pos.y - math.sin(left_angle) * self.vision_length))
        p3 = (int(self.pos.x + math.cos(right_angle) * self.vision_length), int(self.pos.y - math.sin(right_angle) * self.vision_length))
        
        pygame.draw.line(surface, color, p1, p2, 2)
        pygame.draw.line(surface, color, p1, p3, 2)
        pygame.draw.line(surface, color, p2, p3, 1) # Connect tips

        # Draw Enemy Body (Triangle)
        tip = (int(self.pos.x + math.cos(angle_rad) * 20), int(self.pos.y - math.sin(angle_rad) * 20))
        left = (int(self.pos.x + math.cos(angle_rad + 2.5) * 15), int(self.pos.y - math.sin(angle_rad + 2.5) * 15))
        right = (int(self.pos.x + math.cos(angle_rad - 2.5) * 15), int(self.pos.y - math.sin(angle_rad - 2.5) * 15))
        
        pygame.draw.polygon(surface, RED, [tip, left, right])

# --- LEVEL DATA ---
LEVELS = [
    { "id": 1, "start": (50, 300), "key_pos": (400, 300), "goal": (720, 300), "enemy_path": [(200, 50), (600, 50), (600, 550), (200, 550)], "enemy_speed": 2.5, "spots": [(200, 150, "circle"), (600, 150, "circle"), (200, 450, "square"), (600, 450, "square")]},
    { "id": 2, "start": (50, 50), "key_pos": (700, 50), "goal": (720, 550), "enemy_path": [(400, 100), (400, 500), (100, 300), (700, 300)], "enemy_speed": 3.0, "spots": [(150, 150, "square"), (650, 150, "circle"), (400, 300, "circle"), (650, 450, "square")]},
    { "id": 3, "start": (400, 550), "key_pos": (400, 300), "goal": (400, 50), "enemy_path": [(100, 100), (700, 100), (700, 500), (100, 500)], "enemy_speed": 4.0, "spots": [(200, 200, "square"), (600, 200, "square"), (200, 400, "circle"), (600, 400, "circle")]}
]

# --- MAIN GAME ---
async def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Camouflage: Safe Mode")
    clock = pygame.time.Clock()
    font_big = pygame.font.SysFont("Arial", 48, bold=True)
    font_small = pygame.font.SysFont("Arial", 24)

    # Pre-render text
    txt_title = font_big.render("CAMOUFLAGE", True, BLACK)
    txt_sub = font_small.render("Safe Mode", True, RED)
    txt_start = font_small.render("Press SPACE", True, BLACK)
    txt_caught = font_big.render("CAUGHT!", True, RED)
    txt_restart = font_small.render("Press SPACE to Restart", True, BLACK)
    txt_win = font_big.render("ESCAPED!", True, GREEN)

    state = "MENU"
    current_level_idx = 0
    
    def load_level(idx):
        data = LEVELS[idx]
        p = Player(data["start"])
        e = Enemy(data["enemy_path"], speed=data["enemy_speed"])
        k = KeyItem(data["key_pos"][0], data["key_pos"][1])
        s_list = []
        for s_data in data["spots"]:
            s_list.append(HidingSpot(s_data[0], s_data[1], s_data[2]))
        g_rect = pygame.Rect(0, 0, 60, 60)
        g_rect.center = data["goal"]
        return p, e, k, s_list, g_rect

    player, enemy, key_item, spots, goal_rect = load_level(0)

    running = True
    
    # CRASH PROTECTION START
    try: 
        while running:
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.KEYDOWN:
                    if state == "MENU":
                        if event.key == pygame.K_SPACE:
                            state = "PLAYING"
                            current_level_idx = 0
                            player, enemy, key_item, spots, goal_rect = load_level(current_level_idx)
                    
                    elif state == "PLAYING":
                        if event.key == pygame.K_SPACE:
                            for spot in spots:
                                if player.rect.colliderect(spot.rect):
                                    player.shape_type = spot.shape_type

                    elif state in ["GAME_OVER", "LEVEL_DONE"]:
                        if event.key == pygame.K_SPACE:
                            if state == "LEVEL_DONE":
                                current_level_idx += 1
                                if current_level_idx >= len(LEVELS):
                                    state = "ALL_COMPLETE"
                                else:
                                    player, enemy, key_item, spots, goal_rect = load_level(current_level_idx)
                                    state = "PLAYING"
                            else:
                                player, enemy, key_item, spots, goal_rect = load_level(current_level_idx)
                                state = "PLAYING"
                    
                    elif state == "ALL_COMPLETE":
                        if event.key == pygame.K_SPACE:
                            state = "MENU"

            # --- UPDATES ---
            if state == "PLAYING":
                keys = pygame.key.get_pressed()
                player.move(keys)
                
                if key_item.active and player.rect.colliderect(key_item.rect):
                    key_item.active = False
                    player.has_key = True

                if player.rect.colliderect(goal_rect):
                    if player.has_key:
                        state = "LEVEL_DONE"
                
                seen = enemy.can_see(player)
                safe_spot = False
                for spot in spots:
                    dist = player.pos.distance_to(pygame.math.Vector2(spot.rect.center))
                    if dist < 20 and player.shape_type == spot.shape_type:
                        safe_spot = True
                
                is_moving = any([keys[pygame.K_LEFT], keys[pygame.K_RIGHT], keys[pygame.K_UP], keys[pygame.K_DOWN]])
                
                if seen and (is_moving or not safe_spot):
                    enemy.alerted = True 
                else:
                    enemy.alerted = False
                
                enemy.update(player.pos)

                # Simplified Death Check
                dist_to_enemy = player.pos.distance_to(enemy.pos)
                if dist_to_enemy < 25:
                    state = "GAME_OVER"

            # --- DRAWING ---
            screen.fill(WHITE)

            if state == "MENU":
                screen.blit(txt_title, (WIDTH//2 - txt_title.get_width()//2, 200))
                screen.blit(txt_sub, (WIDTH//2 - txt_sub.get_width()//2, 260))
                screen.blit(txt_start, (WIDTH//2 - txt_start.get_width()//2, 400))

            elif state == "PLAYING" or state == "GAME_OVER":
                goal_color = GREEN if player.has_key else RED
                pygame.draw.rect(screen, goal_color, goal_rect)
                
                for spot in spots: spot.draw(screen)
                key_item.draw(screen)
                enemy.draw(screen)
                
                if state == "PLAYING":
                    player.draw(screen)
                
                if state == "GAME_OVER":
                    screen.blit(txt_caught, (WIDTH//2 - txt_caught.get_width()//2, HEIGHT//2 - 50))
                    screen.blit(txt_restart, (WIDTH//2 - txt_restart.get_width()//2, HEIGHT//2 + 10))

            elif state == "LEVEL_DONE":
                screen.fill(GREEN)
                screen.blit(txt_win, (WIDTH//2 - txt_win.get_width()//2, 250))
            
            elif state == "ALL_COMPLETE":
                screen.fill(BLACK)

            pygame.display.flip()
            await asyncio.sleep(0)

    except Exception as e:
        # IF IT CRASHES, PRINT ERROR TO SCREEN
        print(f"CRASH CAUGHT: {e}")
        screen.fill(BLACK)
        err_txt = font_small.render("ERROR!", True, RED)
        err_msg = font_small.render(str(e), True, WHITE)
        screen.blit(err_txt, (10, 10))
        screen.blit(err_msg, (10, 50))
        pygame.display.flip()
        while True:
            await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())