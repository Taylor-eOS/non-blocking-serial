#include <Arduino.h>
#include "NonBlockingSerial.h"

NonBlockingSerial debugStream(Serial, 50);

void setup() {
    Serial.begin(115200);
    while(!Serial);
}

void loop() {
    debugStream.send("System OK");
    delay(1000);
}

