from machine import Pin, PWM
import time
import sys
import uselect


start = True

poll = uselect.poll()
poll.register(sys.stdin, uselect.POLLIN)

ENA = 15
ENA = Pin(ENA, Pin.OUT)
ENA.value(0) # 0 = enabled

motor_dir_pin = [14, 12, 10, 7, 5, 3]
motor_dir_pin = [Pin(pin, Pin.OUT) for pin in motor_dir_pin]
for motor in motor_dir_pin:
    motor.value(0)

motor_pul_pin = [13, 11, 9, 6, 4, 2]
motor_pul_pin = [Pin(pin, Pin.OUT) for pin in motor_pul_pin]
for motor in motor_pul_pin:
    motor.value(0)

motor_running = [False] * 6
motor_move_steps = [0] * 6
motor_step_delay = [0] * 6
last_step_time = [0] * 6
motor_position = [0] * 6

home_direction = [0, 0, 0, 0, 0, 0] # Direction for homing each motor (0 or 1)
homed = [True] * 6

limit_switch_pin = [22, 21, 20, 19, 18, 17, 16]
limit_switch_pin = [Pin(pin, Pin.IN, Pin.PULL_UP) for pin in limit_switch_pin]

switch_status = [0] * 7

servo_pin = [8, 1, 0] #Multifunktional pins, mainly used for servo control
servo_pwm = [PWM(Pin(pin)) for pin in servo_pin]
for pwm in servo_pwm:
    pwm.freq(50)
    pwm.duty_u16(0)

servo_angle = [0] * 3



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
    
    elif parts[0] == "MOVE":
        if len(parts) != 5:
            print("ERROR: Invalid MOVE command. Please use: MOVE <motor> <direction> <steps> <step_delay>")
            return
        try:
            motor = int(parts[1])
            direction = int(parts[2])
            steps = int(parts[3])
            step_delay = int(parts[4])
        except ValueError:
            print("ERROR: Invalid parameters for MOVE command.")
            return
        return motion_control(motor, direction, steps, step_delay)

    elif parts[0] == "STOP":
        if len(parts) != 2:
            print("ERROR: Invalid STOP command. Please use: STOP <motor>")
            return
        try:
            motor = int(parts[1])
        except ValueError:
            print("ERROR: Invalid parameter for STOP command.")
            return
        motion_control(motor, 0, 0, 0)  # Stop the motor
        motor_running[motor] = False
        return 
    
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

    elif parts[0] == "HOME":
        if len(parts) != 1:
            print("ERROR: Invalid HOME command. Please use: HOME")
            return

        # Home all motors
        
        return

    elif parts[0] == "PING":
        print("PONG")
        return
    
    else:
        print("ERROR: Unknown command.")
        return

def motion_control(motor, direction, steps, step_delay):
    if motor < 0 or motor > 5:
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

    motor_dir_pin[motor].value(direction)

    motor_move_steps[motor] = steps
    motor_step_delay[motor] = step_delay
    motor_running[motor] = True

    return

def update_motor(motor):
    if motor_running[motor] == False:
        return
    
    time_now = time.ticks_us()

    if time.ticks_diff(time_now, last_step_time[motor]) < motor_step_delay[motor]:
        return

    last_step_time[motor] = time_now

    motor_pul_pin[motor].value(1)
    time.sleep_us(2)
    motor_pul_pin[motor].value(0)

    motor_move_steps[motor] -= 1
    if motor_dir_pin[motor].value() == 0:
        motor_position[motor] += 1
    else:
        motor_position[motor] -= 1

    if motor_move_steps[motor] <= 0:
        motor_running[motor] = False
        print(f"Motor {motor} has completed its movement.")


def limit_switch_status(switch_number):
    if switch_number < 0 or switch_number > 6:
        print("ERROR: Invalid limit switch number. Please choose a switch between 0 and 6.")
        return

    print (f"Limit switch {switch_number} is {switch_status[switch_number]}")
    return switch_status[switch_number]


def servo_control(servo_number, angle):
    if servo_number < 0 or servo_number > 2:
        print("ERROR: Invalid servo number. Please choose a servo between 0 and 2.")
        return
    if angle < 0 or angle > 180:
        print("ERROR: Invalid angle. Please choose an angle between 0 and 180 degrees.")
        return

    pulse_us = 500 + (angle * 1900 // 180)
    duty = pulse_us * 65535 // 20000
    servo_pwm[servo_number].duty_u16(duty)

    print(f"Servo {servo_number} set to angle {angle} degrees.")
    return




#---LOOP-----------------------------

while start:
    print("PING")
    response = input()
    if response.strip().upper() == "PONG":
        print("Pico online and connected. Awaiting commands...")
        if input("Home all motors? (Y/N): ").strip().upper() == "Y":
            command = "HOME"
        else:
            print("Skipping homing. Motors may not be in a known position.")
        start = False

while True:
    check_commands()

    for motor in range(6):
        update_motor(motor)

    for switch_number in range(len(limit_switch_pin)):
        switch_status[switch_number] = limit_switch_pin[switch_number].value()       
