import pygame
import sys
import math
import asyncio
import random
import traceback 

# --- CONFIGURATION ---
WIDTH, HEIGHT = 800, 600
WHITE = (240, 240, 240)
BLACK = (20, 20, 20)
RED   = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE  = (50, 100, 255)
YELLOW = (255, 200, 0)
ORANGE = (255, 165, 0)
CYAN   = (0, 255, 255)
GRAY   = (150, 150, 150)

# --- CLASSES ---

class Player:
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
        self.decoys_left = 3 # You get 3 decoys per level!
    
    def move(self, keys):
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
                self.speed = self.base_speed * 0.5 # Tired!
        else:
            self.is_sprinting = False
            self.speed = self.base_speed
            if self.stamina < self.max_stamina:
                self.stamina += 0.5 # Recharge

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
        
        # Draw Stamina Bar (Above Player)
        bar_width = 30
        fill = (self.stamina / self.max_stamina) * bar_width
        pygame.draw.rect(surface, GRAY, (self.pos.x - 15, self.pos.y - 25, bar_width, 4))
        pygame.draw.rect(surface, BLUE, (self.pos.x - 15, self.pos.y - 25, fill, 4))

class Decoy:
    def __init__(self, x, y):
        self.pos = pygame.math.Vector2(x, y)
        self.rect = pygame.Rect(0, 0, 30, 30)
        self.rect.center = self.pos
        self.life = 180 # Lasts 3 seconds (60fps * 3)
    
    def update(self):
        self.life -= 1

    def draw(self, surface):
        # Looks like a "fake" player (Hollow Square)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        # Draw a little "!" so you know it's a decoy
        pygame.draw.line(surface, BLACK, (self.pos.x, self.pos.y-5), (self.pos.x, self.pos.y+5), 2)

class Teleporter:
    def __init__(self, x, y, color, is_exit=False):
        self.rect = pygame.Rect(0, 0, 40, 40)
        self.rect.center = (x, y)
        self.color = color
        self.is_exit = is_exit
        self.cooldown = 0
    
    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1

    def draw(self, surface):
        # Draw swirling circle
        pygame.draw.circle(surface, self.color, self.rect.center, 20, 2)
        pygame.draw.circle(surface, self.color, self.rect.center, 10 + (self.cooldown % 5))

class KeyItem:
    def __init__(self, x, y):
        self.rect = pygame.Rect(0,0, 20, 20)
        self.rect.center = (x, y)
        self.active = True
    
    def draw(self, surface):
        if self.active:
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
        self.distracted = False # Is chasing a decoy?
        self.target_decoy = None
        
    def update(self, player_pos, active_decoys):
        # 1. Check for Decoys
        self.distracted = False
        self.target_decoy = None
        
        # If any decoy is close, go for it!
        for decoy in active_decoys:
            dist = self.pos.distance_to(decoy.pos)
            if dist < 200: # Decoy range
                self.distracted = True
                self.target_decoy = decoy.pos
                break

        # 2. Determine Target
        if self.distracted:
            target = self.target_decoy
            self.speed = self.base_speed * 1.5 # Run at decoy
        elif self.alerted:
            target = player_pos
            self.speed = self.base_speed * 1.5 # Run at player
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
        if self.distracted: return False # If distracted, can't see player!
        
        vec_to_player = player.pos - self.pos
        dist = vec_to_player.length()
        if dist < self.vision_length:
            angle_to_player = math.degrees(math.atan2(-vec_to_player.y, vec_to_player.x))
            angle_diff = (angle_to_player - self.vision_angle + 180) % 360 - 180
            if abs(angle_diff) < 35: 
                return True
        return False

    def draw(self, surface):
        color = YELLOW if (self.alerted or self.distracted) else RED
        angle_rad = math.radians(self.vision_angle)
        left_angle = math.radians(self.vision_angle + 35)
        right_angle = math.radians(self.vision_angle - 35)
        
        # Vision Lines
        p1 = (int(self.pos.x), int(self.pos.y))
        p2 = (int(self.pos.x + math.cos(left_angle) * self.vision_length), int(self.pos.y - math.sin(left_angle) * self.vision_length))
        p3 = (int(self.pos.x + math.cos(right_angle) * self.vision_length), int(self.pos.y - math.sin(right_angle) * self.vision_length))
        
        pygame.draw.line(surface, color, p1, p2, 2)
        pygame.draw.line(surface, color, p1, p3, 2)
        pygame.draw.line(surface, color, p2, p3, 1)

        # Body
        tip = (int(self.pos.x + math.cos(angle_rad) * 20), int(self.pos.y - math.sin(angle_rad) * 20))
        left = (int(self.pos.x + math.cos(angle_rad + 2.5) * 15), int(self.pos.y - math.sin(angle_rad + 2.5) * 15))
        right = (int(self.pos.x + math.cos(angle_rad - 2.5) * 15), int(self.pos.y - math.sin(angle_rad - 2.5) * 15))
        
        pygame.draw.polygon(surface, RED, [tip, left, right])
        
        # "!" if distracted
        if self.distracted:
            pygame.draw.circle(surface, BLACK, (int(self.pos.x), int(self.pos.y - 30)), 5)

