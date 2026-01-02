import pygame
import sys
import math
import asyncio
import array

# --- CONFIGURATION ---
WIDTH, HEIGHT = 800, 600
WHITE = (240, 240, 240)
BLACK = (20, 20, 20)
RED   = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE  = (50, 50, 200)
VISION_COLOR = (255, 0, 0, 60)

# --- SOUND GENERATOR (No files needed!) ---
class SoundGen:
    def __init__(self):
        self.sample_rate = 44100
        pygame.mixer.init(frequency=self.sample_rate, size=-16, channels=1)
    
    def make_sound(self, freq, duration, vol=0.5):
        try:
            # Generate a square wave (retro 8-bit sound)
            n_samples = int(self.sample_rate * duration)
            buf = array.array('h', [0] * n_samples)
            amplitude = int(32767 * vol)
            period = self.sample_rate // freq
            
            for i in range(n_samples):
                # 1 if first half of period, -1 if second
                buf[i] = amplitude if (i // (period // 2)) % 2 else -amplitude
                
            return pygame.mixer.Sound(buffer=buf)
        except Exception as e:
            print("Sound generation failed (web audio might be strict):", e)
            return None

# --- CLASSES ---

class Player:
    def __init__(self, start_pos):
        self.pos = pygame.math.Vector2(start_pos)
        self.rect = pygame.Rect(0, 0, 30, 30)
        self.rect.center = self.pos
        self.shape_type = "square"
        self.speed = 4
    
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
        self.speed = speed
        self.vision_length = 160
        self.vision_angle = 0 

    def update(self):
        target = pygame.math.Vector2(self.points[self.current_point_index])
        direction = target - self.pos
        dist = direction.length()

        if dist < 5:
            self.current_point_index = (self.current_point_index + 1) % len(self.points)
        else:
            direction = direction.normalize()
            self.pos += direction * self.speed
            self.vision_angle = math.degrees(math.atan2(-direction.y, direction.x))

    def can_see(self, player):
        vec_to_player = player.pos - self.pos
        dist = vec_to_player.length()
        if dist < self.vision_length:
            angle_to_player = math.degrees(math.atan2(-vec_to_player.y, vec_to_player.x))
            angle_diff = (angle_to_player - self.vision_angle + 180) % 360 - 180
            if abs(angle_diff) < 30: 
                return True
        return False

    def draw(self, surface):
        cone_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        angle_rad = math.radians(self.vision_angle)
        left_angle = math.radians(self.vision_angle + 30)
        right_angle = math.radians(self.vision_angle - 30)
        
        p1 = self.pos
        p2 = self.pos + pygame.math.Vector2(math.cos(left_angle), -math.sin(left_angle)) * self.vision_length
        p3 = self.pos + pygame.math.Vector2(math.cos(right_angle), -math.sin(right_angle)) * self.vision_length
        
        pygame.draw.polygon(cone_surface, VISION_COLOR, [p1, p2, p3])
        surface.blit(cone_surface, (0,0))
        
        # Enemy Body
        tip = self.pos + pygame.math.Vector2(math.cos(angle_rad), -math.sin(angle_rad)) * 20
        left_wing = self.pos + pygame.math.Vector2(math.cos(angle_rad + 2.5), -math.sin(angle_rad + 2.5)) * 15
        right_wing = self.pos + pygame.math.Vector2(math.cos(angle_rad - 2.5), -math.sin(angle_rad - 2.5)) * 15
        pygame.draw.polygon(surface, RED, [tip, left_wing, right_wing])

# --- LEVEL DATA ---
LEVELS = [
    {
        "id": 1,
        "start": (50, 300),
        "goal": (720, 300),
        "enemy_path": [(200, 50), (600, 50), (600, 550), (200, 550)],
        "enemy_speed": 2.5,
        "spots": [
            (200, 150, "circle"), (400, 300, "square"), (600, 150, "circle"),
            (200, 450, "square"), (600, 450, "square")
        ]
    },
    {
        "id": 2,
        "start": (50, 50),
        "goal": (720, 550),
        "enemy_path": [(400, 100), (400, 500), (100, 300), (700, 300)], # Criss-cross
        "enemy_speed": 3.0,
        "spots": [
            (150, 150, "square"), (650, 150, "circle"),
            (400, 300, "circle"),
            (150, 450, "circle"), (650, 450, "square")
        ]
    },
    {
        "id": 3,
        "start": (400, 550),
        "goal": (400, 50),
        "enemy_path": [(100, 100), (700, 100), (700, 500), (100, 500), (100, 300), (700, 300)],
        "enemy_speed": 4.5, # Very fast!
        "spots": [
            (200, 200, "square"), (600, 200, "square"),
            (200, 400, "circle"), (600, 400, "circle")
        ]
    }
]

# --- MAIN GAME ---

async def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Camouflage")
    clock = pygame.time.Clock()
    font_big = pygame.font.SysFont("Arial", 48, bold=True)
    font_small = pygame.font.SysFont("Arial", 24)

    # Initialize Sound
    sound_gen = SoundGen()
    snd_shift = sound_gen.make_sound(440, 0.1) # A4 beep
    snd_win = sound_gen.make_sound(880, 0.2)   # High beep
    snd_lose = sound_gen.make_sound(150, 0.3)  # Low buzz

    # Game State Variables
    state = "MENU" # MENU, PLAYING, LEVEL_DONE, GAME_OVER, ALL_COMPLETE
    current_level_idx = 0
    
    # Load Level Function
    def load_level(idx):
        data = LEVELS[idx]
        p = Player(data["start"])
        e = Enemy(data["enemy_path"], speed=data["enemy_speed"])
        s_list = []
        for s_data in data["spots"]:
            s_list.append(HidingSpot(s_data[0], s_data[1], s_data[2]))
        g_rect = pygame.Rect(0, 0, 60, 60)
        g_rect.center = data["goal"]
        return p, e, s_list, g_rect

    player, enemy, spots, goal_rect = load_level(0)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # --- INPUT HANDLING ---
            if event.type == pygame.KEYDOWN:
                if state == "MENU":
                    if event.key == pygame.K_SPACE:
                        state = "PLAYING"
                        current_level_idx = 0
                        player, enemy, spots, goal_rect = load_level(current_level_idx)
                
                elif state == "PLAYING":
                    if event.key == pygame.K_SPACE:
                        shifted = False
                        for spot in spots:
                            if player.rect.colliderect(spot.rect):
                                player.shape_type = spot.shape_type
                                shifted = True
                        if shifted and snd_shift:
                            snd_shift.play()

                elif state in ["GAME_OVER", "LEVEL_DONE"]:
                    if event.key == pygame.K_SPACE:
                        if state == "LEVEL_DONE":
                            current_level_idx += 1
                            if current_level_idx >= len(LEVELS):
                                state = "ALL_COMPLETE"
                            else:
                                player, enemy, spots, goal_rect = load_level(current_level_idx)
                                state = "PLAYING"
                        else:
                            # Game Over -> Restart Level
                            player, enemy, spots, goal_rect = load_level(current_level_idx)
                            state = "PLAYING"
                
                elif state == "ALL_COMPLETE":
                    if event.key == pygame.K_SPACE:
                        state = "MENU"

        # --- UPDATES ---
        if state == "PLAYING":
            keys = pygame.key.get_pressed()
            player.move(keys)
            enemy.update()

            # Win Condition
            if player.rect.colliderect(goal_rect):
                if snd_win: snd_win.play()
                state = "LEVEL_DONE"

            # Lose Condition
            if enemy.can_see(player):
                is_moving = any([keys[pygame.K_LEFT], keys[pygame.K_RIGHT], keys[pygame.K_UP], keys[pygame.K_DOWN]])
                safe_spot = False
                for spot in spots:
                    dist = player.pos.distance_to(pygame.math.Vector2(spot.rect.center))
                    if dist < 20 and player.shape_type == spot.shape_type:
                        safe_spot = True
                
                if is_moving or not safe_spot:
                    if snd_lose: snd_lose.play()
                    state = "GAME_OVER"

        # --- DRAWING ---
        screen.fill(WHITE)

        if state == "MENU":
            # Draw Title Screen
            title = font_big.render("CAMOUFLAGE", True, BLACK)
            sub = font_small.render("Press SPACE to Start", True, RED)
            inst = font_small.render("Arrows to Move | Space to Hide inside Shapes", True, BLACK)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 200))
            screen.blit(sub, (WIDTH//2 - sub.get_width()//2, 300))
            screen.blit(inst, (WIDTH//2 - inst.get_width()//2, 400))

        elif state == "PLAYING":
            pygame.draw.rect(screen, GREEN, goal_rect)
            for spot in spots: spot.draw(screen)
            enemy.draw(screen)
            player.draw(screen)
            
            # Draw Level UI
            lvl_text = font_small.render(f"Level {current_level_idx + 1}", True, BLACK)
            screen.blit(lvl_text, (20, 20))

        elif state == "GAME_OVER":
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            screen.blit(overlay, (0,0))
            msg = font_big.render("CAUGHT!", True, RED)
            sub = font_small.render("Press SPACE to Try Again", True, WHITE)
            screen.blit(msg, (WIDTH//2 - msg.get_width()//2, 250))
            screen.blit(sub, (WIDTH//2 - sub.get_width()//2, 350))

        elif state == "LEVEL_DONE":
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(WHITE)
            screen.blit(overlay, (0,0))
            msg = font_big.render("ESCAPED!", True, GREEN)
            sub = font_small.render("Press SPACE for Next Level", True, BLACK)
            screen.blit(msg, (WIDTH//2 - msg.get_width()//2, 250))
            screen.blit(sub, (WIDTH//2 - sub.get_width()//2, 350))
        
        elif state == "ALL_COMPLETE":
            screen.fill(BLACK)
            msg = font_big.render("YOU WIN!", True, GREEN)
            sub = font_small.render("You beat all levels. Thanks for playing!", True, WHITE)
            restart = font_small.render("Press SPACE to Menu", True, WHITE)
            screen.blit(msg, (WIDTH//2 - msg.get_width()//2, 200))
            screen.blit(sub, (WIDTH//2 - sub.get_width()//2, 300))
            screen.blit(restart, (WIDTH//2 - restart.get_width()//2, 400))

        pygame.display.flip()
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())