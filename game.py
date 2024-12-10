import random
import sys
import pygame
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Pirates - Multiplayer")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Clock for controlling the frame rate
clock = pygame.time.Clock()
FPS = 60

# Load assets
space_bg = pygame.image.load("assets/space_bg.jpg")
ship_image = pygame.image.load("assets/ship.png")
chest_image = pygame.image.load("assets/chest.png")
rock_image = pygame.image.load("assets/rock.png")
explosion_image = pygame.image.load("assets/explosion5.png")
laser_image = pygame.Surface((5, 20))
laser_image.fill(RED)

# Scale images
space_bg = pygame.transform.scale(space_bg, (WIDTH, HEIGHT))
ship_image = pygame.transform.scale(ship_image, (75, 75))
chest_image = pygame.transform.scale(chest_image, (50, 50))
rock_image = pygame.transform.scale(rock_image, (75, 75))
explosion_image = pygame.transform.scale(explosion_image, (75, 75))

# Fonts
font = pygame.font.SysFont("comicsans", 30)
big_font = pygame.font.SysFont("comicsans", 50)

# Sound Effects
bg_music = pygame.mixer.Sound("assets/bg_music.wav")
crash_sound = pygame.mixer.Sound("assets/crash_sound.wav")
treasure_sound = pygame.mixer.Sound("assets/treasure_sound.wav")
laser_sound = pygame.mixer.Sound("assets/laser_sound.wav")
powerup_sound = pygame.mixer.Sound("assets/powerup_sound.wav")

# Game variables
ship_speed = 5
laser_speed = 7
shield_duration = 10 * FPS

shield_active = False
shield_timer = 0

power_up_state = {
    "shield": {"points": 75, "prompt": False},
}

# Helper functions
def draw_text(text, x, y, color, font=font):
    label = font.render(text, True, color)
    screen.blit(label, (x, y))

team_presents_bg = pygame.image.load("assets/team_presents_bg.jpg")
enter_mode_bg = pygame.image.load("assets/enter_mode_bg.jpg")

# Scale custom backgrounds
team_presents_bg = pygame.transform.scale(team_presents_bg, (WIDTH, HEIGHT))
enter_mode_bg = pygame.transform.scale(enter_mode_bg, (WIDTH, HEIGHT))

