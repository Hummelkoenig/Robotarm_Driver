from machine import Pin, PWM
import time

start = True

ENA = 15

motor_dir = [14, 12, 10, 7, 5, 3]
motor_pul = [13, 11, 9, 6, 4, 2]

home_direction = [0, 0, 0, 0, 0, 0] # Direction for homing each motor (0 or 1)
homed = [False] * 6

motor_running = [False] * 6
motor_steps = [0] * 6
motor_speed = [0] * 6
last_step_time = [0] * 6

LimitSwitches = [22, 21, 20, 19, 18, 17, 16]

switch_status = [0] * 7

servoPins = [8, 1, 0] #Multifunktional pins, mainly used for servo control

ENA = Pin(ENA, Pin.OUT)
ENA.value(0) # 0 = enabled

for motor in motor_dir:
    Pin(motor_dir[motor], Pin.OUT).value(0)
    motor_dir[motor].value(0)

for motor in motor_pul:
    Pin(motor_pul[motor], Pin.OUT).value(0)
    motor_pul[motor].value(0)

for switch in LimitSwitches:
    Pin(LimitSwitches[switch], Pin.IN, Pin.PULL_UP)

servo_pwm = [PWM(Pin(pin)) for pin in servoPins]

for pwm in servo_pwm:
    pwm.freq(50)
    pwm.duty_u16(0)



def motion_control(motor, direction, steps, speed):
    if motor < 0 or motor > 5:
        print("ERROR: Invalid motor number. Please choose a motor between 0 and 5.")
        return
    if direction not in [0, 1]:
        print("ERROR: Invalid direction. Please choose 0 for forward or 1 for backward.")
        return
    if steps < 0:
        print("ERROR: Invalid number of steps. Please choose a positive integer.")
        return
    if speed < 1:
        print("ERROR: Invalid speed. Please choose a positive integer.")
        return

    motor_dir[motor].value(direction)

    motor_steps[motor] = steps
    motor_speed[motor] = speed

    return


def limit_switch_status(switch_number):
    if switch_number < 0 or switch_number > 6:
        print("ERROR: Invalid limit switch number. Please choose a switch between 0 and 6.")
        return

    status = check_limit_switch(switch_number)

    print (f"Limit switch {switch_number} is {status}")
    return status


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


def home_motor(motor):
    speed = 1000
    direction = home_direction[motor]
    motor_dir[motor].value(direction)

    while LimitSwitches[motor].value() == 1:
        motor_pul[motor].value(1)
        time.sleep_us(speed)
        motor_pul[motor].value(0)
        time.sleep_us(speed)
    for i in range(10):  # Move a few steps back to ensure the switch is released
        motor_dir[motor].value(1 - direction)
        time.sleep_us(speed)
        motor_pul[motor].value(0)
        time.sleep_us(speed)

    print(f"Motor {motor} homed.")
    return True


def process_command(command):
    command = command.strip().upper()
    parts = command.split()

    if len(parts) == 0:
        print("ERROR: No command provided.")
        return
    
    elif parts[0] == "MOVE":
        if len(parts) != 5:
            print("ERROR: Invalid MOVE command. Please use: MOVE <motor> <direction> <steps> <speed>")
            return
        try:
            motor = int(parts[1])
            direction = int(parts[2])
            steps = int(parts[3])
            speed = int(parts[4])
        except ValueError:
            print("ERROR: Invalid parameters for MOVE command.")
            return
        return motion_control(motor, direction, steps, speed)

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
        print("Homing all motors...")
        
        for motor in range(6):
            homed[motor] = home_motor(motor)

        if all(homed):
            print("All motors homed.")
        return

    elif parts[0] == "PING":
        print("PONG")
        return

    elif parts[0] == "PONG":
        print("Pico online and connected. Awaiting commands...")
        start = False
        return
    
    else:
        print("ERROR: Unknown command.")
        return


def check_commands():
    try:
        command = input()
        process_command(command)
    except Exception as error:
        print("Error: {}".format(error))


def update_motor(motor):
    if motor_running[motor] == False:
        return
    
    time_now = time.ticks_us()

    if time.ticks_diff(time_now, last_step_time[motor]) < motor_speed[motor]:
        return

    last_step_time[motor] = time_now

    motor_pul[motor].value(1)
    time.sleep_us(2)
    motor_pul[motor].value(0)

    motor_steps[motor] -= 1

    if motor_steps[motor] <= 0:
        motor_running[motor] = False
        print(f"Motor {motor} has completed its movement.")


def check_limit_switch(switch_number):
    switch_status[switch_number] = LimitSwitches[switch_number].value()


#---LOOP-----------------------------

while True:
    if start:
        print("PING")

    check_commands()

    for motor in range(6):
        update_motor(motor)

    for switch_number in range(len(LimitSwitches)):
        check_limit_switch(switch_number)

    for servo_number in range(len(servo_pwm)):
