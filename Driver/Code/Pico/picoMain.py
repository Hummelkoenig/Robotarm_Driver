from machine import Pin, PWM
import time

# =========================
# Pin configuration
# =========================

ENA = 15

M1DIR = 14
M1PUL = 13

M2DIR = 12
M2PUL = 11

M3DIR = 10
M3PUL = 9

M4DIR = 7
M4PUL = 6

M5DIR = 5
M5PUL = 4

M6DIR = 3
M6PUL = 2

SERVO1 = 8
SERVO2 = 1
SERVO3 = 0

LIMIT1 = 22
LIMIT2 = 21
LIMIT3 = 20
LIMIT4 = 19
LIMIT5 = 18
LIMIT6 = 17
LIMIT7 = 16


# =========================
# GPIO setup
# =========================

# Enable pin
ena = Pin(ENA, Pin.OUT)

# Motor direction and pulse pins
motor_dir = [
    Pin(M1DIR, Pin.OUT),
    Pin(M2DIR, Pin.OUT),
    Pin(M3DIR, Pin.OUT),
    Pin(M4DIR, Pin.OUT),
    Pin(M5DIR, Pin.OUT),
]

motor_pul = [
    Pin(M1PUL, Pin.OUT),
    Pin(M2PUL, Pin.OUT),
    Pin(M3PUL, Pin.OUT),
    Pin(M4PUL, Pin.OUT),
    Pin(M5PUL, Pin.OUT),
    Pin(M6PUL, Pin.OUT),
]

# The original C++ code uses GPIO 14, 12, 10, 7, 5 and 3 for direction.
# Set the missing sixth direction pin explicitly.
motor_dir = [
    Pin(M1DIR, Pin.OUT),
    Pin(M2DIR, Pin.OUT),
    Pin(M3DIR, Pin.OUT),
    Pin(M4DIR, Pin.OUT),
    Pin(M5DIR, Pin.OUT),
    Pin(M6DIR, Pin.OUT),
]

# Limit switches
limit_switch = [
    Pin(LIMIT1, Pin.IN, Pin.PULL_DOWN),
    Pin(LIMIT2, Pin.IN, Pin.PULL_DOWN),
    Pin(LIMIT3, Pin.IN, Pin.PULL_DOWN),
    Pin(LIMIT4, Pin.IN, Pin.PULL_DOWN),
    Pin(LIMIT5, Pin.IN, Pin.PULL_DOWN),
    Pin(LIMIT6, Pin.IN, Pin.PULL_DOWN),
    Pin(LIMIT7, Pin.IN, Pin.PULL_DOWN),
]

# Servo PWM
servo_pwm = [
    PWM(Pin(SERVO1)),
    PWM(Pin(SERVO2)),
    PWM(Pin(SERVO3)),
]

for servo in servo_pwm:
    servo.freq(50)

# Motors are disabled/enabled with the same logic as the C++ code.
# 0 = enabled on the original board.
ena.value(0)

for pin in motor_dir:
    pin.value(0)

for pin in motor_pul:
    pin.value(0)


# =========================
# Motor control
# =========================

def motion_control(motor, direction, steps, speed):
    if motor < 1 or motor > 6:
        print("Invalid motor number. Please choose a motor between 1 and 6.")
        return -1

    if steps < 0 or speed < 0:
        print("Steps and speed must not be negative.")
        return -1

    index = motor - 1
    motor_dir[index].value(direction)

    for i in range(steps):
        motor_pul[index].value(1)
        time.sleep_us(speed)
        motor_pul[index].value(0)
        time.sleep_us(speed)

    return 1


# =========================
# Servo control
# =========================

def angle_to_pulse(angle):
    # Same range as the original C++ code:
    # 0 degrees   = 500 us
    # 180 degrees = 2400 us
    return 500 + (angle * 1900 // 180)


def servo_control(servo, angle):
    if servo < 1 or servo > 3:
        print("Invalid servo number. Please choose a servo between 1 and 3.")
        return -1

    if angle < 0 or angle > 180:
        print("Servo angle must be between 0 and 180 degrees.")
        return -1

    pulse_us = angle_to_pulse(angle)

    # 50 Hz = 20 ms = 20000 us period.
    # duty_u16 uses 0..65535 for the complete PWM period.
    duty = pulse_us * 65535 // 20000

    servo_pwm[servo - 1].duty_u16(duty)

    # Keep the same 1 second wait as the original C++ program.
    time.sleep(1)

    return 0


# =========================
# Limit switch status
# =========================

def limit_switch_status(switch_number):
    if switch_number < 1 or switch_number > 7:
        print("Invalid limit switch number. Please choose a switch between 1 and 7.")
        return -1

    return limit_switch[switch_number - 1].value()


# =========================
# Command processing
# =========================

def process_command(command):
    command = command.strip()

    if command == "PING":
        print("PONG")

    elif command.startswith("MOVE "):
        parts = command.split()

        if len(parts) == 5:
            motor = int(parts[1])
            direction = int(parts[2])
            steps = int(parts[3])
            speed = int(parts[4])

            motion_control(motor, direction, steps, speed)
        else:
            print("Invalid motor command format. Use: MOVE <motor> <direction> <steps> <speed>")

    elif command.startswith("SERVO "):
        parts = command.split()

        if len(parts) == 3:
            servo = int(parts[1])
            angle = int(parts[2])

            servo_control(servo, angle)
        else:
            print("Invalid servo command format. Use: SERVO <servo> <angle>")

    elif command.startswith("LIMIT "):
        parts = command.split()

        if len(parts) == 2:
            switch_number = int(parts[1])
            status = limit_switch_status(switch_number)

            if status >= 0:
                print("LIMIT {} {}".format(switch_number, status))
        else:
            print("Invalid limit command format. Use: LIMIT <switch_number>")

    else:
        print("Unknown command: {}".format(command))


# =========================
# Main loop
# =========================

print("Pico robot arm controller started")

while True:
    try:
        command = input()
        process_command(command)
    except Exception as error:
        print("ERROR: {}".format(error))