# --- LEVEL DATA ---
LEVELS = [
    { 
        "id": 1, 
        "start": (50, 300), "key_pos": (400, 300), "goal": (720, 300), 
        "enemy_path": [(200, 50), (600, 50), (600, 550), (200, 550)], "enemy_speed": 2.5, 
        "spots": [(200, 150, "circle"), (600, 150, "circle"), (200, 450, "square"), (600, 450, "square")],
        "teleporters": [] # No teleporters in Level 1
    },
    { 
        "id": 2, 
        "start": (50, 50), "key_pos": (700, 50), "goal": (720, 550), 
        "enemy_path": [(400, 100), (400, 500), (100, 300), (700, 300)], "enemy_speed": 3.0, 
        "spots": [(150, 150, "square"), (650, 150, "circle"), (400, 300, "circle"), (650, 450, "square")],
        "teleporters": [((100, 550), (700, 100))] # One pair (Orange -> Cyan)
    },
    { 
        "id": 3, 
        "start": (400, 550), "key_pos": (400, 300), "goal": (400, 50), 
        "enemy_path": [(100, 100), (700, 100), (700, 500), (100, 500)], "enemy_speed": 4.0, 
        "spots": [(200, 200, "square"), (600, 200, "square"), (200, 400, "circle"), (600, 400, "circle")],
        "teleporters": [((50, 300), (750, 300))] # Cross-map jump
    }
]

