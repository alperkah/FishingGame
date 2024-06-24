import pygame
import random

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

# fishing line
fishing_line = {
    "x": boat.centerx,
    "y": boat.bottom,
    "length": 0,
    "max_length": HEIGHT - WATER_LEVEL - 20,
    "speed": 5
}

# Fishes
fishes = []
fish_types = [
    {"color": (0, 255, 0), "points": 10, "speed": 2, "dangerous": False},
    {"color": (0, 0, 255), "points": 20, "speed": 3, "dangerous": False},
    {"color": (255, 255, 0), "points": 30, "speed": 4, "dangerous": False},
    {"color": (255, 0, 0), "points": -10, "speed": 5, "dangerous": True}
]

# Game variables
score = 0
lives = 3
font = pygame.font.Font(None, 36)
game_over = False

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

def draw_lives():
    for i in range(lives):
        pygame.draw.rect(screen, RED, (WIDTH - 30 * (i + 1), 10, 20, 20))

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
                fishes.clear()
                game_over = False

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
        if random.randint(1, 60) == 1:  # Her saniye 1/60 olasılık
            create_fish()

        # Move fishes and catch colntrol
        for fish in fishes[:]:
            fish["rect"].x += fish["type"]["speed"] * fish["direction"]

            if fish["rect"].right < 0 or fish["rect"].left > WIDTH:
                fishes.remove(fish)
            elif (fishing_line["x"] > fish["rect"].left and
                  fishing_line["x"] < fish["rect"].right and
                  fishing_line["y"] + fishing_line["length"] > fish["rect"].top and
                  fishing_line["y"] + fishing_line["length"] < fish["rect"].bottom):
                if fish["type"]["dangerous"]:
                    lives -= 1
                    fishing_line["length"] = 0  # Fishing line cracked
                    if lives <= 0:
                        game_over = True
                else:
                    score += fish["type"]["points"]
                fishes.remove(fish)

    # Draw the scene
    screen.fill(LIGHT_BLUE)
    pygame.draw.rect(screen, BLUE, (0, WATER_LEVEL, WIDTH, HEIGHT - WATER_LEVEL))
    pygame.draw.rect(screen, BROWN, boat)
    pygame.draw.line(screen, BLACK, (fishing_line["x"], fishing_line["y"]),
                     (fishing_line["x"], fishing_line["y"] + fishing_line["length"]))

    for fish in fishes:
        pygame.draw.rect(screen, fish["type"]["color"], fish["rect"])

    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))
    draw_lives()

    if game_over:
        game_over_text = font.render("Game Over! Press space button to restart", True, RED)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()