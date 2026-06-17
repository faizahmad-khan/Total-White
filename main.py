"""
Camouflage: Advanced Stealth Game
==================================
A stealth-based puzzle game built with Pygame where players navigate
through enemy territory while avoiding detection by changing shape
to blend in with the environment.
"""

import pygame
import asyncio
import traceback

from config import (
    WIDTH, HEIGHT, FPS, WHITE, BLACK, RED,
    COLLISION_DISTANCE, SAFE_SPOT_DISTANCE, TELEPORTER_COOLDOWN,
    NOISE_DECOY_RADIUS,
    THREAT_MAX, THREAT_DETECTION_GAIN
)
from entities import Decoy
from levels import LEVELS, load_level
from score import ScoreTracker
from ui import draw_menu, draw_gameplay, draw_hud, draw_level_done, draw_all_complete


async def main():
    """Main game loop handling state transitions, input, updates, and rendering."""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Camouflage: Advanced Stealth Game")
    clock = pygame.time.Clock()

    # Fonts (passed as a tuple to UI functions)
    fonts = (
        pygame.font.SysFont("Arial", 48, bold=True),
        pygame.font.SysFont("Arial", 32, bold=True),
        pygame.font.SysFont("Arial", 24),
        pygame.font.SysFont("Arial", 18),
    )

    score_tracker = ScoreTracker()

    state = "MENU"
    current_level_idx = 0
    active_decoys = []
    level_timer = 0
    noise_points = []

    player, enemies, key_item, spots, teleporters, goal_rect, walls = load_level(0)

    running = True

    try:
        while running:
            clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if state == "MENU":
                        if event.key == pygame.K_SPACE:
                            state = "PLAYING"
                            current_level_idx = 0
                            active_decoys = []
                            level_timer = 0
                            noise_points = []
                            score_tracker.reset()
                            player, enemies, key_item, spots, teleporters, goal_rect, walls = load_level(current_level_idx)
                            score_tracker.start_level(player.decoys_left)

                    elif state == "PLAYING":
                        if event.key == pygame.K_SPACE:
                            for spot in spots:
                                if player.rect.colliderect(spot.rect):
                                    player.shape_type = spot.shape_type

                        if event.key == pygame.K_z:
                            if player.decoys_left > 0:
                                player.decoys_left -= 1
                                decoy = Decoy(player.pos.x, player.pos.y)
                                active_decoys.append(decoy)
                                noise_points.append((pygame.math.Vector2(decoy.pos), NOISE_DECOY_RADIUS, 0))

                    elif state in ["GAME_OVER", "LEVEL_DONE"]:
                        if event.key == pygame.K_SPACE:
                            active_decoys = []
                            level_timer = 0
                            noise_points = []
                            if state == "LEVEL_DONE":
                                current_level_idx += 1
                                if current_level_idx >= len(LEVELS):
                                    state = "ALL_COMPLETE"
                                else:
                                    player, enemies, key_item, spots, teleporters, goal_rect, walls = load_level(current_level_idx)
                                    score_tracker.start_level(player.decoys_left)
                                    state = "PLAYING"
                            else:
                                score_tracker.record_death()
                                player, enemies, key_item, spots, teleporters, goal_rect, walls = load_level(current_level_idx)
                                score_tracker.start_level(player.decoys_left)
                                state = "PLAYING"

                    elif state == "ALL_COMPLETE":
                        if event.key == pygame.K_SPACE:
                            state = "MENU"

            # --- UPDATES ---
            if state == "PLAYING":
                keys = pygame.key.get_pressed()
                player.move(keys, walls)
                level_timer += 1

                for d in active_decoys[:]:
                    d.update()
                    if d.life <= 0:
                        active_decoys.remove(d)

                for t_pair in teleporters:
                    t1, t2 = t_pair
                    t1.update()
                    t2.update()

                    if player.rect.colliderect(t1.rect) and t1.cooldown == 0:
                        player.pos = pygame.math.Vector2(t2.rect.center)
                        t2.cooldown = TELEPORTER_COOLDOWN
                    elif player.rect.colliderect(t2.rect) and t2.cooldown == 0:
                        player.pos = pygame.math.Vector2(t1.rect.center)
                        t1.cooldown = TELEPORTER_COOLDOWN

                if key_item.active and player.rect.colliderect(key_item.rect):
                    key_item.active = False
                    player.has_key = True

                if player.rect.colliderect(goal_rect):
                    if player.has_key:
                        score_tracker.finish_level(player.decoys_left)
                        state = "LEVEL_DONE"

                is_moving = any([keys[pygame.K_LEFT], keys[pygame.K_RIGHT],
                                 keys[pygame.K_UP], keys[pygame.K_DOWN]])
                safe_spot = False
                for spot in spots:
                    dist = player.pos.distance_to(pygame.math.Vector2(spot.rect.center))
                    if dist < SAFE_SPOT_DISTANCE and player.shape_type == spot.shape_type:
                        safe_spot = True

                noise_radius, noise_emitted = player.get_noise(is_moving)
                if noise_emitted:
                    noise_points.append((pygame.math.Vector2(player.pos), noise_radius, 0))

                for np_tuple in noise_points[:]:
                    np, nr, age = np_tuple
                    dist_to_enemy = 0
                    for enemy in enemies:
                        dist_to_enemy = max(dist_to_enemy, enemy.pos.distance_to(np))
                    if dist_to_enemy > nr + NOISE_ENEMY_HEAR_RADIUS:
                        age += 1
                        if age >= 60:
                            noise_points.remove(np_tuple)

                for enemy in enemies:
                    seen = enemy.can_see(player)
                    if seen and (is_moving or not safe_spot):
                        enemy.threat += THREAT_DETECTION_GAIN
                        if enemy.threat > THREAT_MAX:
                            enemy.threat = THREAT_MAX

                    enemy.update(player.pos, active_decoys, noise_points)

                    dist_to_enemy = player.pos.distance_to(enemy.pos)
                    if dist_to_enemy < COLLISION_DISTANCE:
                        state = "GAME_OVER"

            # --- DRAWING ---
            screen.fill(WHITE)

            if state == "MENU":
                draw_menu(screen, fonts)

            elif state in ("PLAYING", "GAME_OVER"):
                draw_gameplay(screen, fonts, player, enemies, spots,
                              teleporters, key_item, active_decoys,
                              walls, goal_rect, state, noise_points)
                draw_hud(screen, fonts, current_level_idx, level_timer,
                         player, score_tracker)

            elif state == "LEVEL_DONE":
                draw_level_done(screen, fonts, current_level_idx, score_tracker)

            elif state == "ALL_COMPLETE":
                draw_all_complete(screen, fonts, score_tracker)

            pygame.display.flip()
            await asyncio.sleep(0)

        pygame.quit()

    except Exception as e:
        print(f"CRASH CAUGHT: {e}")
        traceback.print_exc()
        screen.fill(BLACK)
        font_small = fonts[2]
        err_txt = font_small.render("ERROR!", True, RED)
        err_msg = font_small.render(str(e)[:60], True, WHITE)
        screen.blit(err_txt, (10, 10))
        screen.blit(err_msg, (10, 50))
        hint_msg = font_small.render("Press ESC or close window to exit.", True, WHITE)
        screen.blit(hint_msg, (10, 90))
        pygame.display.flip()

        error_running = True
        while error_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    error_running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    error_running = False
            await asyncio.sleep(0)

        pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())