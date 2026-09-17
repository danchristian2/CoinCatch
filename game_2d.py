import argparse
import threading

import pygame
import serial


# ============================================================
# GAME SETTINGS
# ============================================================

WIDTH = 900
HEIGHT = 600

PLAYER_SPEED = 260
PLAYER_SIZE = 34
COIN_RADIUS = 12

BACKGROUND = (19, 36, 51)
PLAYER_COLOR = (41, 182, 246)
COIN_COLOR = (255, 213, 79)
TEXT_COLOR = (255, 255, 255)


# ============================================================
# COMMAND LINE
# ============================================================

parser = argparse.ArgumentParser()

parser.add_argument(
    "--port",
    help="Arduino serial port, for example COM4"
)

args = parser.parse_args()


# ============================================================
# ARDUINO CONTROLLER DATA
# ============================================================

# J1_X, J1_Y, J1_SW,
# J2_X, J2_Y, J2_SW

controller = [
    512,
    512,
    0,
    512,
    512,
    0
]

controller_lock = threading.Lock()


# ============================================================
# READ DATA FROM ARDUINO
# ============================================================

def read_controller(port_name):
    """
    Continuously reads the two joystick values
    from the Arduino through USB serial.
    """

    try:
        arduino = serial.Serial(
            port_name,
            115200,
            timeout=1
        )

        print(f"Connected to Arduino on {port_name}")

        while True:

            line = arduino.readline().decode(
                "utf-8",
                errors="ignore"
            ).strip()

            if not line:
                continue

            values = line.split(",")

            # We need exactly 6 values
            if len(values) != 6:
                continue

            try:

                values = [
                    int(value)
                    for value in values
                ]

                # Check joystick 1
                valid_j1 = (
                    0 <= values[0] <= 1023
                    and
                    0 <= values[1] <= 1023
                    and
                    values[2] in (0, 1)
                )

                # Check joystick 2
                valid_j2 = (
                    0 <= values[3] <= 1023
                    and
                    0 <= values[4] <= 1023
                    and
                    values[5] in (0, 1)
                )

                if valid_j1 and valid_j2:

                    with controller_lock:

                        controller[:] = values

            except ValueError:

                continue

    except Exception as error:

        print("Arduino connection error:")
        print(error)


# ============================================================
# START ARDUINO THREAD
# ============================================================

if args.port:

    controller_thread = threading.Thread(
        target=read_controller,
        args=(args.port,),
        daemon=True
    )

    controller_thread.start()


# ============================================================
# JOYSTICK AXIS PROCESSING
# ============================================================

def axis(raw):
    """
    Convert Arduino analog value:

        0    -> -1
        512  ->  0
        1023 -> +1

    A dead zone is used so small joystick
    imperfections do not move the player.
    """

    value = (raw - 512) / 511

    # Joystick is considered centered
    if abs(value) < 0.15:
        return 0

    return value


# ============================================================
# INITIALIZE PYGAME
# ============================================================

pygame.init()

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT)
)

pygame.display.set_caption(
    "Arduino Joystick Coin Challenge"
)

clock = pygame.time.Clock()

font = pygame.font.Font(
    None,
    36
)

big_font = pygame.font.Font(
    None,
    64
)


# ============================================================
# PLAYER
# ============================================================

player = pygame.Vector2(
    WIDTH / 2,
    HEIGHT / 2
)


# ============================================================
# COINS
# ============================================================

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


# ============================================================
# RESET GAME
# ============================================================

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


# ============================================================
# MAIN GAME LOOP
# ============================================================

running = True

