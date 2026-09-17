import pygame

pygame.init()
pygame.joystick.init()

print("Searching for controllers...")

count = pygame.joystick.get_count()

if count == 0:
    print("❌ No controller detected.")
else:
    print(f"✅ Found {count} controller(s)")

    for i in range(count):
        controller = pygame.joystick.Joystick(i)
        controller.init()

        print("\nController:", controller.get_name())
        print("Axes:", controller.get_numaxes())
        print("Buttons:", controller.get_numbuttons())
        print("Hats:", controller.get_numhats())

        print("\nMove the controller and press its buttons...")

running = True

while running:
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.JOYAXISMOTION:
            print(
                "AXIS:",
                event.axis,
                "VALUE:",
                round(event.value, 2)
            )

        elif event.type == pygame.JOYBUTTONDOWN:
            print(
                "BUTTON:",
                event.button,
                "PRESSED"
            )

        elif event.type == pygame.JOYBUTTONUP:
            print(
                "BUTTON:",
                event.button,
                "RELEASED"
            )

        elif event.type == pygame.JOYHATMOTION:
            print(
                "HAT:",
                event.value
            )

pygame.quit()