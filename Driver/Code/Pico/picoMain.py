from machine import Pin, PWM
import time
import sys
import uselect


class Motor:
    def __init__(self, dir_pin, pul_pin, limit_switch):
        self.dir = Pin(dir_pin, Pin.OUT)
        self.pul = Pin(pul_pin, Pin.OUT)
        self.limit_switch = limit_switch

        self.running = False
        self.move_steps = 0
        self.step_delay = 0
        self.last_step_time = 0
        self.position = 0
        self.homing = False

    def update(self):
        # Homing
        if self.homing:
            if self.limit_switch.value() == 0:
                self.running = False
                self.homing = False
                self.position = 0
                print("Motor homed")
                return

        if not self.running:
            return

        time_now = time.ticks_us()

        if time.ticks_diff(time_now, self.last_step_time) < self.step_delay:
            return

        self.last_step_time = time_now

        # Step
        self.pul.value(1)
        time.sleep_us(2)
        self.pul.value(0)

        self.move_steps -= 1

        # Position aktualisieren
        if self.dir.value() == 0:
            self.position += 1
        else:
            self.position -= 1

        # Bewegung fertig
        if self.move_steps <= 0:
            self.running = False

    def home(self, direction):
        self.dir.value(direction)
        self.step_delay = 1000
        self.move_steps = 10000
        self.running = True
        self.homing = True


