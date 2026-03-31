import pygame
import random
import os
import math

pygame.init()

# --- EKRAN BAŞLATMA ---
screen_width = 360
screen_height = 640
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Jungle Jumper")

# --- SKIN SİSTEMİ ---
BASE_DIR = os.path.dirname(__file__)
def asset_path(path):
    return os.path.join(BASE_DIR, path)

def load_skins():
    def load_sprite(path):
        image = pygame.image.load(asset_path(path)).convert_alpha()
        return image
    
    return {
        "bunny": {
            "jump_color": (255, 255, 255),
            "sprites": {
                "right": load_sprite("skins/bunny/bunny_right.png"),
                "left": load_sprite("skins/bunny/bunny_left.png"),
                "right_dead": load_sprite("skins/bunny/bunny_right_gameover.png"),
                "left_dead": load_sprite("skins/bunny/bunny_left_gameover.png"),
            },
            "price": 0
        },
    }

# --- VARLIK YÜKLEME ---
def initialize_assets():
    global COIN_TYPES, bubble_img, bubble_active_img, apple_img
    COIN_TYPES[1]["image"] = pygame.image.load(asset_path("assets/1gold_apple.png")).convert_alpha()
    COIN_TYPES[2]["image"] = pygame.image.load(asset_path("assets/2gold_cherry.png")).convert_alpha()
    COIN_TYPES[3]["image"] = pygame.image.load(asset_path("assets/3gold_grape.png")).convert_alpha()
    bubble_img = pygame.image.load(asset_path("assets/bubble.png")).convert_alpha()
    apple_img = COIN_TYPES[1]["image"]
    bubble_active_img = pygame.image.load(asset_path("assets/bubble_active.png")).convert_alpha()

# --- HIGH SCORE ---
def load_high_score():
    if os.path.exists("highscore.txt"):
        try:
            with open("highscore.txt", "r") as f:
                return int(f.read())
        except:
            return 0
    return 0

def save_high_score(new_score):
    with open("highscore.txt", "w") as f:
        f.write(str(new_score))

# --- ALTIN SİSTEMİ ---
def load_coins():
    if os.path.exists("coins.txt"):
        try:
            with open("coins.txt", "r") as f:
                return int(f.read())
        except:
            return 0
    return 0

def save_coins(amount):
    with open("coins.txt", "w") as f:
        f.write(str(amount))

# --- OYUN DEĞİŞKENLERİ ---
score = 0
high_score = load_high_score()
game_over = False
show_game_over_ui = False
game_over_start_time = 0
game_state = "start"
start_animation_time = 0
skins = load_skins()
current_skin = "bunny" 
total_coins = load_coins()
coins = []
floating_texts = []
coin_spawn_ready = False
coin_spawn_side = None
bubble = None
bubble_active = False
invincible_until = 0
bubble_img = None
bubble_active_img = None
apple_img = None

COIN_TYPES = {
    1: {"image": None, "value": 1, "text_color": (161, 235, 52)},
    2: {"image": None, "value": 2, "text_color": (235, 52, 52)},
    3: {"image": None, "value": 3, "text_color": (202, 38, 235)}
}
coin_size = 32

# Varlıkları yükle
initialize_assets()

# --- FONKSİYONLAR ---
def spawn_coin(side, score):
    coins.clear()
    if score < 1:
        return
    if score <= 7:
        ctype = 1
    elif score <= 15:
        ctype = 2
    else:
        ctype = 3

    if side == "left":
        x = 50
    else:
        x = screen_width - 50 - coin_size

    y_min = spike_height + 90
    y_max = screen_height - spike_height - 120 - coin_size
    y = random.randint(y_min, y_max)

    coins.append({"x": x, "y": y, "type": ctype, "base_y": y, "phase": random.uniform(0, 2 * math.pi)})

def draw_coins():
    for c in coins:
        offset_y = math.sin(pygame.time.get_ticks() / 350.0 + c["phase"]) * 4  
        screen.blit(COIN_TYPES[c["type"]]["image"], (int(c["x"]), int(c["y"] + offset_y)))

def check_coin_collision():
    global total_coins, coin_spawn_ready
    player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
    for c in coins[:]:
        coin_rect = pygame.Rect(c["x"], c["y"], coin_size, coin_size)
        if player_rect.colliderect(coin_rect):
            value = COIN_TYPES[c["type"]]["value"]
            total_coins += value
            floating_texts.append({
                "x": c["x"],
                "y": c["y"],
                "text": f"+{value}",
                "color": COIN_TYPES[c["type"]]["text_color"],
                "alpha": 255,
                "vy": -0.5
            })
            coins.remove(c)
            coin_spawn_ready = True

