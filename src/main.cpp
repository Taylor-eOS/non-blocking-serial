#include <Arduino.h>
#include "NonBlockingSerial.h"

NonBlockingSerial debugStream(Serial);

void setup() {
    Serial.begin(115200);
}

void loop() {
    uint8_t status[] = "System OK";
    debugStream.sendBytes(status, 9);
    delay(1000);
}

