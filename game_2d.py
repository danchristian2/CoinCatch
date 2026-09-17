
import pygame

# =========================
# SETTINGS
# =========================

WIDTH = 900
HEIGHT = 600

PLAYER_SPEED = 260
PLAYER_SIZE = 34
COIN_RADIUS = 12

BACKGROUND = (19, 36, 51)
PLAYER_COLOR = (41, 182, 246)
COIN_COLOR = (255, 213, 79)
TEXT_COLOR = (255, 255, 255)


# =========================
# INITIALIZE PYGAME
# =========================

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Coin Challenge")

clock = pygame.time.Clock()

font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 60)


# =========================
# PLAYER
# =========================

player = pygame.Vector2(
    WIDTH / 2,
    HEIGHT / 2
)


# =========================
# COINS
# =========================

coin_positions = [
    (100, 100),
    (800, 100),
    (100, 500),
    (800, 500),
    (450, 130)
]

coins = [
    pygame.Vector2(position)
    for position in coin_positions
]


# =========================
# RESET GAME
# =========================

def reset_game():

    global coins

    player.update(
        WIDTH / 2,
        HEIGHT / 2
    )

    coins = [
        pygame.Vector2(position)
        for position in coin_positions
    ]


# =========================
# GAME LOOP
# =========================

running = True

while running:

    # Time since previous frame
    dt = min(clock.tick(60) / 1000, 0.05)


    # =========================
    # EVENTS
    # =========================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False


    # =========================
    # KEYBOARD INPUT
    # =========================

    keys = pygame.key.get_pressed()

    movement = pygame.Vector2(

        int(
            keys[pygame.K_RIGHT]
            or keys[pygame.K_d]
        )
        -
        int(
            keys[pygame.K_LEFT]
            or keys[pygame.K_a]
        ),

        int(
            keys[pygame.K_DOWN]
            or keys[pygame.K_s]
        )
        -
        int(
            keys[pygame.K_UP]
            or keys[pygame.K_w]
        )
    )


    # =========================
    # NORMALIZE MOVEMENT
    # =========================

    # Prevent diagonal movement
    # from being faster.

    if movement.length_squared() > 1:

        movement = movement.normalize()


    # =========================
    # MOVE PLAYER
    # =========================

    player += movement * PLAYER_SPEED * dt


    # Keep player inside window

    player.x = max(
        PLAYER_SIZE / 2,
        min(
            WIDTH - PLAYER_SIZE / 2,
            player.x
        )
    )

    player.y = max(
        PLAYER_SIZE / 2,
        min(
            HEIGHT - PLAYER_SIZE / 2,
            player.y
        )
    )


    # =========================
    # RESET WITH SPACE
    # =========================

    if keys[pygame.K_SPACE]:

        reset_game()


    # =========================
    # COIN COLLISION
    # =========================

    coins = [

        coin

        for coin in coins

        if player.distance_to(coin)
        >
        PLAYER_SIZE / 2 + COIN_RADIUS
    ]


    # =========================
    # SCORE
    # =========================

    collected = (
        len(coin_positions)
        - len(coins)
    )


    # =========================
    # DRAW BACKGROUND
    # =========================

    screen.fill(BACKGROUND)


    # =========================
    # DRAW COINS
    # =========================

    for coin in coins:

        pygame.draw.circle(
            screen,
            COIN_COLOR,
            coin,
            COIN_RADIUS
        )


    # =========================
    # DRAW PLAYER
    # =========================

    player_rect = pygame.Rect(
        0,
        0,
        PLAYER_SIZE,
        PLAYER_SIZE
    )

    player_rect.center = player

    pygame.draw.rect(
        screen,
        PLAYER_COLOR,
        player_rect,
        border_radius=6
    )


    # =========================
    # UI
    # =========================

    score_text = font.render(
        f"Coins: {collected}/5",
        True,
        TEXT_COLOR
    )

    screen.blit(
        score_text,
        (20, 20)
    )


    controls_text = font.render(
        "WASD / Arrow Keys: Move",
        True,
        TEXT_COLOR
    )

    screen.blit(
        controls_text,
        (20, 55)
    )


    # =========================
    # WIN MESSAGE
    # =========================

    if collected == 5:

        win_text = big_font.render(
            "YOU WIN!",
            True,
            COIN_COLOR
        )

        win_rect = win_text.get_rect(
            center=(WIDTH / 2, HEIGHT / 2)
        )

        screen.blit(
            win_text,
            win_rect
        )

        reset_text = font.render(
            "Press SPACE to play again",
            True,
            TEXT_COLOR
        )

        reset_rect = reset_text.get_rect(
            center=(WIDTH / 2, HEIGHT / 2 + 60)
        )

        screen.blit(
            reset_text,
            reset_rect
        )


    # =========================
    # UPDATE DISPLAY
    # =========================

    pygame.display.flip()


# =========================
# EXIT
# =========================

pygame.quit()

