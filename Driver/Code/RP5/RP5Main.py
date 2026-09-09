import serial # python3 -m pip install pyserial

PORT = "/dev/ttyACM0" # ls /dev/ttyACM*
BAUDRATE = 115200

with serial.Serial(PORT, BAUDRATE, timeout=1) as ser:
    print(f"Verbunden mit {PORT}")

    while True:
        message = ser.readline().decode("utf-8", errors="ignore").strip()

        if message:
            print(f"Pico: {message}")

            if message == "ping":
                ser.write(b"pong\n")
                print("PC: pong")

        command = input("?: ")
        if command == "help":
            print("help: Zeigt diese Hilfe an")
            print("ping: Sendet einen Ping an die Pico")
        if command == "mode":
            mode = input("mode: (move, stop, servo, limit) ")
            if mode == "move":
                motor = input("motor: ")
                direction = input("direction: ")
                steps = input("steps: ")
                speed = input("speed: ")

                command = f"MOVE {motor} {direction} {steps} {speed}\n"
                ser.write(command.encode("ascii"))
                print("PC: " + command.strip())

            if mode == "stop":
                motor = input("motor: ")

                command = f"STOP {motor}\n"
                ser.write(command.encode("ascii"))
                print("PC: " + command.strip())

            if mode == "servo":
                servo = input("servo: ")
                angle = input("angle: ")

                command = f"SERVO {servo} {angle}\n"
                ser.write(command.encode("ascii"))
                print("PC: " + command.strip())

            if mode == "limit":
                switch_number = input("switch_number: ")

                command = f"LIMIT {switch_number}\n"
                ser.write(command.encode("ascii"))
                print("PC: " + command.strip())