import serial
import time

PORT = "COM4"  # CHANGE THIS to your Arduino port
BAUD_RATE = 115200

arduino = serial.Serial(PORT, BAUD_RATE, timeout=1)

time.sleep(2)

print("Connected to Arduino!")
print("Move the joysticks...")
print("Press Ctrl+C to stop.\n")

try:
    while True:
        line = arduino.readline().decode("utf-8", errors="ignore").strip()

        if line:
            print(line)

except KeyboardInterrupt:
    print("\nStopped.")

finally:
    arduino.close()