class Servo:
    def __init__(self, pin):
        self.pwm = PWM(Pin(pin))
        self.pwm.freq(50)
        self.angle = 0

    def set_angle(self, angle):
        if angle < 0 or angle > 180:
            print("ERROR: Invalid angle. Please choose an angle between 0 and 180 degrees.")
            return

        pulse_us = 500 + (angle * 1900 // 180)
        duty = pulse_us * 65535 // 20000

        self.pwm.duty_u16(duty)
        self.angle = angle

        print(f"Servo set to angle {angle} degrees.")


# =========================
# Setup
# =========================

start = True

poll = uselect.poll()
poll.register(sys.stdin, uselect.POLLIN)

ENA = Pin(15, Pin.OUT)
ENA.value(0)  # 0 = enabled

home_direction = [0, 0, 0, 0, 0, 0]


# Limit switches
# 0 = ausgelöst
# 1 = nicht ausgelöst

limit_switch_pin = [
    Pin(22, Pin.IN, Pin.PULL_UP),
    Pin(21, Pin.IN, Pin.PULL_UP),
    Pin(20, Pin.IN, Pin.PULL_UP),
    Pin(19, Pin.IN, Pin.PULL_UP),
    Pin(18, Pin.IN, Pin.PULL_UP),
    Pin(17, Pin.IN, Pin.PULL_UP),
    Pin(16, Pin.IN, Pin.PULL_UP)   # NOT-AUS
]

switch_status = [0] * 7


# Motoren
motors = [
    Motor(14, 13, limit_switch_pin[0]),
    Motor(12, 11, limit_switch_pin[1]),
    Motor(10, 9, limit_switch_pin[2]),
    Motor(7, 6, limit_switch_pin[3]),
    Motor(5, 4, limit_switch_pin[4]),
    Motor(3, 2, limit_switch_pin[5])
]


# Servos
servos = [
    Servo(8),
    Servo(1),
    Servo(0)
]

servo_angle = [0] * 3


# =========================
# Commands
# =========================

def check_commands():
    if poll.poll(0):
        try:
            command = sys.stdin.readline().strip()

            if command:
                process_command(command)

        except Exception as error:
            print(f"Error: {error}")


def process_command(command):
    command = command.strip().upper()
    parts = command.split()

    if len(parts) == 0:
        print("ERROR: No command provided.")
        return

    # =========================
    # MOVE
    # =========================

    elif parts[0] == "MOVE":

        if len(parts) != 5:
            print("ERROR: Invalid MOVE command. Please use: MOVE <motor> <direction> <steps> <step_delay>")
            return

        try:
            motor_number = int(parts[1])
            direction = int(parts[2])
            steps = int(parts[3])
            step_delay = int(parts[4])

        except ValueError:
            print("ERROR: Invalid parameters for MOVE command.")
            return

        return motion_control(
            motor_number,
            direction,
            steps,
            step_delay
        )

    # =========================
    # STOP
    # =========================

    elif parts[0] == "STOP":

        if len(parts) != 2:
            print("ERROR: Invalid STOP command. Please use: STOP <motor>")
            return

        try:
            motor_number = int(parts[1])

        except ValueError:
            print("ERROR: Invalid parameter for STOP command.")
            return

        if motor_number < 0 or motor_number >= len(motors):
            print("ERROR: Invalid motor number. Please choose a motor between 0 and 5.")
            return

        motors[motor_number].running = False
        motors[motor_number].homing = False
        motors[motor_number].move_steps = 0

        print(f"Motor {motor_number} has been stopped.")

        return

    # =========================
    # LIMIT
    # =========================

    elif parts[0] == "LIMIT":

        if len(parts) != 2:
            print("ERROR: Invalid LIMIT command. Please use: LIMIT <switch_number>")
            return

        try:
            switch_number = int(parts[1])

        except ValueError:
            print("ERROR: Invalid parameter for LIMIT command.")
            return

        return limit_switch_status(switch_number)

    # =========================
    # SERVO
    # =========================

    elif parts[0] == "SERVO":

        if len(parts) != 3:
            print("ERROR: Invalid SERVO command. Please use: SERVO <servo_number> <angle>")
            return

        try:
            servo_number = int(parts[1])
            angle = int(parts[2])

        except ValueError:
            print("ERROR: Invalid parameters for SERVO command.")
            return

        return servo_control(servo_number, angle)

    # =========================
    # HOME
    # =========================

    elif parts[0] == "HOME":

        if len(parts) != 1:
            print("ERROR: Invalid HOME command. Please use: HOME")
            return

        for i in range(6):
            motors[i].home(home_direction[i])

        print("Homing started.")

    # =========================
    # PING
    # =========================

    elif parts[0] == "PING":
        print("PONG")
        return

    else:
        print("ERROR: Unknown command.")
        return


# =========================
# Motion control
# =========================

def motion_control(motor_number, direction, steps, step_delay):

    if motor_number < 0 or motor_number >= len(motors):
        print("ERROR: Invalid motor number. Please choose a motor between 0 and 5.")
        return

    if direction not in [0, 1]:
        print("ERROR: Invalid direction. Please choose 0 for forward or 1 for backward.")
        return

    if steps < 0:
        print("ERROR: Invalid number of steps. Please choose a positive integer.")
        return

    if step_delay < 0:
        print("ERROR: Invalid step_delay. Please choose a positive integer.")
        return

    motor_instance = motors[motor_number]

    motor_instance.dir.value(direction)
    motor_instance.move_steps = steps
    motor_instance.step_delay = step_delay
    motor_instance.running = steps > 0

    # Wichtig:
    # Normale Bewegung ist kein Homing
    motor_instance.homing = False


# =========================
# Limit switch
# =========================

def limit_switch_status(switch_number):

    if switch_number < 0 or switch_number > 6:
        print("ERROR: Invalid limit switch number. Please choose a switch between 0 and 6.")
        return

    print(f"Limit switch {switch_number} is {switch_status[switch_number]}")

    return switch_status[switch_number]


# =========================
# Servo control
# =========================

def servo_control(servo_number, angle):

    if servo_number < 0 or servo_number > 2:
        print("ERROR: Invalid servo number. Please choose a servo between 0 and 2.")
        return

    if angle < 0 or angle > 180:
        print("ERROR: Invalid angle. Please choose an angle between 0 and 180 degrees.")
        return

    servos[servo_number].set_angle(angle)


# =========================
# Main loop
# =========================

while start:

    print("PING")

    response = input()

    if response.strip().upper() == "PONG":

        print("Pico online and connected. Awaiting commands...")

        x = input("Should all motors home? (Y/N): ").strip().upper()

        if x == "Y":
            process_command("HOME")
            start = False

        elif x == "N":
            print("Skipping homing. Motors may not be in a known position.")
            start = False


while True:

    # -------------------------
    # Not-Aus
    # -------------------------

    if limit_switch_pin[6].value() == 0:
        ENA.value(1)
        for motor in motors:
            motor.running = False
            motor.homing = False
            motor.move_steps = 0

        print("EMERGENCY STOP!")

        # Warten bis Not-Aus wieder losgelassen wird
        while limit_switch_pin[6].value() == 0:
            time.sleep_ms(10)

        ENA.value(0)


    # -------------------------
    # Commands
    # -------------------------

    check_commands()


    # -------------------------
    # Motoren
    # -------------------------

    for motor_instance in motors:
        motor_instance.update()


    # -------------------------
    # Limit switches aktualisieren
    # -------------------------

    for switch_number in range(len(limit_switch_pin)):
        switch_status[switch_number] = limit_switch_pin[switch_number].value()