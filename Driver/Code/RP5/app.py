from flask import Flask, render_template, request, jsonify
import serial

app = Flask(__name__)

PORT = "/dev/ttyACM0"  # ls /dev/ttyACM*
BAUDRATE = 115200

ser = serial.Serial(PORT, BAUDRATE, timeout=0.1)

console_messages = []


def console_print(message):
    print(message)
    console_messages.append(message)


@app.route("/")
def home():

    return render_template("index.html")


@app.route("/send", methods=["POST"])
def receiveInputs():

    # Daten von der Webseite holen
    data = request.get_json()

    process_command(data)

    # Antwort an die Webseite
    return "OK"


@app.route("/console")
def console():

    return jsonify(console_messages)


def process_command(data):

    if data["mode"] == "Move":

        motor = data["input1"]
        direction = data["input2"]
        steps = data["input3"]
        speed = data["input4"]

        command = f"MOVE {motor} {direction} {steps} {speed}\n"

        ser.write(command.encode("ascii"))

        console_print("PC: " + command.strip())


    elif data["mode"] == "Stop":

        motor = data["input1"]

        command = f"STOP {motor}\n"

        ser.write(command.encode("ascii"))

        console_print("PC: " + command.strip())


    elif data["mode"] == "Limit":

        switch_number = data["input1"]

        command = f"LIMIT {switch_number}\n"

        ser.write(command.encode("ascii"))

        console_print("PC: " + command.strip())


    elif data["mode"] == "Servo":

        servo = data["input1"]
        angle = data["input2"]

        command = f"SERVO {servo} {angle}\n"

        ser.write(command.encode("ascii"))

        console_print("PC: " + command.strip())


    elif data["mode"] == "Home":

        command = "HOME\n"

        ser.write(command.encode("ascii"))

        console_print("PC: " + command.strip())


    elif data["mode"] == "Ping":

        command = "PING\n"

        ser.write(command.encode("ascii"))

        console_print("PC: " + command.strip())


def check_serial():

    if ser.in_waiting > 0:

        message = ser.readline().decode(
            "utf-8",
            errors="ignore"
        ).strip()

        if message:

            console_print("Pico: " + message)

            if message == "ping":

                ser.write(b"pong\n")

                console_print("PC: pong")


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )