import pygame
import random
import os
import time

# Pygame start
pygame.init()

# Screen sizes
WIDTH = 800
HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLUE = (65, 105, 225)
LIGHT_BLUE = (135, 206, 235)
BROWN = (139, 69, 19)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
GOLD = (255, 215, 0)

# Game screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fishing")

# Clock
clock = pygame.time.Clock()

# Water level
WATER_LEVEL = HEIGHT // 3

# Boat
boat = pygame.Rect(WIDTH // 2 - 20, WATER_LEVEL - 20, 40, 20)
boat_speed = 5
base_boat_speed = boat_speed

# Fishing line
fishing_line = {
    "x": boat.centerx,
    "y": boat.bottom,
    "length": 0,
    "max_length": HEIGHT - WATER_LEVEL - 20,
    "speed": 5,
    "base_speed": 5
}

# Fishes
fishes = []
fish_types = [
    {"color": GREEN, "points": 10, "speed": 2, "dangerous": False},
    {"color": BLUE, "points": 20, "speed": 3, "dangerous": False},
    {"color": YELLOW, "points": 30, "speed": 4, "dangerous": False},
    {"color": RED, "points": -10, "speed": 5, "dangerous": True},
    {"color": PURPLE, "points": 50, "speed": 6, "dangerous": False}
]

# Bonuses
bonuses = []
bonus_types = [
    {"color": GOLD, "effect": "extra_points", "points": 100},
    {"color": (0, 255, 0), "effect": "extra_life"},
    {"color": (0, 0, 255), "effect": "increase_boat_speed"},
    {"color": (255, 165, 0), "effect": "increase_line_speed"}
]
bonus_duration = 20 * 60  # 20 seconds at 60 FPS
bonus_spawn_rate = 600  # 10 seconds

# Game variables
score = 0
lives = 3
level = 1
font = pygame.font.Font(None, 36)
game_over = False
difficulty_timer = 0
fish_spawn_rate = 60
last_fish_caught_time = time.time()
bonus_effects = {
    "increase_boat_speed": 0,
    "increase_line_speed": 0
}
fishless_counter = 15 * 60  # 15 seconds countdown at 60 FPS
best_score = 0

# Load best score from file
best_score_file = "best_score.txt"
if os.path.exists(best_score_file):
    with open(best_score_file, "r") as f:
        best_score = int(f.read().strip())

# Sound effects
try:
    catch_sound = pygame.mixer.Sound('catch.wav')
    lose_life_sound = pygame.mixer.Sound('lose_life.wav')
    game_over_sound = pygame.mixer.Sound('game_over.wav')
    bonus_sound = pygame.mixer.Sound('bonus.wav')
    pygame.mixer.music.load('background_music.mp3')
    pygame.mixer.music.play(-1)  # Loop background music
except pygame.error as e:
    print(f"Sound loading error: {e}")

def create_fish():
    fish_type = random.choice(fish_types)
    x_pos = random.choice([-20, WIDTH + 20])
    direction = 1 if x_pos < 0 else -1
    fish = {
        "rect": pygame.Rect(
            x_pos,
            random.randint(WATER_LEVEL + 20, HEIGHT - 20),
            20,
            10
        ),
        "type": fish_type,
        "direction": direction
    }
    fishes.append(fish)

def create_bonus():
    bonus_type = random.choice(bonus_types)
    bonus = {
        "rect": pygame.Rect(
            random.randint(0, WIDTH - 20),
            random.randint(WATER_LEVEL + 20, HEIGHT - 20),
            20,
            20
        ),
        "type": bonus_type,
        "spawn_time": time.time()
    }
    bonuses.append(bonus)

def draw_lives():
    for i in range(lives):
        pygame.draw.rect(screen, RED, (WIDTH - 30 * (i + 1), 10, 20, 20))

def check_level_up():
    global level, fish_spawn_rate
    if score >= level * 200:
        level += 1
        fish_spawn_rate = max(10, fish_spawn_rate - 5)

def apply_bonus_effect(effect):
    global boat_speed, fishing_line
    if effect == "increase_boat_speed":
        boat_speed += 3
        bonus_effects["increase_boat_speed"] = bonus_duration
    elif effect == "increase_line_speed":
        fishing_line["speed"] += 3
        bonus_effects["increase_line_speed"] = bonus_duration

def reset_bonus_effects():
    global boat_speed, fishing_line
    if bonus_effects["increase_boat_speed"] > 0:
        bonus_effects["increase_boat_speed"] -= 1
        if bonus_effects["increase_boat_speed"] == 0:
            boat_speed = base_boat_speed
    if bonus_effects["increase_line_speed"] > 0:
        bonus_effects["increase_line_speed"] -= 1
        if bonus_effects["increase_line_speed"] == 0:
            fishing_line["speed"] = fishing_line["base_speed"]

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_SPACE:
                # Restart the game
                score = 0
                lives = 3
                level = 1
                fishes.clear()
                bonuses.clear()
                game_over = False
                fish_spawn_rate = 60
                last_fish_caught_time = time.time()
                bonus_effects = {
                    "increase_boat_speed": 0,
                    "increase_line_speed": 0
                }
                boat_speed = base_boat_speed
                fishing_line["speed"] = fishing_line["base_speed"]
                pygame.mixer.music.play(-1)  # Restart background music
                # Reset fishless counter when a game restarted
                fishless_counter = 15 * 60

    if not game_over:
        # Button controls
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and boat.left > 0:
            boat.x -= boat_speed
        if keys[pygame.K_RIGHT] and boat.right < WIDTH:
            boat.x += boat_speed
        if keys[pygame.K_DOWN] and fishing_line["length"] < fishing_line["max_length"]:
            fishing_line["length"] += fishing_line["speed"]
        if keys[pygame.K_UP] and fishing_line["length"] > 0:
            fishing_line["length"] -= fishing_line["speed"]

        # Update line position
        fishing_line["x"] = boat.centerx

        # Create new fish
        if random.randint(1, fish_spawn_rate) == 1:
            create_fish()

        # Create new bonus
        if random.randint(1, bonus_spawn_rate) == 1:
            create_bonus()

        # Increase difficulty over time
        difficulty_timer += 1
        if difficulty_timer % 600 == 0:
            fish_spawn_rate = max(10, fish_spawn_rate - 5)

        # Check if player didn't catch a fish for 15 seconds
        if time.time() - last_fish_caught_time > 15:
            lives -= 1
            last_fish_caught_time = time.time()
            try:
                lose_life_sound.play()
            except NameError:
                pass
            if lives <= 0:
                game_over = True
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                try:
                    game_over_sound.play()
                except NameError:
                    pass

        # Move fishes and catch control
        for fish in fishes[:]:
            fish["rect"].x += fish["type"]["speed"] * fish["direction"]

            if fish["rect"].right < 0 or fish["rect"].left > WIDTH:
                fishes.remove(fish)
            elif (fishing_line["x"] > fish["rect"].left and
                  fishing_line["x"] < fish["rect"].right and
                  fishing_line["y"] + fishing_line["length"] > fish["rect"].top and
                  fishing_line["y"] + fishing_line["length"] < fish["rect"].bottom):
                fishless_counter = 15 * 60  # Fishless counter reset
                last_fish_caught_time = time.time()
                
                if fish["type"]["dangerous"]:
                    lives -= 1
                    fishing_line["length"] = 0  # Fishing line cracked
                    try:
                        lose_life_sound.play()
                    except NameError:
                        pass
                    if lives <= 0:
                        game_over = True
                        if pygame.mixer.music.get_busy():
                            pygame.mixer.music.stop()
                        try:
                            game_over_sound.play()
                        except NameError:
                            pass
                else:
                    score += fish["type"]["points"]
                    
                    try:
                        catch_sound.play()
                    except NameError:
                        pass
                fishes.remove(fish)
            elif (fish["type"]["dangerous"] and
                  fishing_line["y"] < fish["rect"].bottom and
                  fishing_line["y"] + fishing_line["length"] > fish["rect"].top and
                  fishing_line["x"] > fish["rect"].left and
                  fishing_line["x"] < fish["rect"].right):
                lives -= 1
                fishing_line["length"] = 0  # Fishing line cracked
                try:
                    lose_life_sound.play()
                except NameError:
                    pass
                if lives <= 0:
                    game_over = True
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.stop()
                    try:
                        game_over_sound.play()
                    except NameError:
                        pass
                fishes.remove(fish)

        # Move and apply bonuses
        for bonus in bonuses[:]:
            if time.time() - bonus["spawn_time"] > 10:  # Bonus disappears after 10 seconds
                bonuses.remove(bonus)
            elif (fishing_line["x"] > bonus["rect"].left and
                  fishing_line["x"] < bonus["rect"].right and
                  fishing_line["y"] + fishing_line["length"] > bonus["rect"].top and
                  fishing_line["y"] + fishing_line["length"] < bonus["rect"].bottom):
                if bonus["type"]["effect"] == "extra_points":
                    score += bonus["type"]["points"]
                elif bonus["type"]["effect"] == "extra_life":
                    lives += 1
                else:
                    apply_bonus_effect(bonus["type"]["effect"])
                bonuses.remove(bonus)
                try:
                    bonus_sound.play()
                except NameError:
                    pass

        # Reset bonus effects after duration
        reset_bonus_effects()

        # Check for level up
        check_level_up()

        # Countdown for fishless time
        fishless_counter -= 1
        if fishless_counter <= 0:
            fishless_counter = 15 * 60  # Reset fishless counter
            lives -= 1
            last_fish_caught_time = time.time()
            try:
                lose_life_sound.play()
            except NameError:
                pass
            if lives <= 0:
                game_over = True
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                try:
                    game_over_sound.play()
                except NameError:
                    pass

        # Update best score
        if score > best_score:
            best_score = score
            with open(best_score_file, "w") as f:
                f.write(str(best_score))

    # Draw the scene
    screen.fill(LIGHT_BLUE)
    pygame.draw.rect(screen, BLUE, (0, WATER_LEVEL, WIDTH, HEIGHT - WATER_LEVEL))
    pygame.draw.rect(screen, BROWN, boat)
    pygame.draw.line(screen, BLACK, (fishing_line["x"], fishing_line["y"]),
                     (fishing_line["x"], fishing_line["y"] + fishing_line["length"]))

    for fish in fishes:
        pygame.draw.rect(screen, fish["type"]["color"], fish["rect"])

    for bonus in bonuses:
        pygame.draw.rect(screen, bonus["type"]["color"], bonus["rect"])

    # Draw score, lives, level, fishless counter, and best score
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))
    draw_lives()

    level_text = font.render(f"Level: {level}", True, BLACK)
    screen.blit(level_text, (WIDTH - level_text.get_width() - 10, 30))

    fishless_text = font.render(f"Fishless: {fishless_counter // 60}", True, BLACK)
    screen.blit(fishless_text, (10, 50))

    best_score_text = font.render(f"Best Score: {best_score}", True, BLACK)
    screen.blit(best_score_text, (10, 90))

    if game_over:
        game_over_text = font.render("Game Over! Press space button to restart", True, RED)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