def team_presents_animation():
    """Displays the 'Team Presents' animation with intro music and custom background."""
    # Play introduction music (continuing across screens)
    intro_music = pygame.mixer.Sound("assets/intro_music.mp3")
    intro_music.play(-1)  # Loop the intro music

    # Load and scale the custom background for Team Presents
    team_presents_bg = pygame.image.load("assets/team_presents_bg.jpg")
    team_presents_bg = pygame.transform.scale(team_presents_bg, (WIDTH, HEIGHT))

    # Display Team Presents background
    screen.blit(team_presents_bg, (0, 0))
    draw_text("Our Team Presents", WIDTH // 2 - 150, HEIGHT // 2 - 100, GOLD, font=big_font)

    # Space Pirates logo or title moving in from the side
    title_font = pygame.font.SysFont("comicsans", 100)
    title_text = "Space Pirates"
    title_x = WIDTH  # Start off-screen

    # Animation loop for smoother effect
    for i in range(WIDTH, -300, -8):  # Title moves more slowly
        screen.blit(team_presents_bg, (0, 0))  # Keep the custom background
        draw_text("Our Team Presents", WIDTH // 2 - 150, HEIGHT // 2 - 100, GOLD, font=big_font)
        draw_text(title_text, i, HEIGHT // 2 + 50, BLUE, font=title_font)  # Smooth animation
        pygame.display.flip()
        pygame.time.wait(20)  # Wait for a moment to create the animation effect

    pygame.time.wait(1000)  # Wait before transitioning to the next screen

def main_menu():
    """Displays the main menu to choose player mode with custom background and continuous music."""
    # Load and scale the custom background for the Enter Mode screen
    enter_mode_bg = pygame.image.load("assets/team_presents_bg.jpg")  # Use the same background
    enter_mode_bg = pygame.transform.scale(enter_mode_bg, (WIDTH, HEIGHT))

    screen.blit(enter_mode_bg, (0, 0))  # Use custom background for the mode selection screen
    draw_text("Select Game Mode:", WIDTH // 2 - 150, HEIGHT // 2 - 100, WHITE, font=big_font)
    draw_text("1. Solo", WIDTH // 2 - 50, HEIGHT // 2, WHITE)
    draw_text("2. Duo", WIDTH // 2 - 50, HEIGHT // 2 + 50, WHITE)
    draw_text("3. Quad", WIDTH // 2 - 50, HEIGHT // 2 + 100, WHITE)
    pygame.display.flip()

    mode = None
    while mode is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    mode = 1
                elif event.key == pygame.K_2:
                    mode = 2
                elif event.key == pygame.K_3:
                    mode = 4
    return mode

def draw_shield_effect(ship_rect):
    """Draws a glowing shield effect around the ship."""
    pygame.draw.circle(screen, BLUE, ship_rect.center, 50, 4)

def activate_power_up(power_up_type, score):
    """Activates the specified power-up and adjusts score."""
    global shield_active, shield_timer

    if power_up_type == "shield":
        shield_active = True
        shield_timer = shield_duration
        score -= power_up_state["shield"]["points"]

    powerup_sound.play()
    power_up_state[power_up_type]["prompt"] = False
    return score


def adjust_phase_behavior(remaining_time, obstacles, ship_x, ship_y):
    """Adjusts rock behavior based on the current phase of the game."""
    if remaining_time > 60 * FPS:  # Phase 1: Normal rocks, medium-fast speed (0-30 seconds)
        for obstacle in obstacles:
            obstacle.y += 5  # Medium-fast downward movement
    elif remaining_time > 30 * FPS:  # Phase 2: Rocks targeting the ship (30-60 seconds)
        for obstacle in obstacles:
            obstacle.y += 7  # Faster downward movement
            if random.randint(0, 20) == 0:  # Occasionally target the player's ship
                if obstacle.x < ship_x:
                    obstacle.x += 1  # Move right if the obstacle is to the left
                elif obstacle.x > ship_x:
                    obstacle.x -= 1  # Move left if the obstacle is to the right
    else:  # Phase 3: Rocks from sides and faster rocks (60-90 seconds)
        for obstacle in obstacles:
            obstacle.y += 9  # Very fast downward movement
            obstacle.x += random.randint(-3, 3)  # Rocks now move randomly from the sides

# Modify the run_turn function to handle freezing
def run_turn(players, current_turn, solo_mode=False):
    global shield_active, shield_timer

    ship_x, ship_y = WIDTH // 2, HEIGHT - 100
    obstacles = []
    treasures = []
    lasers = []
    explosions = []
    spawn_timer = 0
    treasure_timer = 0
    shield_active = False
    shield_timer = 0
    score = 0
    running = True
    remaining_time = 90 * FPS

    while running:
        clock.tick(FPS)
        screen.blit(space_bg, (0, 0))

        # Display current player's name
        draw_text(f"Player {current_turn + 1}: {players[current_turn]['name']}'s Turn", 10, 50, WHITE, font=font)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    lasers.append(pygame.Rect(ship_x + 35, ship_y - 20, 5, 20))
                    laser_sound.play()
                if event.key == pygame.K_s and power_up_state["shield"]["prompt"]:  # Shield Power-Up
                    score = activate_power_up("shield", score)

        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and ship_x > 0:
            ship_x -= ship_speed
        if keys[pygame.K_RIGHT] and ship_x < WIDTH - 75:
            ship_x += ship_speed
        if keys[pygame.K_UP] and ship_y > 0:
            ship_y -= ship_speed
        if keys[pygame.K_DOWN] and ship_y < HEIGHT - 75:
            ship_y += ship_speed

        # Spawn rocks
        spawn_timer += 1
        if spawn_timer > 50:  # Rocks spawn every 50 frames
            spawn_timer = 0
            obstacles.append(pygame.Rect(random.randint(0, WIDTH - 75), -75, 75, 75))

        # Spawn treasures
        treasure_timer += 1
        if treasure_timer > FPS * 5:  # Treasures spawn every 5 seconds
            treasure_timer = 0
            treasures.append(pygame.Rect(random.randint(0, WIDTH - 50), -50, 50, 50))

        # Adjust phase behavior (keeping same function)
        adjust_phase_behavior(remaining_time, obstacles, ship_x, ship_y)

        # Move obstacles
        for obstacle in obstacles[:]:
            obstacle.y += 5
            if obstacle.colliderect(pygame.Rect(ship_x, ship_y, 75, 75)):
                if not shield_active:
                    crash_sound.play()
                    running = False
                else:
                    obstacles.remove(obstacle)  # Shield destroys the obstacle
            if obstacle.y > HEIGHT:
                obstacles.remove(obstacle)

        # Move treasures
        for treasure in treasures[:]:
            treasure.y += 3
            if treasure.colliderect(pygame.Rect(ship_x, ship_y, 75, 75)):
                treasures.remove(treasure)
                treasure_sound.play()
                score += 10
            elif treasure.y > HEIGHT:
                treasures.remove(treasure)

        # Move lasers
        for laser in lasers[:]:
            laser.y -= laser_speed
            if laser.y < 0:
                lasers.remove(laser)
            else:
                for obstacle in obstacles[:]:
                    if laser.colliderect(obstacle):
                        explosions.append((obstacle.x, obstacle.y))
                        obstacles.remove(obstacle)
                        lasers.remove(laser)
                        score += 5
                        break

        # Handle explosions
        for explosion in explosions[:]:
            screen.blit(explosion_image, explosion)
            explosions.remove(explosion)

        # Update power-up prompts
        for power, state in power_up_state.items():
            state["prompt"] = score >= state["points"]

        # Handle shield effect
        if shield_active:
            draw_shield_effect(pygame.Rect(ship_x, ship_y, 75, 75))
            shield_timer -= 1
            if shield_timer <= 0:
                shield_active = False

        # Draw elements
        screen.blit(ship_image, (ship_x, ship_y))
        for obstacle in obstacles:
            screen.blit(rock_image, obstacle.topleft)
        for treasure in treasures:
            screen.blit(chest_image, treasure.topleft)
        for laser in lasers:
            screen.blit(laser_image, laser.topleft)
        draw_text(f"Score: {score}", 10, 10, WHITE)
        draw_text(f"Time: {remaining_time // FPS}", WIDTH - 150, 10, WHITE)
        if power_up_state["shield"]["prompt"]:
            draw_text("Press S for Shield!", WIDTH // 2 - 100, 10, GOLD)

        pygame.display.flip()
        remaining_time -= 1
        if remaining_time <= 0:
            running = False

    # Update the player's score
    players[current_turn]['score'] = score
    return players


def get_player_names(player_count):
    """Get player names based on the number of players selected, using continuous music and same background."""
    names = []
    input_box = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 40)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    font = pygame.font.Font(None, 28)  # Font size adjusted for fitting text
    text = ''
    active = False
    player_index = 0

    # Custom background for player name input (same as other screens)
    enter_name_bg = pygame.image.load("assets/team_presents_bg.jpg")  # Same background
    enter_name_bg = pygame.transform.scale(enter_name_bg, (WIDTH, HEIGHT))
    screen.blit(enter_name_bg, (0, 0))  # Use custom background image here

    while player_index < player_count:
        screen.fill(BLACK)

        # Title text for prompt
        draw_text("Enter Player Name:", WIDTH // 2 - 100, HEIGHT // 2 - 120, WHITE, font=big_font)

        # Draw the input box
        pygame.draw.rect(screen, color, input_box, 2)

        # Render the entered text and place it inside the input box, centered
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(input_box.centerx, input_box.centery))  # Centering the text
        screen.blit(text_surface, text_rect)

        # Blit instructions for user to press Enter
        draw_text("Press ENTER to confirm", WIDTH // 2 - 120, HEIGHT // 2 + 20, WHITE)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = True
                else:
                    active = False
                color = color_active if active else color_inactive

            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:  # Confirm the name
                        names.append(text if text else f"Player {player_index + 1}")
                        text = ''  # Reset text after confirming
                        player_index += 1
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]  # Delete last character
                    else:
                        text += event.unicode  # Add typed character

        pygame.time.Clock().tick(FPS)

    return names


def display_leaderboard(players):
    """Displays the leaderboard at the end."""
    players.sort(key=lambda p: p["score"], reverse=True)  # Sort players by score
    screen.fill(BLACK)
    draw_text("LEADERBOARD", WIDTH // 2 - 100, 50, GOLD, font=big_font)

    for i, player in enumerate(players):
        draw_text(f"{i + 1}. {player['name']} - {player['score']} pts", WIDTH // 2 - 200, 150 + i * 40, WHITE)

    pygame.display.flip()
    pygame.time.wait(3000)


# Main game loop
team_presents_animation()

# Show the main menu to select the game mode (Solo, Duo, Quad)
PLAYER_COUNT = main_menu()

# Get player names based on the mode selected
player_names = get_player_names(PLAYER_COUNT)

# Initialize players with their names and scores
players = [{"name": name, "score": 0} for name in player_names]

# Play background music in loop (continuing from the intro)
bg_music.play(-1)  # Play background music in loop

current_turn = 0  # This will track whose turn it is

# Smaller font for the countdown to fit within the screen
countdown_font = pygame.font.SysFont("comicsans", 40)

# Game loop for player turns
while True:
    is_solo = (PLAYER_COUNT == 1)  # Check if it's solo mode

    # Show a 5-second countdown before starting the player's turn
    screen.fill(BLACK)
    draw_text(f"Player {players[current_turn]['name']}'s Turn", WIDTH // 2 - 150, HEIGHT // 2 - 100, WHITE,
              font=big_font)
    draw_text("Get Ready!", WIDTH // 2 - 100, HEIGHT // 2, GOLD, font=big_font)
    pygame.display.flip()

    for i in range(5, 0, -1):
        screen.fill(BLACK)
        countdown_text = f"Turn Starts In {i} Seconds"
        draw_text(countdown_text, WIDTH // 2 - countdown_font.size(countdown_text)[0] // 2, HEIGHT // 2, WHITE,
                  font=countdown_font)
        pygame.display.flip()
        pygame.time.wait(1000)  # Wait 1 second for the countdown

    # Run the current player's turn
    players = run_turn(players, current_turn, solo_mode=is_solo)

    # Update the current_turn to the next player after the turn ends
    current_turn = (current_turn + 1) % len(players)

    # Check if all players have had their turn
    if current_turn == 0:  # All players have completed their turn
        break

# Display the leaderboard after all turns
display_leaderboard(players)

# Quit Pygame
pygame.quit()