# --- MAIN GAME ---
async def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Camouflage: Safe Mode + Features")
    clock = pygame.time.Clock()
    font_big = pygame.font.SysFont("Arial", 48, bold=True)
    font_small = pygame.font.SysFont("Arial", 24)

    # Pre-render text
    txt_title = font_big.render("CAMOUFLAGE", True, BLACK)
    txt_sub = font_small.render("Safe Mode + Features", True, RED)
    txt_start = font_small.render("Press SPACE", True, BLACK)
    txt_caught = font_big.render("CAUGHT!", True, RED)
    txt_restart = font_small.render("Press SPACE to Restart", True, BLACK)
    txt_win = font_big.render("ESCAPED!", True, GREEN)

    state = "MENU"
    current_level_idx = 0
    active_decoys = []
    
    def load_level(idx):
        data = LEVELS[idx]
        p = Player(data["start"])
        e = Enemy(data["enemy_path"], speed=data["enemy_speed"])
        k = KeyItem(data["key_pos"][0], data["key_pos"][1])
        s_list = []
        for s_data in data["spots"]:
            s_list.append(HidingSpot(s_data[0], s_data[1], s_data[2]))
        
        t_list = []
        if "teleporters" in data:
            for pair in data["teleporters"]:
                t1 = Teleporter(pair[0][0], pair[0][1], ORANGE)
                t2 = Teleporter(pair[1][0], pair[1][1], CYAN)
                # Link them logically (handled in loop)
                t_list.append((t1, t2))

        g_rect = pygame.Rect(0, 0, 60, 60)
        g_rect.center = data["goal"]
        return p, e, k, s_list, t_list, g_rect

    player, enemy, key_item, spots, teleporters, goal_rect = load_level(0)

    running = True
    
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
                            active_decoys = []
                            player, enemy, key_item, spots, teleporters, goal_rect = load_level(current_level_idx)
                    
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
                            if state == "LEVEL_DONE":
                                current_level_idx += 1
                                if current_level_idx >= len(LEVELS):
                                    state = "ALL_COMPLETE"
                                else:
                                    player, enemy, key_item, spots, teleporters, goal_rect = load_level(current_level_idx)
                                    state = "PLAYING"
                            else:
                                player, enemy, key_item, spots, teleporters, goal_rect = load_level(current_level_idx)
                                state = "PLAYING"
                    
                    elif state == "ALL_COMPLETE":
                        if event.key == pygame.K_SPACE:
                            state = "MENU"

            # --- UPDATES ---
            if state == "PLAYING":
                keys = pygame.key.get_pressed()
                player.move(keys)
                
                # Decoy Update
                for d in active_decoys[:]:
                    d.update()
                    if d.life <= 0: active_decoys.remove(d)
                
                # Teleporter Logic
                for t_pair in teleporters:
                    t1, t2 = t_pair
                    t1.update()
                    t2.update()
                    
                    # Enter T1 -> Go to T2
                    if player.rect.colliderect(t1.rect) and t1.cooldown == 0:
                        player.pos = pygame.math.Vector2(t2.rect.center)
                        t2.cooldown = 60 # 1 second safe time
                    
                    # Enter T2 -> Go to T1
                    elif player.rect.colliderect(t2.rect) and t2.cooldown == 0:
                        player.pos = pygame.math.Vector2(t1.rect.center)
                        t1.cooldown = 60
                
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
                
                enemy.update(player.pos, active_decoys)

                # Death Check
                dist_to_enemy = player.pos.distance_to(enemy.pos)
                if dist_to_enemy < 25:
                    state = "GAME_OVER"

            # --- DRAWING ---
            screen.fill(WHITE)

            if state == "MENU":
                screen.blit(txt_title, (WIDTH//2 - txt_title.get_width()//2, 200))
                screen.blit(txt_sub, (WIDTH//2 - txt_sub.get_width()//2, 260))
                screen.blit(txt_start, (WIDTH//2 - txt_start.get_width()//2, 400))
                
                controls = font_small.render("Z = Decoy | SHIFT = Sprint | Portals = Teleport", True, BLUE)
                screen.blit(controls, (WIDTH//2 - controls.get_width()//2, 500))

            elif state == "PLAYING" or state == "GAME_OVER":
                goal_color = GREEN if player.has_key else RED
                pygame.draw.rect(screen, goal_color, goal_rect)
                
                for spot in spots: spot.draw(screen)
                
                for t_pair in teleporters:
                    t_pair[0].draw(screen)
                    t_pair[1].draw(screen)
                    
                key_item.draw(screen)
                
                for d in active_decoys: d.draw(screen)
                
                enemy.draw(screen)
                
                if state == "PLAYING":
                    player.draw(screen)
                
                if state == "GAME_OVER":
                    screen.blit(txt_caught, (WIDTH//2 - txt_caught.get_width()//2, HEIGHT//2 - 50))
                    screen.blit(txt_restart, (WIDTH//2 - txt_restart.get_width()//2, HEIGHT//2 + 10))
                
                # UI
                decoy_txt = font_small.render(f"Decoys: {player.decoys_left}", True, BLACK)
                screen.blit(decoy_txt, (10, 570))

            elif state == "LEVEL_DONE":
                screen.fill(GREEN)
                screen.blit(txt_win, (WIDTH//2 - txt_win.get_width()//2, 250))
            
            elif state == "ALL_COMPLETE":
                screen.fill(BLACK)

            pygame.display.flip()
            await asyncio.sleep(0)

    except Exception as e:
        print(f"CRASH CAUGHT: {e}")
        traceback.print_exc()
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