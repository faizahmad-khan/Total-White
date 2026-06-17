"""UI rendering functions for menus, HUD, and transition screens."""

import pygame

from config import (
    WIDTH, HEIGHT, FPS,
    WHITE, BLACK, RED, GREEN, BLUE, GOLD, GRAY, DARK_GRAY, ORANGE,
)
from levels import LEVELS


def draw_menu(screen, fonts):
    """Render the main menu screen."""
    font_big, font_med, font_small, font_tiny = fonts

    txt_title = font_big.render("CAMOUFLAGE", True, BLACK)
    screen.blit(txt_title, (WIDTH // 2 - txt_title.get_width() // 2, 140))

    txt_sub = font_small.render("Advanced Stealth Game", True, RED)
    screen.blit(txt_sub, (WIDTH // 2 - txt_sub.get_width() // 2, 200))

    pygame.draw.line(screen, GRAY, (200, 240), (600, 240), 2)

    txt_levels = font_small.render(f"{len(LEVELS)} Levels | Score System | Wall Obstacles", True, DARK_GRAY)
    screen.blit(txt_levels, (WIDTH // 2 - txt_levels.get_width() // 2, 260))

    controls_header = font_med.render("Controls", True, BLACK)
    screen.blit(controls_header, (WIDTH // 2 - controls_header.get_width() // 2, 320))

    control_lines = [
        "Arrow Keys = Move",
        "SHIFT = Sprint  |  SPACE = Change Shape",
        "Z = Deploy Decoy  |  Portals = Teleport",
    ]
    for i, line in enumerate(control_lines):
        txt = font_tiny.render(line, True, DARK_GRAY)
        screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, 365 + i * 28))

    if (pygame.time.get_ticks() // 500) % 2 == 0:
        txt_start = font_med.render("Press SPACE to Start", True, BLUE)
        screen.blit(txt_start, (WIDTH // 2 - txt_start.get_width() // 2, 490))


def draw_gameplay(screen, fonts, player, enemies, spots, teleporters,
                  key_item, active_decoys, walls, goal_rect, state,
                  noise_points=None):
    """Render the playing field (used for both PLAYING and GAME_OVER states)."""
    font_big, _font_med, font_small, font_tiny = fonts

    if noise_points is None:
        noise_points = []

    # Draw walls first (background layer)
    for wall in walls:
        wall.draw(screen)

    # Goal zone
    goal_color = GREEN if player.has_key else RED
    pygame.draw.rect(screen, goal_color, goal_rect)
    pygame.draw.rect(screen, BLACK, goal_rect, 2)

    if player.has_key:
        exit_txt = font_tiny.render("EXIT", True, BLACK)
        screen.blit(exit_txt, (goal_rect.centerx - exit_txt.get_width() // 2,
                                goal_rect.centery - exit_txt.get_height() // 2))

    for spot in spots:
        spot.draw(screen)

    for t_pair in teleporters:
        t_pair[0].draw(screen)
        t_pair[1].draw(screen)

    key_item.draw(screen)

    for d in active_decoys:
        d.draw(screen)

    # Draw all vision cone fills on one shared alpha surface to reduce allocations.
    cone_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for enemy in enemies:
        enemy.draw_vision_cone(cone_overlay)
    screen.blit(cone_overlay, (0, 0))

    for enemy in enemies:
        enemy.draw(screen)

    if state == "PLAYING" or state == "GAME_OVER":
        ping_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for (np, nr, age) in noise_points:
            alpha = max(0, 255 - age * 4)
            pygame.draw.circle(ping_surface, (255, 200, 0, alpha // 6), (int(np.x), int(np.y)), int(nr))
            pygame.draw.circle(ping_surface, (255, 165, 0, alpha // 3), (int(np.x), int(np.y)), int(nr * 0.7), 1)
        screen.blit(ping_surface, (0, 0))

    if state == "PLAYING":
        player.draw(screen)

    if state == "GAME_OVER":
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))

        txt_caught = font_big.render("CAUGHT!", True, RED)
        screen.blit(txt_caught, (WIDTH // 2 - txt_caught.get_width() // 2, HEIGHT // 2 - 60))
        txt_restart = font_small.render("Press SPACE to Retry", True, WHITE)
        screen.blit(txt_restart, (WIDTH // 2 - txt_restart.get_width() // 2, HEIGHT // 2 + 10))


def draw_hud(screen, fonts, current_level_idx, level_timer, player, score_tracker):
    """Render the in-game HUD overlay."""
    _font_big, _font_med, _font_small, font_tiny = fonts

    level_data = LEVELS[current_level_idx]
    level_name = level_data.get("name", f"Level {level_data['id']}")
    hud_level = font_tiny.render(f"Level {level_data['id']}: {level_name}", True, BLACK)
    screen.blit(hud_level, (10, 8))

    elapsed_sec = level_timer // FPS
    elapsed_min = elapsed_sec // 60
    elapsed_sec = elapsed_sec % 60
    timer_txt = font_tiny.render(f"Time: {elapsed_min:02d}:{elapsed_sec:02d}", True, BLACK)
    screen.blit(timer_txt, (WIDTH - timer_txt.get_width() - 10, 8))

    decoy_txt = font_tiny.render(f"Decoys: {player.decoys_left}", True, BLACK)
    screen.blit(decoy_txt, (10, 574))

    key_status = "KEY" if player.has_key else "Find Key"
    key_color = GOLD if player.has_key else GRAY
    key_txt = font_tiny.render(key_status, True, key_color)
    screen.blit(key_txt, (WIDTH - key_txt.get_width() - 10, 574))

    if score_tracker.total_deaths > 0:
        death_txt = font_tiny.render(f"Deaths: {score_tracker.total_deaths}", True, RED)
        screen.blit(death_txt, (WIDTH // 2 - death_txt.get_width() // 2, 574))


def draw_level_done(screen, fonts, current_level_idx, score_tracker):
    """Render the level-complete transition screen."""
    font_big, _font_med, font_small, _font_tiny = fonts

    screen.fill(WHITE)

    txt_escaped = font_big.render("LEVEL CLEAR!", True, GREEN)
    screen.blit(txt_escaped, (WIDTH // 2 - txt_escaped.get_width() // 2, 120))

    level_data = LEVELS[current_level_idx]
    level_name = level_data.get("name", f"Level {level_data['id']}")
    name_txt = font_small.render(level_name, True, DARK_GRAY)
    screen.blit(name_txt, (WIDTH // 2 - name_txt.get_width() // 2, 185))

    pygame.draw.line(screen, GRAY, (200, 220), (600, 220), 2)

    if score_tracker.level_times:
        last_time = score_tracker.level_times[-1]
        time_txt = font_small.render(f"Level Time: {last_time:.1f}s", True, BLACK)
        screen.blit(time_txt, (WIDTH // 2 - time_txt.get_width() // 2, 250))

    progress = f"Level {current_level_idx + 1} / {len(LEVELS)} Complete"
    prog_txt = font_small.render(progress, True, BLUE)
    screen.blit(prog_txt, (WIDTH // 2 - prog_txt.get_width() // 2, 300))

    if current_level_idx + 1 < len(LEVELS):
        next_txt = font_small.render("Press SPACE for Next Level", True, BLACK)
    else:
        next_txt = font_small.render("Press SPACE to See Final Score!", True, GOLD)
    screen.blit(next_txt, (WIDTH // 2 - next_txt.get_width() // 2, 400))


def draw_all_complete(screen, fonts, score_tracker):
    """Render the final victory / scoring screen."""
    font_big, _font_med, font_small, _font_tiny = fonts

    screen.fill(BLACK)

    txt_victory = font_big.render("MISSION COMPLETE", True, GOLD)
    screen.blit(txt_victory, (WIDTH // 2 - txt_victory.get_width() // 2, 60))

    pygame.draw.line(screen, GRAY, (150, 120), (650, 120), 2)

    total_time = score_tracker.get_total_time()
    final_score = score_tracker.get_final_score()
    rank = score_tracker.get_rank()

    stats = [
        (f"Total Time: {total_time:.1f}s", WHITE),
        (f"Decoys Used: {score_tracker.total_decoys_used}", WHITE),
        (f"Times Caught: {score_tracker.total_deaths}", RED if score_tracker.total_deaths > 0 else WHITE),
        (f"Levels Cleared: {len(LEVELS)}", GREEN),
    ]

    for i, (text, color) in enumerate(stats):
        txt = font_small.render(text, True, color)
        screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, 160 + i * 40))

    pygame.draw.line(screen, GRAY, (200, 330), (600, 330), 2)

    score_txt = font_big.render(f"Score: {final_score}", True, GOLD)
    screen.blit(score_txt, (WIDTH // 2 - score_txt.get_width() // 2, 350))

    rank_colors = {"S": GOLD, "A": GREEN, "B": BLUE, "C": ORANGE, "D": RED}
    rank_color = rank_colors.get(rank, WHITE)
    rank_txt = font_big.render(f"Rank: {rank}", True, rank_color)
    screen.blit(rank_txt, (WIDTH // 2 - rank_txt.get_width() // 2, 420))

    restart_txt = font_small.render("Press SPACE to Return to Menu", True, GRAY)
    screen.blit(restart_txt, (WIDTH // 2 - restart_txt.get_width() // 2, 530))
