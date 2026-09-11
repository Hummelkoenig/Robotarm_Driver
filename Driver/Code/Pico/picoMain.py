from machine import Pin, PWM
import time
import sys
import uselect

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

ena = Pin(ENA, Pin.OUT)

motor_dir = [
    Pin(M1DIR, Pin.OUT), Pin(M2DIR, Pin.OUT),
    Pin(M3DIR, Pin.OUT), Pin(M4DIR, Pin.OUT),
    Pin(M5DIR, Pin.OUT), Pin(M6DIR, Pin.OUT),
]

motor_pul = [
    Pin(M1PUL, Pin.OUT), Pin(M2PUL, Pin.OUT),
    Pin(M3PUL, Pin.OUT), Pin(M4PUL, Pin.OUT),
    Pin(M5PUL, Pin.OUT), Pin(M6PUL, Pin.OUT),
]

limit_switch = [
    Pin(LIMIT1, Pin.IN, Pin.PULL_DOWN),
    Pin(LIMIT2, Pin.IN, Pin.PULL_DOWN),
    Pin(LIMIT3, Pin.IN, Pin.PULL_DOWN),
    Pin(LIMIT4, Pin.IN, Pin.PULL_DOWN),
    Pin(LIMIT5, Pin.IN, Pin.PULL_DOWN),
    Pin(LIMIT6, Pin.IN, Pin.PULL_DOWN),
    Pin(LIMIT7, Pin.IN, Pin.PULL_DOWN),
]

servo_pwm = [PWM(Pin(SERVO1)), PWM(Pin(SERVO2)), PWM(Pin(SERVO3))]

for servo in servo_pwm:
    servo.freq(50)

ena.value(0)

for pin in motor_dir:
    pin.value(0)

for pin in motor_pul:
    pin.value(0)

# =========================
# Motor control
# =========================

# Each motor has its own state.
# Therefore all 6 motors can move at the same time.
motor_steps = [0, 0, 0, 0, 0, 0]
motor_speed = [0, 0, 0, 0, 0, 0]
motor_running = [False, False, False, False, False, False]
motor_pulse_high = [False, False, False, False, False, False]
motor_next_step = [0, 0, 0, 0, 0, 0]


def start_motor(motor, direction, steps, speed):
    if motor < 1 or motor > 6:
        print("Error: motor must be between 1 and 6")
        return

    if steps < 0 or speed <= 0:
        print("Error: steps >= 0 and speed > 0 required")
        return

    index = motor - 1
    motor_dir[index].value(1 if direction else 0)
    motor_steps[index] = steps
    motor_speed[index] = speed
    motor_pulse_high[index] = False

    if steps == 0:
        motor_running[index] = False
        return

    motor_running[index] = True
    motor_next_step[index] = time.ticks_us()
    print("MOTOR {} STARTED".format(motor))


def stop_motor(motor):
    if motor < 1 or motor > 6:
        print("Error: motor must be between 1 and 6")
        return

    index = motor - 1
    motor_running[index] = False
    motor_steps[index] = 0
    motor_pulse_high[index] = False
    motor_pul[index].value(0)
    print("MOTOR {} STOPPED".format(motor))


def update_motors():
    # Non-blocking motor update.
    # No sleep() is used here, so USB commands can still be received.
    now = time.ticks_us()

    for index in range(6):
        if not motor_running[index]:
            continue

        if time.ticks_diff(now, motor_next_step[index]) < 0:
            continue

        if not motor_pulse_high[index]:
            motor_pul[index].value(1)
            motor_pulse_high[index] = True
        else:
            motor_pul[index].value(0)
            motor_pulse_high[index] = False
            motor_steps[index] -= 1

            if motor_steps[index] <= 0:
                motor_running[index] = False
                continue

        motor_next_step[index] = time.ticks_add(now, motor_speed[index])

# =========================
# Servo control
# =========================

def angle_to_pulse(angle):
    return 500 + (angle * 1900 // 180)


def servo_control(servo, angle):
    if servo < 1 or servo > 3:
        print("Error: servo must be between 1 and 3")
        return

    if angle < 0 or angle > 180:
        print("Error: angle must be between 0 and 180")
        return

    pulse_us = angle_to_pulse(angle)
    duty = pulse_us * 65535 // 20000
    servo_pwm[servo - 1].duty_u16(duty)
    print("SERVO {} SET {}".format(servo, angle))

# =========================
# Limit switch status
# =========================

def limit_switch_status(switch_number):
    if switch_number < 1 or switch_number > 7:
        print("Error: limit switch must be between 1 and 7")
        return

    status = limit_switch[switch_number - 1].value()
    print("LIMIT {} {}".format(switch_number, status))

# =========================
# Command processing
# =========================

def process_command(command):
    command = command.strip()

    if not command:
        return

    try:
        if command.upper() == "PING":
            print("PONG")

        elif command.startswith("MOVE "):
            parts = command.split()
            if len(parts) == 5:
                start_motor(
                    int(parts[1]), int(parts[2]),
                    int(parts[3]), int(parts[4])
                )
            else:
                print("Error: MOVE motor direction steps speed")

        elif command.startswith("STOP"):
            parts = command.split()
            if len(parts) == 2:
                stop_motor(int(parts[1]))
            else:
                print("Error: STOP motor")

        elif command.startswith("SERVO "):
            parts = command.split()
            if len(parts) == 3:
                servo_control(int(parts[1]), int(parts[2]))
            else:
                print("Error: SERVO servo angle")

        elif command.startswith("LIMIT "):
            parts = command.split()
            if len(parts) == 2:
                limit_switch_status(int(parts[1]))
            else:
                print("Error: LIMIT switch")

        elif command.startswith("HOME"):
            print("Error: Homing sequence not implemented")

        else:
            print("Unknown command: {}".format(command))

    except ValueError:
        print("Error: invalid number in command")

# =========================
# USB input
# =========================

# poll() checks USB without blocking motor control.
poll = uselect.poll()
poll.register(sys.stdin, uselect.POLLIN)

print("Pico online. Awaiting commands...")

while True:
    # Keep all motors running independently.
    update_motors()

    # Read USB commands whenever data is available.
    for event in poll.poll(0):
        try:
            command = sys.stdin.readline()
            process_command(command)
        except Exception as error:
            print("Error: {}".format(error))
