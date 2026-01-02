import pygame
import sys
import math
import asyncio
import array
import random

# --- CONFIGURATION ---
WIDTH, HEIGHT = 800, 600
WHITE = (240, 240, 240)
BLACK = (20, 20, 20)
RED   = (200, 50, 50)   # Enemy / Locked Door
GREEN = (50, 200, 50)   # Unlocked Door
BLUE  = (50, 100, 255)  # Key
YELLOW = (255, 200, 0)  # Alert Color
VISION_COLOR = (255, 0, 0, 60)
ALERT_COLOR = (255, 200, 0, 80)

# --- SOUND GENERATOR ---
class SoundGen:
    def __init__(self):
        self.sample_rate = 44100
        pygame.mixer.init(frequency=self.sample_rate, size=-16, channels=1)
    
    def make_sound(self, freq, duration, vol=0.5):
        try:
            n_samples = int(self.sample_rate * duration)
            buf = array.array('h', [0] * n_samples)
            amplitude = int(32767 * vol)
            period = self.sample_rate // freq
            for i in range(n_samples):
                buf[i] = amplitude if (i // (period // 2)) % 2 else -amplitude
            return pygame.mixer.Sound(buffer=buf)
        except:
            return None

# --- PARTICLE SYSTEM (EXPLOSIONS) ---
class Particle:
    def __init__(self, x, y):
        self.pos = pygame.math.Vector2(x, y)
        # Random burst velocity
        angle = random.uniform(0, 6.28)
        speed = random.uniform(2, 6)
        self.vel = pygame.math.Vector2(math.cos(angle)*speed, math.sin(angle)*speed)
        self.life = random.randint(20, 40)
        self.size = random.randint(3, 6)

    def update(self):
        self.pos += self.vel
        self.life -= 1
        self.size = max(0, self.size - 0.1)

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.rect(surface, BLACK, (self.pos.x, self.pos.y, self.size, self.size))

# --- GAME OBJECTS ---

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
            pygame.draw.circle(surface, BLACK, (int(self.pos.x), int(self.pos.y)), 15)

class KeyItem:
    def __init__(self, x, y):
        self.rect = pygame.Rect(0,0, 20, 20)
        self.rect.center = (x, y)
        self.active = True
        self.float_y = 0
    
    def draw(self, surface):
        if self.active:
            # Simple bobbing animation
            self.float_y += 0.1
            offset = math.sin(self.float_y) * 5
            # Draw Diamond (Rotated Rect)
            center = (self.rect.centerx, self.rect.centery + offset)
            p1 = (center[0], center[1] - 10)
            p2 = (center[0] + 10, center[1])
            p3 = (center[0], center[1] + 10)
            p4 = (center[0] - 10, center[1])
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
        self.alerted = False # Is chasing?

    def update(self, player_pos):
        target = pygame.math.Vector2(self.points[self.current_point_index])
        
        # If alerted, chase the player instead of the waypoint!
        if self.alerted:
            target = player_pos
            self.speed = self.base_speed * 1.5 # Run faster!
        else:
            self.speed = self.base_speed

        direction = target - self.pos
        dist = direction.length()

        # Patrol Logic (Only if not chasing)
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
            if abs(angle_diff) < 35: # Slightly wider vision
                return True
        return False

    def draw(self, surface):
        cone_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        # Color changes if alerted
        color = ALERT_COLOR if self.alerted else VISION_COLOR
        
        angle_rad = math.radians(self.vision_angle)
        left_angle = math.radians(self.vision_angle + 35)
        right_angle = math.radians(self.vision_angle - 35)
        
        p1 = self.pos
        p2 = self.pos + pygame.math.Vector2(math.cos(left_angle), -math.sin(left_angle)) * self.vision_length
        p3 = self.pos + pygame.math.Vector2(math.cos(right_angle), -math.sin(right_angle)) * self.vision_length
        
        pygame.draw.polygon(cone_surface, color, [p1, p2, p3])
        surface.blit(cone_surface, (0,0))
        
        tip = self.pos + pygame.math.Vector2(math.cos(angle_rad), -math.sin(angle_rad)) * 20
        left_wing = self.pos + pygame.math.Vector2(math.cos(angle_rad + 2.5), -math.sin(angle_rad + 2.5)) * 15
        right_wing = self.pos + pygame.math.Vector2(math.cos(angle_rad - 2.5), -math.sin(angle_rad - 2.5)) * 15
        pygame.draw.polygon(surface, RED, [tip, left_wing, right_wing])

# --- LEVEL DATA ---
LEVELS = [
    {
        "id": 1,
        "start": (50, 300),
        "key_pos": (400, 300),
        "goal": (720, 300),
        "enemy_path": [(200, 50), (600, 50), (600, 550), (200, 550)],
        "enemy_speed": 2.5,
        "spots": [(200, 150, "circle"), (600, 150, "circle"), (200, 450, "square"), (600, 450, "square")]
    },
    {
        "id": 2,
        "start": (50, 50),
        "key_pos": (700, 50), # Key is far away
        "goal": (720, 550),
        "enemy_path": [(400, 100), (400, 500), (100, 300), (700, 300)],
        "enemy_speed": 3.0,
        "spots": [(150, 150, "square"), (650, 150, "circle"), (400, 300, "circle"), (650, 450, "square")]
    },
    {
        "id": 3,
        "start": (400, 550),
        "key_pos": (400, 300), # Key in the middle of patrol
        "goal": (400, 50),
        "enemy_path": [(100, 100), (700, 100), (700, 500), (100, 500)],
        "enemy_speed": 4.0,
        "spots": [(200, 200, "square"), (600, 200, "square"), (200, 400, "circle"), (600, 400, "circle")]
    }
]

# --- MAIN GAME ---

async def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Camouflage: Ultimate Edition")
    clock = pygame.time.Clock()
    font_big = pygame.font.SysFont("Arial", 48, bold=True)
    font_small = pygame.font.SysFont("Arial", 24)

    # Sounds
    sound_gen = SoundGen()
    snd_shift = sound_gen.make_sound(440, 0.1) 
    snd_key   = sound_gen.make_sound(660, 0.1)
    snd_win   = sound_gen.make_sound(880, 0.2)
    snd_lose  = sound_gen.make_sound(150, 0.3) 

    # Variables
    state = "MENU"
    current_level_idx = 0
    particles = []
    
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
    while running:
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
                        shifted = False
                        for spot in spots:
                            if player.rect.colliderect(spot.rect):
                                player.shape_type = spot.shape_type
                                shifted = True
                        if shifted and snd_shift: snd_shift.play()

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
            
            # Key Logic
            if key_item.active and player.rect.colliderect(key_item.rect):
                key_item.active = False
                player.has_key = True
                if snd_key: snd_key.play()

            # Win Logic
            if player.rect.colliderect(goal_rect):
                if player.has_key:
                    if snd_win: snd_win.play()
                    state = "LEVEL_DONE"
            
            # Enemy AI & Line of Sight
            seen = enemy.can_see(player)
            safe_spot = False
            for spot in spots:
                dist = player.pos.distance_to(pygame.math.Vector2(spot.rect.center))
                if dist < 20 and player.shape_type == spot.shape_type:
                    safe_spot = True
            
            is_moving = any([keys[pygame.K_LEFT], keys[pygame.K_RIGHT], keys[pygame.K_UP], keys[pygame.K_DOWN]])
            
            # Smart AI State
            if seen and (is_moving or not safe_spot):
                enemy.alerted = True # START CHASE
            else:
                enemy.alerted = False
            
            enemy.update(player.pos)

            # Caught Logic (Touching Enemy)
            if player.rect.colliderect(enemy.pos.x - 10, enemy.pos.y - 10, 20, 20) or (enemy.alerted and player.rect.distance_to(enemy.pos) < 25):
                if snd_lose: snd_lose.play()
                # SPAWN PARTICLES
                for _ in range(50):
                    particles.append(Particle(player.pos.x, player.pos.y))
                state = "GAME_OVER"

        # Update Particles (Even in Game Over)
        for p in particles[:]:
            p.update()
            if p.life <= 0: particles.remove(p)

        # --- DRAWING ---
        screen.fill(WHITE)

        if state == "MENU":
            title = font_big.render("CAMOUFLAGE", True, BLACK)
            sub = font_small.render("Ultimate Edition", True, RED)
            inst = font_small.render("Collect Blue Key -> Unlock Green Door", True, BLACK)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 200))
            screen.blit(sub, (WIDTH//2 - sub.get_width()//2, 260))
            screen.blit(inst, (WIDTH//2 - inst.get_width()//2, 400))
            screen.blit(font_small.render("[SPACE] to Start", True, BLACK), (WIDTH//2 - 80, 500))

        elif state == "PLAYING" or state == "GAME_OVER":
            # Draw Goal (Red if locked, Green if open)
            goal_color = GREEN if player.has_key else RED
            pygame.draw.rect(screen, goal_color, goal_rect)
            
            # Draw Objects
            for spot in spots: spot.draw(screen)
            key_item.draw(screen)
            enemy.draw(screen)
            
            # Only draw player if alive
            if state == "PLAYING":
                player.draw(screen)
            
            # Draw Particles
            for p in particles: p.draw(screen)

            if state == "GAME_OVER":
                 # Draw text over the chaos
                msg = font_big.render("CAUGHT!", True, RED)
                screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 - 50))
                sub = font_small.render("Press SPACE", True, BLACK)
                screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 10))
            
            # HUD
            if not player.has_key:
                txt = font_small.render("Find the Key!", True, BLUE)
                screen.blit(txt, (20, 20))
            else:
                txt = font_small.render("Escape!", True, GREEN)
                screen.blit(txt, (20, 20))

        elif state == "LEVEL_DONE":
            screen.fill(GREEN)
            msg = font_big.render("ESCAPED!", True, WHITE)
            sub = font_small.render("Press SPACE for Next Level", True, WHITE)
            screen.blit(msg, (WIDTH//2 - msg.get_width()//2, 250))
            screen.blit(sub, (WIDTH//2 - sub.get_width()//2, 350))
        
        elif state == "ALL_COMPLETE":
            screen.fill(BLACK)
            msg = font_big.render("YOU ARE A MASTER", True, GREEN)
            screen.blit(msg, (WIDTH//2 - msg.get_width()//2, 300))

        pygame.display.flip()
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())