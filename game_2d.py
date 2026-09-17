import argparse
import threading
import time

import pygame
import serial


# =========================
# GAME SETTINGS
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
# COMMAND LINE
# =========================

parser = argparse.ArgumentParser()
parser.add_argument("--port", help="Arduino serial port, e.g. COM4")
args = parser.parse_args()


# =========================
# ARDUINO CONTROLLER
# =========================

controller = [512, 512, 0, 512, 512, 0]
controller_lock = threading.Lock()


def read_controller(port_name):
    """Continuously read joystick data from Arduino."""

    try:
        ser = serial.Serial(port_name, 115200, timeout=1)

        print(f"Connected to Arduino on {port_name}")

        while True:
            line = ser.readline().decode(
                "utf-8",
                errors="ignore"
            ).strip()

            if not line:
                continue

            values = line.split(",")

            if len(values) != 6:
                continue

            try:
                values = [int(value) for value in values]

                # Make sure values are valid
                if (
                    0 <= values[0] <= 1023
                    and 0 <= values[1] <= 1023
                    and values[2] in (0, 1)
                    and 0 <= values[3] <= 1023
                    and 0 <= values[4] <= 1023
                    and values[5] in (0, 1)
                ):
                    with controller_lock:
                        controller[:] = values

            except ValueError:
                continue

    except Exception as e:
        print("Arduino connection error:", e)


# Start Arduino reader if a port was provided
if args.port:
    controller_thread = threading.Thread(
        target=read_controller,
        args=(args.port,),
        daemon=True
    )

    controller_thread.start()


# =========================
# JOYSTICK AXIS
# =========================

def axis(raw):
    """Convert Arduino analog value 0-1023 into -1 to +1."""

    value = (raw - 512) / 511

    # Dead zone prevents small joystick drift
    if abs(value) < 0.12:
        return 0

    return value


# =========================
# PYGAME
# =========================

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arduino Joystick Coin Challenge")

clock = pygame.time.Clock()

font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 64)


# =========================
# PLAYER AND COINS
# =========================

player = pygame.Vector2(
    WIDTH / 2,
    HEIGHT / 2
)

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
# MAIN GAME LOOP
# =========================

running = True

while running:

    # Time since last frame
    dt = min(
        clock.tick(60) / 1000,
        0.05
    )

    # =========================
    # EVENTS
    # =========================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False


    # =========================
    # MOVEMENT
    # =========================

    movement = pygame.Vector2(0, 0)

    if args.port:

        # Read Arduino controller
        with controller_lock:
            j1_x = controller[0]
            j1_y = controller[1]
            j1_sw = controller[2]

        # Joystick 1 controls player
        movement.x = axis(j1_x)
        movement.y = axis(j1_y)

        # Joystick button resets game
        if j1_sw == 1:
            reset_game()

    else:

        # Keyboard controls
        keys = pygame.key.get_pressed()

        movement.x = (
            int(keys[pygame.K_RIGHT] or keys[pygame.K_d])
            -
            int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        )

        movement.y = (
            int(keys[pygame.K_DOWN] or keys[pygame.K_s])
            -
            int(keys[pygame.K_UP] or keys[pygame.K_w])
        )

        if keys[pygame.K_SPACE]:
            reset_game()


    # Prevent diagonal movement from being faster
    if movement.length_squared() > 1:
        movement = movement.normalize()


    # Move player
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
    # COIN COLLISION
    # =========================

    coins = [
        coin
        for coin in coins
        if player.distance_to(coin)
        > PLAYER_SIZE / 2 + COIN_RADIUS
    ]

    collected = len(coin_positions) - len(coins)


    # =========================
    # DRAW
    # =========================

    screen.fill(BACKGROUND)


    # Draw coins
    for coin in coins:
        pygame.draw.circle(
            screen,
            COIN_COLOR,
            coin,
            COIN_RADIUS
        )


    # Draw player
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


    # Score
    score_text = font.render(
        f"Coins: {collected}/5",
        True,
        TEXT_COLOR
    )

    screen.blit(
        score_text,
        (20, 20)
    )


    # Controls
    if args.port:
        controls = "Joystick 1: Move | Press joystick: Reset"
    else:
        controls = "WASD / Arrow Keys: Move | SPACE: Reset"

    controls_text = font.render(
        controls,
        True,
        TEXT_COLOR
    )

    screen.blit(
        controls_text,
        (20, 55)
    )


    # Win message
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
            "Press joystick button to play again",
            True,
            TEXT_COLOR
        )

        reset_rect = reset_text.get_rect(
            center=(
                WIDTH / 2,
                HEIGHT / 2 + 60
            )
        )

        screen.blit(
            reset_text,
            reset_rect
        )


    pygame.display.flip()


pygame.quit()