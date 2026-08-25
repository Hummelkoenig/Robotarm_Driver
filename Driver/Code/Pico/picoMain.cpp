#include <stdio.h>
#include "pico/stdlib.h"

const uint ENA = 15;

const uint M1DIR = 14;
const uint M1PUL = 13;

const uint M2DIR = 12;
const uint M2PUL = 11;

const uint M3DIR = 10;
const uint M3PUL = 9;

const uint M4DIR = 7;
const uint M4PUL = 6;

const uint M5DIR = 5;
const uint M5PUL = 4;

const uint M6DIR = 3;
const uint M6PUL = 2;

const uint servoConnector1 = 8;
const uint servoConnector2 = 1;
const uint servoConnector3 = 0;

const uint limitSwitch1 = 22;
const uint limitSwitch2 = 21;
const uint limitSwitch3 = 20;
const uint limitSwitch4 = 19;
const uint limitSwitch5 = 18;
const uint limitSwitch6 = 17;
const uint limitSwitch7 = 16;

void GPIOconfig() {
    gpio_init_all();

    gpio_set_dir(ENA, GPIO_OUT);

    gpio_set_dir(M1DIR, GPIO_OUT);
    gpio_set_dir(M1PUL, GPIO_OUT);
    gpio_set_dir(M2DIR, GPIO_OUT);
    gpio_set_dir(M2PUL, GPIO_OUT);
    gpio_set_dir(M3DIR, GPIO_OUT);
    gpio_set_dir(M3PUL, GPIO_OUT);
    gpio_set_dir(M4DIR, GPIO_OUT);
    gpio_set_dir(M4PUL, GPIO_OUT);
    gpio_set_dir(M5DIR, GPIO_OUT);
    gpio_set_dir(M5PUL, GPIO_OUT);
    gpio_set_dir(M6DIR, GPIO_OUT);
    gpio_set_dir(M6PUL, GPIO_OUT);

    gpio_set_dir(servoConnector1, GPIO_OUT);
    gpio_set_dir(servoConnector2, GPIO_OUT);
    gpio_set_dir(servoConnector3, GPIO_OUT);

    gpio_set_dir(limitSwitch1, GPIO_IN);
    gpio_pull_down(limitSwitch1);
    gpio_set_dir(limitSwitch2, GPIO_IN);
    gpio_pull_down(limitSwitch2);
    gpio_set_dir(limitSwitch3, GPIO_IN);
    gpio_pull_down(limitSwitch3);
    gpio_set_dir(limitSwitch4, GPIO_IN);
    gpio_pull_down(limitSwitch4);
    gpio_set_dir(limitSwitch5, GPIO_IN);
    gpio_pull_down(limitSwitch5);
    gpio_set_dir(limitSwitch6, GPIO_IN);
    gpio_pull_down(limitSwitch6);
    gpio_set_dir(limitSwitch7, GPIO_IN);
    gpio_pull_down(limitSwitch7);

    gpio_put(ENA, 0); // enable all motors initially
    for (int i = 0; i < 6; i++) {
        gpio_put(14 - i * 2, 0); // set all to 0
    }
}

int motionControl(int motor, int direction, int steps, int speed) {
    if (motor == 1) {
        gpio_put(M1DIR, direction);
        for (int i = 0; i < steps; i++) {
            gpio_put(M1PUL, 1);
            sleep_us(speed);
            gpio_put(M1PUL, 0);
            sleep_us(speed);
        }
    }
    else if (motor == 2) {
        gpio_put(M2DIR, direction);
        for (int i = 0; i < steps; i++) {
            gpio_put(M2PUL, 1);
            sleep_us(speed);
            gpio_put(M2PUL, 0);
            sleep_us(speed);
        }
    }
    else if (motor == 3) {
        gpio_put(M3DIR, direction);
        for (int i = 0; i < steps; i++) {
            gpio_put(M3PUL, 1);
            sleep_us(speed);
            gpio_put(M3PUL, 0);
            sleep_us(speed);
        }
    }
    else if (motor == 4) {
        gpio_put(M4DIR, direction);
        for (int i = 0; i < steps; i++) {
            gpio_put(M4PUL, 1);
            sleep_us(speed);
            gpio_put(M4PUL, 0);
            sleep_us(speed);
        }
    }
    else if (motor == 5) {
        gpio_put(M5DIR, direction);
        for (int i = 0; i < steps; i++) {
            gpio_put(M5PUL, 1);
            sleep_us(speed);
            gpio_put(M5PUL, 0);
            sleep_us(speed);
        }
    }
    else if (motor == 6) {
        gpio_put(M6DIR, direction);
        for (int i = 0; i < steps; i++) {
            gpio_put(M6PUL, 1);
            sleep_us(speed);
            gpio_put(M6PUL, 0);
            sleep_us(speed);
        }
    }
    else {
        printf("Invalid motor number. Please choose a motor between 1 and 6.\n");
        return -1;
    }
    return 0;
}

int servoControl(int servo, int angle) {
    if (servo == 1) {
        // ... code to control servo 1
    }
    else {
        printf("Invalid servo number. Please choose a servo between 1 and 3.\n");
        return -1;
    }
    return 0;
}

int limitSwitchStatus(int switchNumber) {
    if (switchNumber == 1) {
        return gpio_get(limitSwitch1);
    }
    else if (switchNumber == 2) {
        return gpio_get(limitSwitch2);
    }
    else if (switchNumber == 3) {
        return gpio_get(limitSwitch3);
    }
    else if (switchNumber == 4) {
        return gpio_get(limitSwitch4);
    }
    else if (switchNumber == 5) {
        return gpio_get(limitSwitch5);
    }
    else if (switchNumber == 6) {
        return gpio_get(limitSwitch6);
    }
    else if (switchNumber == 7) {
        return gpio_get(limitSwitch7);
    }
    else {
        printf("Invalid limit switch number. Please choose a switch between 1 and 7.\n");
        return -1;
    }
}

int main() {
    GPIOconfig();
    
    while (true) {
        
    }
}