def update_floating_texts():
    for t in floating_texts[:]:
        t["y"] += t["vy"]
        t["alpha"] -= 3
        if t["alpha"] <= 0:
            floating_texts.remove(t)

def draw_floating_texts():
    for t in floating_texts:
        text_surface = font_40.render(t["text"], True, t["color"])
        text_surface.set_alpha(t["alpha"])
        outline_surface = font_40.render(t["text"], True, (0, 0, 0))
        outline_surface.set_alpha(t["alpha"])
        for dx in (-1, 1):
            for dy in (-1, 1):
                screen.blit(outline_surface, (t["x"] + dx, t["y"] + dy))
        screen.blit(text_surface, (t["x"], t["y"]))

# --- BALONCUK ---
def spawn_bubble(side):
    global bubble
    if bubble or bubble_active or random.randint(1, 8) != 1:
        return
    if side == "left":
        x = 80
    else:
        x = screen_width - 80 - 32
    y_min = spike_height + 90
    y_max = screen_height - spike_height - 160
    y = random.randint(y_min, y_max)
    bubble = {"x": x, "y": y, "base_y": y, "phase": random.uniform(0, 2 * math.pi)}

def draw_bubble():
    if bubble:
        offset_y = math.sin(pygame.time.get_ticks() / 350.0 + bubble["phase"]) * 4  
        screen.blit(pygame.transform.scale(bubble_img, (player_width + 10, player_height + 10)), (int(bubble["x"]), int(bubble["y"] + offset_y)))
    if bubble_active:
        screen.blit(pygame.transform.scale(bubble_active_img, (player_width + 27, player_height + 25)), (player_x - 10, player_y - 8))

def check_bubble_collision():
    global bubble_active, bubble
    if bubble:
        player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
        bubble_rect = pygame.Rect(bubble["x"], bubble["y"], 32, 32)
        if player_rect.colliderect(bubble_rect):
            bubble_active = True
            bubble = None

# --- FONTLAR ---
font = pygame.font.SysFont("Comic Sans MS", 100, bold=True)
score_font = pygame.font.SysFont("Comic Sans MS", 100, bold=True)
font_40 = pygame.font.SysFont("Roboto Mono Thin", 40, bold=False)
font_30 = pygame.font.SysFont("Roboto Mono Thin", 30, bold=False)

spike_height = 50
SPIKE_HEIGHT = 37
SPIKE_MAX_WIDTH = 35
SPIKE_SPEED = 1.4

def draw_score_text(surface, text, font, pos, text_color, outline_color):
    x, y = pos
    base = font.render(text, True, text_color)
    outline = font.render(text, True, outline_color)
    for dx in range(-4, 6):
        for dy in range(-4, 6):
            if dx != 0 or dy != 0:
                surface.blit(outline, (x + dx, y + dy))
    surface.blit(base, pos)

def draw_text_with_outline(surface, text, font, pos, text_color, outline_color):
    x, y = pos
    base = font.render(text, True, text_color)
    outline = font.render(text, True, outline_color)
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            if dx != 0 or dy != 0:
                surface.blit(outline, (x + dx, y + dy))
    surface.blit(base, pos)

spike_img = pygame.image.load(asset_path("assets/spike.png")).convert_alpha()
background_img = pygame.image.load(asset_path("assets/background.png")).convert_alpha()
spike_up_img = pygame.image.load(asset_path("assets/spike_up.png")).convert_alpha()
spike_down_img = pygame.image.load(asset_path("assets/spike_down.png")).convert_alpha()

clock = pygame.time.Clock()
FPS = 120

