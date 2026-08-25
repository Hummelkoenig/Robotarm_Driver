import serial


def setup():
    ser = serial.Serial('COM3', 9600)
