import serial

PORT = "COM4"
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