player_width = 32
player_height = 32
player_x = (screen_width // 2) - 30
player_y = screen_height // 2
player_color = (175, 0, 0)
player_gameover_color = (0, 0, 0)
player_direction = 1
player_speed = 2
player_velocity = 0
base_player_y = player_y

left_spikes = []
right_spikes = []

def create_spikes_with_gap(count):
    spikes = []
    min_gap = 160
    gap_y = random.randint(0, screen_height - min_gap)
    attempts = 0

    while len(spikes) < count and attempts < 100:
        spike_y_pos = random.randint(spike_height + 30, screen_height - spike_height - 60)
        if spike_y_pos >= gap_y and spike_y_pos <= gap_y + min_gap:
            attempts += 1
            continue
        if not any(abs(spike_y_pos - s["y"]) < SPIKE_HEIGHT for s in spikes):
            spikes.append({
                "y": spike_y_pos,
                "current_width": 0,
                "max_width": SPIKE_MAX_WIDTH,
                "retracting": False
            })
        attempts += 1
    return spikes

def draw_spikes(spikes, spike_x_pos, direction):
    for s in spikes:
        if s.get("retracting", False):
            s["current_width"] -= SPIKE_SPEED
            if s["current_width"] < 0:
                s["current_width"] = 0
        else:
            if s["current_width"] < s["max_width"]:
                s["current_width"] += SPIKE_SPEED
                if s["current_width"] > s["max_width"]:
                    s["current_width"] = s["max_width"]

        width = int(s["current_width"])
        if direction == "right":
            x_pos = spike_x_pos - width + 5
        else:
            x_pos = spike_x_pos - 5

        if width > 0:
            scaled_spike = pygame.transform.scale(spike_img, (width, SPIKE_HEIGHT))
            screen.blit(scaled_spike, (x_pos, int(s["y"])))

    spikes[:] = [s for s in spikes if not (s.get("retracting", False) and s["current_width"] <= 0)]

def check_spike_collision(spikes, x_pos, direction):
    global bubble_active, game_over, player_direction, player_velocity, game_over_start_time
    player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
    for s in spikes:
        w = s["current_width"]
        if w <= 0:
            continue
        collision_width = max(0, w - 4)
        if direction == "right":
            spike_rect = pygame.Rect(int(x_pos - collision_width), int(s["y"]) + 3, int(collision_width), int(SPIKE_HEIGHT - 6))
        else:
            spike_rect = pygame.Rect(int(x_pos), int(s["y"]) + 3, int(collision_width), int(SPIKE_HEIGHT - 6))
        if player_rect.colliderect(spike_rect):
            return True  # Çarpışma var
    return False  # Çarpışma yok

gravity = 0.08
jump_strength = -3.6
# Sekme hızları
death_bounce_top = abs(jump_strength) - 3   
death_bounce_bottom = jump_strength * 2     

bubble_bounce_top = abs(jump_strength) - 3   
bubble_bounce_bottom = jump_strength - 1  

particles = []

def spawn_jump_particles(x, y, color):
    for _ in range(random.randint(20, 24)):
        particles.append({
            "x": x + 5,
            "y": y,
            "size": random.randint(4, 8),
            "color": color,
            "alpha": 225,
            "vel_x": random.uniform(-0.5, 0.5),
            "vel_y": random.uniform(0.5, 0)
        })

def spawn_death_particles(x, y, color):
    for _ in range(random.randint(18, 20)):
        particles.append({
            "x": x,
            "y": y,
            "size": random.randint(8, 10),
            "color": color,
            "alpha": 200,
            "vel_x": random.uniform(-2, 2),
            "vel_y": random.uniform(-2, 2)
        })

def update_particles():
    for p in particles[:]:
        p["x"] += p.get("vel_x", 0)
        p["y"] += p.get("vel_y", 0)
        p["alpha"] -= 3
        if p["alpha"] <= 0:
            particles.remove(p)

def draw_particles(screen):
    for p in particles:
        surface = pygame.Surface((p["size"], p["size"]), pygame.SRCALPHA)
        radius = p["size"] // 2
        center = (radius, radius)
        pygame.draw.circle(surface, (*p["color"], p["alpha"]), center, radius)
        screen.blit(surface, (p["x"], p["y"]))

running = True
while running:
    dt = clock.tick(FPS) / 1000
    update_particles()
    update_floating_texts()
    start_animation_time += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_state == "start":
                    game_state = "playing"
                    player_velocity = jump_strength
                    spawn_jump_particles(player_x, player_y, skins[current_skin]["jump_color"])
                elif game_state == "playing" and not game_over and not show_game_over_ui:
                    player_velocity = jump_strength
                    spawn_jump_particles(player_x, player_y, skins[current_skin]["jump_color"])
            if event.key == pygame.K_r and show_game_over_ui:
                score = 0
                player_x = screen_width // 2 - 30
                player_y = screen_height // 2
                base_player_y = player_y
                player_direction = 1
                player_velocity = 0
                left_spikes = []
                right_spikes = []
                coins.clear()
                coin_spawn_ready = False
                coin_spawn_side = None
                bubble = None
                bubble_active = False
                game_over = False
                show_game_over_ui = False
                game_state = "start"
                start_animation_time = 0

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if game_state == "start":
                game_state = "playing"
                player_velocity = jump_strength
                spawn_jump_particles(player_x, player_y, skins[current_skin]["jump_color"])

    if game_state == "start":
        player_y = base_player_y + math.sin(start_animation_time * 4) * 15
        player_color = (175, 0, 0)
        sprite = skins[current_skin]["sprites"]["right"]

    elif game_state == "playing":
        if not game_over:
            player_color = (175, 0, 0)
            player_velocity += gravity
            player_y += player_velocity
            player_x += player_direction * player_speed

            if player_y < spike_height or player_y + player_height > screen_height - spike_height - 30:
                is_top = player_y < spike_height 
                if is_top:
                    player_y = spike_height
                else:
                    player_y = screen_height - spike_height - 30 - player_height

                current_time = pygame.time.get_ticks()

                if current_time >= invincible_until:
                    if bubble_active:
                        bubble_active = False
                        bubble = None
                        spawn_death_particles(player_x, player_y, (200, 200, 255))  
                        invincible_until = current_time + 150 
                        if is_top:
                            player_velocity = bubble_bounce_top
                        else:
                            player_velocity = bubble_bounce_bottom
                    else:
                        game_over = True
                        coins.clear()
                        bubble = None
                        bubble_active = False
                        game_over_start_time = current_time
                        spawn_death_particles(player_x, player_y, (0, 0, 0)) 
                        if is_top:
                            player_velocity = death_bounce_top
                        else:
                            player_velocity = death_bounce_bottom

                else:
                    if player_y < spike_height:
                        player_velocity = -2
                    elif player_y + player_height > screen_height - spike_height - 30:
                        player_velocity = 2

            check_coin_collision()
            check_bubble_collision()

            if player_x <= 0:
                player_direction = 1
                score += 1
                for s in left_spikes:
                    s["retracting"] = True
                right_spikes = create_spikes_with_gap(min(4 + score // 10, 7))
                spawn_bubble("right")
                if coin_spawn_ready:
                    spawn_coin("right", score)
                    coin_spawn_ready = False
                elif not coins:
                    spawn_coin("right", score)

            elif player_x + player_width >= screen_width:
                player_direction = -1
                score += 1
                for s in right_spikes:
                    s["retracting"] = True
                left_spikes = create_spikes_with_gap(min(4 + score // 10, 7))
                spawn_bubble("left")
                if coin_spawn_ready:
                    spawn_coin("left", score)
                    coin_spawn_ready = False
                elif not coins:
                    spawn_coin("left", score)

            collision_occurred = False
            current_time = pygame.time.get_ticks()

            if current_time >= invincible_until:
                if player_y < spike_height or player_y + player_height > screen_height - spike_height - 30:
                    collision_occurred = True
                elif check_spike_collision(left_spikes, 0, "left") or check_spike_collision(right_spikes, screen_width, "right"):
                    collision_occurred = True

            if collision_occurred:
                if player_x <= 0 or check_spike_collision(left_spikes, 0, "left"):
                    player_direction = 1
                elif player_x + player_width >= screen_width or check_spike_collision(right_spikes, screen_width, "right"):
                    player_direction = -1

                if bubble_active:
                    if bubble_active and (player_x <= 0 or check_spike_collision(left_spikes, 0, "left") or player_x + player_width >= screen_width or check_spike_collision(right_spikes, screen_width, "right")):
                        if player_x <= 0 or check_spike_collision(left_spikes, 0, "left"):
                            for s in left_spikes:
                                s["retracting"] = True
                            right_spikes = create_spikes_with_gap(min(4 + score // 10, 7))
                            score += 1
                            spawn_bubble("right")
                        elif player_x + player_width >= screen_width or check_spike_collision(right_spikes, screen_width, "right"):
                            for s in right_spikes:
                                s["retracting"] = True
                            left_spikes = create_spikes_with_gap(min(4 + score // 10, 7))
                            score += 1
                            spawn_bubble("left")
                        bubble_active = False
                        bubble = None
                        spawn_death_particles(player_x, player_y, (154, 220, 255)) 
                        invincible_until = pygame.time.get_ticks() + 150    
                else:
                    game_over = True
                    coins.clear()
                    bubble = None
                    bubble_active = False
                    game_over_start_time = pygame.time.get_ticks()
                    if player_y < spike_height or player_y + player_height > screen_height - spike_height - 30:
                        spawn_death_particles(player_x, player_y, (0, 0, 0))  
                        player_velocity = death_bounce_top if player_y < spike_height else death_bounce_bottom
                    else:
                        spawn_death_particles(player_x, player_y, (0, 0, 0)) 
                        player_velocity = jump_strength + 0.5

            if score > high_score:
                high_score = score

        else:
            player_color = player_gameover_color
            player_velocity += gravity * 2
            player_y += player_velocity
            player_x += player_direction * player_speed

            elapsed = pygame.time.get_ticks() - game_over_start_time
            if elapsed < 1000:
                for s in left_spikes + right_spikes:
                    s["retracting"] = True
            else:
                show_game_over_ui = True
                save_coins(total_coins)
                save_high_score(high_score)

    screen.blit(background_img, (0, 0))

    if game_state == "start":
        tap_text = "Tap to jump!"
        alpha = 128 + int(math.sin(start_animation_time * 3) * 127)
        text_surface = font_40.render(tap_text, True, (156, 228, 44))
        text_surface.set_alpha(alpha)
        outline_surface = font_40.render(tap_text, True, (0, 0, 0))
        outline_surface.set_alpha(alpha)
        text_x = screen_width // 2 - font_40.size(tap_text)[0] // 2
        text_y = screen_height // 2 - 100
        for dx in (-1, 1):
            for dy in (-1, 1):
                screen.blit(outline_surface, (text_x + dx, text_y + dy))
        screen.blit(text_surface, (text_x, text_y))
        
        screen.blit(apple_img, (screen_width // 2 - 65, screen_height - 165))
        draw_text_with_outline(screen, str(total_coins), font_40, (screen_width // 2 - 20, screen_height - 155), (156, 228, 44), (0, 0, 0))
        draw_text_with_outline(screen, f"BEST SCORE: {high_score}", font_30, (screen_width // 2 - 80, screen_height - 115), (156, 228, 44), (0, 0, 0))
        screen.blit(spike_up_img, (-20, -180))
        screen.blit(spike_down_img, (-25, screen_height - spike_height - 45))

    elif game_state == "playing" and not game_over:
        score_text = str(score)
        text_surface = score_font.render(score_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(screen_width // 2, screen_height // 2))
        draw_score_text(screen, score_text, score_font, (text_rect.x, text_rect.y), (22, 145, 0), (0, 25, 0))

    if player_y < screen_height:
        if not game_over:
            if player_direction == 1:
                sprite = skins[current_skin]["sprites"]["right"]
            else:
                sprite = skins[current_skin]["sprites"]["left"]
        else:
            if player_direction == 1:
                sprite = skins[current_skin]["sprites"]["right_dead"]
            else:
                sprite = skins[current_skin]["sprites"]["left_dead"]
        screen.blit(sprite, (player_x, int(player_y)))

    if game_state == "playing":
        pygame.draw.rect(screen, (1, 100, 1), (0, 0, screen_width, spike_height - 10))
        pygame.draw.rect(screen, (1, 100, 1), (0, screen_height - spike_height - 15, screen_width, spike_height + 20))
        screen.blit(spike_up_img, (-20, -180))
        screen.blit(spike_down_img, (-25, screen_height - spike_height - 45))
        draw_spikes(left_spikes, 0, "left")
        draw_spikes(right_spikes, screen_width, "right")
        draw_coins()
        draw_bubble()
        draw_floating_texts()

    if show_game_over_ui:
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        font_40_bold = pygame.font.SysFont("Comic Sans MS", 40, bold=True)
        # GAME OVER
        go_text = font_40_bold.render("GAME OVER", True, (255, 50, 50))
        go_rect = go_text.get_rect(center=(screen_width // 2, screen_height // 2 - 60))
        screen.blit(go_text, go_rect)

        # SKOR
        score_surface = pygame.font.SysFont("Comic Sans MS", 35, bold=True).render(f"Score: {score}", True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(screen_width // 2, screen_height // 2 - 10))
        screen.blit(score_surface, score_rect)

        # REPLAY
        replay_text = pygame.font.SysFont("Comic Sans MS", 30).render("Press R to Replay", True, (255, 255, 255))
        replay_rect = replay_text.get_rect(center=(screen_width // 2, screen_height // 2 + 40))
        screen.blit(replay_text, replay_rect)

        screen.blit(apple_img, (screen_width // 2 - 65, screen_height - 165))
        draw_text_with_outline(screen, str(total_coins), font_40, (screen_width // 2 - 20, screen_height - 155), (156, 228, 44), (0, 0, 0))

    draw_particles(screen)
    pygame.display.flip()

pygame.quit()