import sys
import uselect
from time import sleep

poll = uselect.poll()
poll.register(sys.stdin, uselect.POLLIN)

while True:
    # Solange kein pong kommt, immer wieder ping senden
    while True:
        print("ping")

        # Kurz auf Antwort warten
        events = poll.poll(500)

        if events:
            response = sys.stdin.readline().strip()

            if response == "pong":
                print("pong empfangen!")
                break

        sleep(0.1)

    # Nach erfolgreichem pong 3 Sekunden warten
    sleep(3)