while running:

    # Calculate time between frames
    dt = min(
        clock.tick(60) / 1000,
        0.05
    )


    # ========================================================
    # EVENTS
    # ========================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False


    # ========================================================
    # MOVEMENT
    # ========================================================

    movement = pygame.Vector2(
        0,
        0
    )


    # ========================================================
    # ARDUINO MODE
    # ========================================================

    if args.port:

        with controller_lock:

            j1_x = controller[0]
            j1_y = controller[1]
            j1_sw = controller[2]


        # ----------------------------------------
        # JOYSTICK 1 MOVEMENT
        # ----------------------------------------

        movement.x = axis(j1_x)

        movement.y = axis(j1_y)


        # ----------------------------------------
        # RESET BUTTON
        # ----------------------------------------

        if j1_sw == 1:

            reset_game()


    # ========================================================
    # KEYBOARD MODE
    # ========================================================

    else:

        keys = pygame.key.get_pressed()


        movement.x = (
            int(
                keys[pygame.K_RIGHT]
                or
                keys[pygame.K_d]
            )
            -
            int(
                keys[pygame.K_LEFT]
                or
                keys[pygame.K_a]
            )
        )


        movement.y = (
            int(
                keys[pygame.K_DOWN]
                or
                keys[pygame.K_s]
            )
            -
            int(
                keys[pygame.K_UP]
                or
                keys[pygame.K_w]
            )
        )


        # SPACE resets the game

        if keys[pygame.K_SPACE]:

            reset_game()


    # ========================================================
    # NORMALIZE DIAGONAL MOVEMENT
    # ========================================================

    if movement.length_squared() > 1:

        movement = movement.normalize()


    # ========================================================
    # MOVE PLAYER
    # ========================================================

    player += (
        movement
        *
        PLAYER_SPEED
        *
        dt
    )


    # ========================================================
    # KEEP PLAYER INSIDE SCREEN
    # ========================================================

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


    # ========================================================
    # COIN COLLISION
    # ========================================================

    remaining_coins = []

    for coin in coins:

        distance = player.distance_to(
            coin
        )

        collision_distance = (
            PLAYER_SIZE / 2
            +
            COIN_RADIUS
        )

        if distance > collision_distance:

            remaining_coins.append(
                coin
            )


    coins = remaining_coins


    # Calculate score

    collected = (
        len(coin_positions)
        -
        len(coins)
    )


    # ========================================================
    # DRAW BACKGROUND
    # ========================================================

    screen.fill(
        BACKGROUND
    )


    # ========================================================
    # DRAW COINS
    # ========================================================

    for coin in coins:

        pygame.draw.circle(
            screen,
            COIN_COLOR,
            coin,
            COIN_RADIUS
        )


    # ========================================================
    # DRAW PLAYER
    # ========================================================

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


    # ========================================================
    # SCORE
    # ========================================================

    score_text = font.render(
        f"Coins: {collected}/5",
        True,
        TEXT_COLOR
    )

    screen.blit(
        score_text,
        (20, 20)
    )


    # ========================================================
    # CONTROLS UI
    # ========================================================

    if args.port:

        controls = (
            "Joystick 1: Move"
            " | Press Joystick: Reset"
        )

    else:

        controls = (
            "WASD / Arrow Keys: Move"
            " | SPACE: Reset"
        )


    controls_text = font.render(
        controls,
        True,
        TEXT_COLOR
    )

    screen.blit(
        controls_text,
        (20, 55)
    )


    # ========================================================
    # WIN SCREEN
    # ========================================================

    if collected == 5:

        win_text = big_font.render(
            "YOU WIN!",
            True,
            COIN_COLOR
        )

        win_rect = win_text.get_rect(
            center=(
                WIDTH / 2,
                HEIGHT / 2
            )
        )

        screen.blit(
            win_text,
            win_rect
        )


        if args.port:

            reset_message = (
                "Press joystick button to play again"
            )

        else:

            reset_message = (
                "Press SPACE to play again"
            )


        reset_text = font.render(
            reset_message,
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


    # ========================================================
    # UPDATE SCREEN
    # ========================================================

    pygame.display.flip()


# ============================================================
# EXIT
# ============================================================

pygame.quit()