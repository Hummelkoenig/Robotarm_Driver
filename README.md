# Robotarm Driver

Steuerungselektronik und Software für einen mehrachsigen Roboterarm. Das Projekt verbindet einen **Raspberry Pi 5 (RP5)** mit einem **Raspberry Pi Pico**. Der Pico übernimmt die zeitkritische Ansteuerung der Motoren und Servos, während der RP5 als übergeordnete Steuerung dient.

> **Projektstatus:** Entwicklung

## Überblick

```text
Raspberry Pi 5
      │
      │ USB / Serial
      ▼
Raspberry Pi Pico
      │
      ├── Stepper Driver / Motoren
      ├── Servos
      └── Endschalter + Not-Aus
```

### Aufgabenverteilung

**Raspberry Pi 5**
- Übergeordnete Steuerung
- Kommunikation mit dem Pico über USB-Serial
- Senden von Bewegungs- und Steuerbefehlen
- Zukünftige Berechnung von Bewegungsvektoren und Benutzeroberfläche

**Raspberry Pi Pico**
- Ansteuerung der Motoren
- Ansteuerung der Servos über PWM
- Auswertung der Endschalter
- Homing
- Not-Aus
- Verarbeitung der Befehle vom RP5
- Gleichzeitige Bewegung mehrerer Motoren

## Hardware

- Raspberry Pi 5
- Raspberry Pi Pico
- Stepper-Motor-Treiber
- Bis zu 6 Stepper-Motoren
- Bis zu 3 Servos
- 6 Endschalter
- 1 separater Not-Aus-Eingang

## Pinbelegung Pico

| Funktion | GPIO |
|---|---:|
| Motor 1 DIR | 14 |
| Motor 1 PUL | 13 |
| Motor 2 DIR | 12 |
| Motor 2 PUL | 11 |
| Motor 3 DIR | 10 |
| Motor 3 PUL | 9 |
| Motor 4 DIR | 7 |
| Motor 4 PUL | 6 |
| Motor 5 DIR | 5 |
| Motor 5 PUL | 4 |
| Motor 6 DIR | 3 |
| Motor 6 PUL | 2 |
| Servo 1 | 8 |
| Servo 2 | 1 |
| Servo 3 | 0 |
| Endschalter 1 | 22 |
| Endschalter 2 | 21 |
| Endschalter 3 | 20 |
| Endschalter 4 | 19 |
| Endschalter 5 | 18 |
| Endschalter 6 | 17 |
| Not-Aus | 16 |
| Motor Enable (ENA) | 15 |

Die Endschalter werden mit Pull-Up-Widerständen betrieben:

- `0` = Schalter ausgelöst
- `1` = Schalter nicht ausgelöst

## Software

### Pico

Die Pico-Software befindet sich unter `Driver/Code/Pico/picoMain.py` und ist in **MicroPython** geschrieben.

Die Motorsteuerung arbeitet nicht-blockierend. Jeder Motor besitzt seinen eigenen Bewegungszustand. Dadurch können mehrere Motoren gleichzeitig laufen, während gleichzeitig Befehle, Endschalter und Servos verarbeitet werden.

### RP5

Die Steuerung für den Raspberry Pi 5 befindet sich unter `Driver/Code/RP5/RP5Main.py`.

Sie verwendet Python und `pyserial` für die Kommunikation mit dem Pico.

Installation von `pyserial`:

```bash
python3 -m pip install pyserial
```

Standardmäßig wird `/dev/ttyACM0` mit `115200 Baud` verwendet.

## Kommunikationsprotokoll

Die Kommunikation erfolgt zeilenweise über USB-Serial.

### Motor bewegen

```text
MOVE <motor> <direction> <steps> <step_delay>
```

Beispiel:

```text
MOVE 0 0 1000 1000
```

Parameter:

- `motor`: Motor `0` bis `5`
- `direction`: `0` oder `1`
- `steps`: Anzahl der Schritte
- `step_delay`: Verzögerung zwischen den Schritten in Mikrosekunden

Mehrere Motoren können nacheinander gestartet werden, ohne auf das Ende der vorherigen Bewegung warten zu müssen:

```text
MOVE 0 0 1000 1000
MOVE 1 1 500 1500
MOVE 2 0 2000 800
```

### Motor stoppen

```text
STOP <motor>
```

Beispiel:

```text
STOP 0
```

Dabei wird nur der angegebene Motor gestoppt.

### Servo bewegen

```text
SERVO <servo> <angle>
```

Beispiel:

```text
SERVO 0 90
```

Der Winkel liegt zwischen `0` und `180` Grad.

### Endschalter abfragen

```text
LIMIT <switch_number>
```

Beispiel:

```text
LIMIT 0
```

Es können die Eingänge `0` bis `6` abgefragt werden. Eingang `6` ist der Not-Aus.

### Homing

```text
HOME
```

Beim Homing fahren die Motoren in ihre konfigurierte Home-Richtung, bis der jeweilige Endschalter ausgelöst wird.

### Verbindung testen

```text
PING
```

Der Pico antwortet mit:

```text
PONG
```

## Sicherheit

Der Not-Aus ist an **GPIO 16** angeschlossen.

Wird der Not-Aus ausgelöst:

1. wird `ENA` deaktiviert,
2. werden alle Motorbewegungen gestoppt,
3. werden laufende Homing-Vorgänge beendet,
4. wartet der Pico, bis der Not-Aus wieder freigegeben wird,
5. anschließend werden die Motor-Treiber wieder aktiviert.

Der Not-Aus sollte **hardwareseitig** ausgeführt werden und nicht ausschließlich von der Software abhängen. Die konkrete Sicherheitsbeschaltung muss für die verwendeten Treiber und Motoren entsprechend ausgelegt werden.

## Projektstruktur

```text
Robotarm_Driver/
│
├── Driver/
│   └── Code/
│       ├── Pico/
│       │   ├── picoMain.py
│       │   └── picoMain.cpp
│       │
│       ├── RP5/
│       │   └── RP5Main.py
│       │
│       └── test connection/
│
└── README.md
```

## Aktueller Stand

- [x] Pico-Grundsteuerung
- [x] 6 Motor-Ausgänge
- [x] 3 Servo-Ausgänge
- [x] Endschalter
- [x] Homing
- [x] Not-Aus
- [x] USB-Serial-Kommunikation
- [x] Nicht-blockierende Motorsteuerung auf dem Pico
- [x] Gleichzeitige Bewegung mehrerer Motoren
- [ ] Vollständig nicht-blockierende RP5-Steuerung
- [ ] Definiertes Kommunikationsprotokoll V1.0
- [ ] Bewegungsplanung / Vektorberechnung
- [ ] Benutzeroberfläche
- [ ] Inverse Kinematik

## Ziel des Projekts

Das langfristige Ziel ist eine vollständige Steuerung für den Roboterarm mit einer Trennung zwischen Benutzeroberfläche, Bewegungsberechnung und Hardwaresteuerung. Der Raspberry Pi 5 soll dabei die komplexere Logik übernehmen, während der Pico die zuverlässige und zeitnahe Ansteuerung der Hardware übernimmt.

## Lizenz

Aktuell ist noch keine Lizenz für das Projekt festgelegt.
